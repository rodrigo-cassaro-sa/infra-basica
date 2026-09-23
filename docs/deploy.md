# Deploy — [NOME DO PRODUTO]

> Lido pelas skills `git-deploy` (fluxo git) e `devops` (ambientes, pipeline, operação).
> Campo desconhecido: `PENDENTE`. Nunca colocar valor de segredo aqui — só o NOME e onde está.
>
> Documento **operacional**, não DAH. Dono: `git-deploy`, com a `devops`.

## Repositório

- Remoto: [https://github.com/<conta>/<repo>.git] · visibilidade: privado
- Estrutura: monorepo do template `infra-basica` — `backend/` (Django), `frontend/` (Expo), `coder/` (Code Server), `docs/`, `scripts/`
- Branches: PENDENTE (ver "Pipeline")
- Line endings: LF

## Ambientes

Um único serviço Compose no EasyPanel (`docker-compose.yml`) com os três ambientes isolados.
Variáveis no Ambiente do EasyPanel, com prefixo `DEV_` / `HOM_` / `PROD_` (modelo em `.env.example`).

| | dev | hom | prod |
|---|---|---|---|
| Código | workspace do Code Server (volume `coder_workspace`) | checkout do EasyPanel | checkout do EasyPanel |
| API | https://[api-dev-projeto.dominio] | https://[api-hom-projeto.dominio] | https://[api-projeto.dominio] |
| Web | https://[dev-projeto.dominio] | https://[hom-projeto.dominio] | https://[projeto.dominio] |
| Code Server | https://[coder-projeto.dominio] | — | — |
| App nativo (EAS profile) | development | preview | production |
| Aprovação | automático | PENDENTE | PENDENTE |

## Serviços por ambiente

| Serviço | Origem | Porta interna | Health |
|---|---|---|---|
| `django-dev` / `django-hom` / `django-prod` | build de `backend/` | 8000 | `/api/health/` |
| `expo-dev` | Metro sobre o workspace | 8081 | — |
| `expo-hom` / `expo-prod` | build de `frontend/` (`Dockerfile.web`) + Nginx | 80 | `/healthz` |
| `postgres-dev` / `postgres-hom` / `postgres-prod` | `postgres:17-alpine` | 5432 (sem domínio) | `pg_isready` |
| `code-server` | build de `coder/` | 8080 | `/healthz` |

## Pipeline

- Forma atual: redeploy do Compose no EasyPanel a partir do repositório.
- PENDENTE: definir a promoção entre hom e prod (branch/ref de cada um).
- PENDENTE: adotar os workflows da `devops` (ci/deploy/rollback) ou manter o redeploy manual.

## Aplicativo

| Alvo | Comando | Situação |
|---|---|---|
| APK Android | `eas build -p android --profile preview` | PENDENTE |
| iOS instalável | `eas build -p ios` | PENDENTE (exige Apple Developer Program) |
| Publicação em loja | `eas submit` | PENDENTE contas de loja |

**Backend sempre antes do app**: versões antigas continuam instaladas por semanas chamando a API.

## Dados e recuperação

- Backup: `make backup-dev|hom|prod` (pg_dump para `backups/`) · destino off-site: PENDENTE · frequência: PENDENTE · retenção: PENDENTE
- RPO: PENDENTE · RTO: PENDENTE · último restore testado: PENDENTE
- Dados de hom: PENDENTE (seed sintético ou cópia anonimizada — nunca cópia crua de prod)

## Credenciais de terceiros (inventário, sem valores)

| Nome da env | Serviço | Ambiente | Dono | Expira |
|---|---|---|---|---|
| `GH_TOKEN` | GitHub (Code Server) | dev | [ ] | [ ] |

## DNS

| Registro | Aponta para | Ambiente | Serviço |
|---|---|---|---|
| — | — | — | — |

PostgreSQL não recebe domínio público.

## Histórico de decisões

| Data | Decisão | Motivo |
|---|---|---|
| — | — | — |
