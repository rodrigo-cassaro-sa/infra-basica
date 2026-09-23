# Ambientes — dev, hom, prod

## 1. Papel de cada um

| | dev | hom | prod |
|---|---|---|---|
| Objetivo | desenvolver | QA, integração, teste de deploy e migration, smoke, aceite do cliente | uso real |
| Onde | máquina (compose) | EasyPanel `<produto>-hom` | EasyPanel `<produto>-prod` |
| Branch | `feat/*`, `fix/*` | `develop` | `main` |
| `APP_ENV` | `dev` | `hom` | `prod` |
| Django settings | `config.settings.local` | `config.settings.production` | `config.settings.production` |
| DEBUG | True | **False** | **False** |
| HTTPS | não | sim | sim |
| Dados | seed sintético | sintético ou anonimizado | reais |
| Credenciais externas | sandbox | **sandbox** | produção |
| Sentry `environment` | — | `hom` | `prod` |
| App nativo (EAS) | development build | channel `preview` | channel `production` |

hom e prod usam **o mesmo settings e a mesma imagem**: o que difere é só a configuração
(envs). hom é "prod com outros dados", por isso pega erro de deploy antes do cliente.

## 2. Isolamento

Cada ambiente tem o próprio: Postgres, Redis (broker e cache), bucket MinIO, secrets,
credenciais de terceiros, domínio, webhook de deploy, DSN/environment do Sentry.
Nada é compartilhado por padrão. Exceção só registrada como decisão.

## 3. Configuração

- Tudo por env. `.env.example` lista todas as variáveis, sem valor sensível.
- Local: `.env` (no `.gitignore`). hom/prod: envs do serviço no EasyPanel.
- Mesma chave, valor diferente por ambiente. Nunca `if APP_ENV == "prod"` espalhado no
  código: o comportamento diferente vem de configuração (`OUTBOUND_ALLOWLIST`, flags).
- Domínios padrão:

```text
prod: api.<produto>.com.br   app.<produto>.com.br   minio.<produto>.com.br
hom:  api.hom.<produto>.com.br app.hom.<produto>.com.br minio.hom.<produto>.com.br
```

Registrar no `docs/deploy.md` domínio, serviço e ambiente (DNS não fica "só na cabeça").

## 4. hom não fala com gente de verdade

hom tem integrações reais em modo sandbox — e é onde mais se esquece disso.

- **Saída de mensagens (e-mail, WhatsApp/Evolution, SMS, push)**: `OUTBOUND_ALLOWLIST`
  com os destinos permitidos (e-mails e telefones da equipe). Fora da lista, o adapter
  (BE-05) registra e **não envia**. Em prod a variável fica vazia = sem restrição.
- Gateway de pagamento: chave **sandbox** sempre.
- Webhooks de provider apontam para `api.hom...` com secret próprio.
- Instância Evolution API de hom separada da de prod (número de teste).

```python
# apps/integrations/base/outbound.py (BE-05)
def outbound_allowed(destination: str) -> bool:
    allow = settings.OUTBOUND_ALLOWLIST  # env: lista separada por vírgula; vazia = tudo liberado (prod)
    return not allow or destination in allow
```

## 5. Dados de hom

- Seed sintético (`manage.py seed_hom`) é o padrão.
- Cópia de prod para hom **só anonimizada** (CPF, nome, telefone, e-mail, endereço,
  dados de saúde) — LGPD. Script de anonimização versionado, nunca manual.
- Backup de prod nunca é restaurado em hom sem passar pela anonimização.

## 6. dev

- `docker compose up` sobe tudo (ver `stacks/backend-django/docker-compose.yml`).
- Bootstrap de novo dev/agente em poucos passos documentados no README do projeto:
  clonar → copiar `.env.example` → `docker compose up` → `migrate` → `seed`.
- Frontend aponta para a API local (`EXPO_PUBLIC_API_URL=http://localhost:8000` em dev).
