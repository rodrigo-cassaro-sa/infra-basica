# Runbook

Copiar para `docs/runbook.md` do projeto (ou para onde a DAH mantém documentação
operacional) e preencher nomes reais. Cada procedimento responde: o que aconteceu, como
verificar, como mitigar, como recuperar.

## Deploy em hom (automático)

1. Merge em `develop` → Actions `deploy` → job do environment `hom`.
2. Smoke verde (api e web com o `release` novo).
3. QA/aceite manual em `app.hom...`: login, fluxo da história, app via channel `preview`.

## Deploy em prod

1. Release PR `develop → main` (git-deploy) com: histórias, migrations, risco, rollback.
2. `migration-risk`? → backup manual antes (ver `migrations-e-rollback.md` §3).
3. Merge → Actions pede aprovação do environment `prod` → aprovar.
4. Smoke verde → Sentry sem erro novo na release por 15 min → uptime ok.
5. App nativo: `eas update --channel production` se houve mudança JS.

## Rollback

1. Actions → `rollback` → ambiente `prod`, componente, tag `tree-<anterior>`.
2. Smoke confirma o release antigo.
3. Migration aplicada não volta: se o código antigo não roda com o schema novo, corrigir
   para frente (hotfix). Por isso migrations são compatíveis (expandir/contrair).
4. `git revert` do que saiu, via PR, para o código acompanhar.

## Hotfix

`hotfix/<assunto>` a partir da `main` → PR para `main` → deploy prod (build novo) →
back-merge `main → develop` (git-deploy).

## Incidente

```text
detectar → conter → restaurar → investigar → corrigir → registrar
```

1. `/health/ready/` da api: qual check falha (database/broker)?
2. Sentry: erro, release, primeira ocorrência. Coincide com deploy? → rollback primeiro, investigar depois.
3. Logs do serviço filtrando pelo `correlation_id` informado pelo usuário.
4. Fila parada: `worker_health`; backlog `redis-cli -n 0 llen default`; beat rodando?
5. Provider externo fora: `TransientError` → tasks em retry; sistema segue (degradação). Avisar cliente se passar do combinado.
6. Disco cheio: logs/backups locais/volume do postgres → liberar, depois alerta de 80%.
7. Restart loop / OOM: ver limite de memória, `CELERY_MAX_TASKS_PER_CHILD`, `GUNICORN_WORKERS`.
8. Registrar no diário de bordo; incidente grave → postmortem (causa, impacto, linha do tempo, ação corretiva). Mudança estrutural → decisão D-xxx.

## Restore

Ver `backup-e-recuperacao.md` §3–4. Sempre restaurar em banco novo, conferir, depois apontar.

## Segredo vazado

1. Revogar/rotacionar no provider imediatamente.
2. Atualizar env no EasyPanel (ambiente afetado) e redeployar os serviços que usam.
3. `DJANGO_SECRET_KEY` trocada invalida sessões do Admin e tokens JWT (todos relogam).
4. Se estava no git: rotacionar é obrigatório (limpar histórico não basta).
