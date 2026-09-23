# Migrations e rollback

Regras de código das migrations: `backend-core` §12. Aqui: como elas passam pelos ambientes.

## 1. Caminho

```text
dev (makemigrations + revisão) → CI (migrations check + testes com Postgres)
→ hom (aplicada no deploy; conferir tempo e locks) → prod (mesma migration, mesmo artefato)
```

- Aplicação: `RUN_MIGRATIONS=1` só no serviço `api`; worker/beat nunca migram.
- Migration falhou → container da api não sobe → deploy para (o smoke falha). Nada de
  "sobe sem migration".
- Migration que demorou em hom com dados sintéticos pode demorar **muito mais** em prod:
  avaliar volume real antes da release PR.

## 2. Compatibilidade entre versões

Durante o deploy, versões diferentes convivem (api nova + worker velho; api nova + app
nativo velho por meses). Toda migration precisa funcionar com o código **anterior**:

```text
release 1: adicionar campo nullable / tabela nova / índice CONCURRENTLY
release 2: código escreve nos dois + backfill em task (BE-03)
release 3: tornar obrigatório / remover o antigo
```

Rename e drop de coluna nunca na mesma release que para de usá-la.

## 3. Backup antes

PR com migration marcada como arriscada (label `migration-risk`: drop, alter type, tabela
grande) → antes de aprovar o environment `prod`:

```bash
pg_dump -Fc "$DATABASE_URL" > pre_<release>.dump   # e enviar para o destino off-site
```

## 4. Frontend × backend

- Backend sobe antes do web e do update do app.
- Campo removido da API só depois que nenhuma versão ativa do app o usa (ver
  `backend-api/references/versionamento.md`; app nativo = API pública).
- Feature flag para ligar funcionalidade depois do deploy quando o risco justificar.
