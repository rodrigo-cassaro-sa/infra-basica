# Deploy — [NOME DO PRODUTO]

> Lido pelas skills `git-deploy` (fluxo git) e `devops` (ambientes, pipeline, operação).
> Campo desconhecido: `PENDENTE`. Nunca colocar valor de segredo aqui — só o NOME e onde está.
>
> Documento **operacional**, não DAH. Dono: `git-deploy`, com a `devops`.

## Repositório

- Remoto: [https://github.com/<conta>/<repo>.git] · visibilidade: privado
- Estrutura: monorepo do template `infra-basica` — `backend/` (Django), `frontend/` (Expo), `coder/` (Code Server), `docs/`, `scripts/`
- Branches: `dev` → dev · `hom` → hom · `main` → prod · trabalho `feat|fix/H-xxx-slug` (a partir de `dev`) · `hotfix/slug` (a partir de `main`)
- Promoção: PR `dev → hom` → PR `hom → main` · hotfix com back-merge `main → hom → dev`
- Branch padrão no GitHub: `dev` · protegidas: `main`, `hom` e `dev` (PR obrigatório)
- Este modelo substitui o `develop`/`main` descrito nas skills `git-deploy` e `devops`.
- Line endings: LF

## Ambientes

Um serviço Compose no EasyPanel por branch, todos com o mesmo `docker-compose.yml`.
Cada um sobe Code Server + Django + Expo + PostgreSQL, com rede, volumes e variáveis próprios.
A diferença entre ambientes é só o Ambiente do serviço (modelos: `.env.dev.example`, `.env.hom.example`, `.env.prod.example`).

| | dev | hom | prod |
|---|---|---|---|
| Serviço EasyPanel | `[projeto]-dev` | `[projeto]-hom` | `[projeto]-prod` |
| Branch | `dev` | `hom` | `main` |
| `RUN_MODE` | `dev` (workspace do Code Server) | `server` (checkout de `hom`) | `server` (checkout de `main`) |
| Settings | `config.settings.development` | `config.settings.homologation` | `config.settings.production` |
| API | https://[api-dev-projeto.dominio] | https://[api-hom-projeto.dominio] | https://[api-projeto.dominio] |
| Web | https://[dev-projeto.dominio] | https://[hom-projeto.dominio] | https://[projeto.dominio] |
| Code Server | https://[coder-dev-projeto.dominio] | https://[coder-hom-projeto.dominio] | https://[coder-projeto.dominio] |
| App nativo (EAS profile) | development | preview | production |
| Aprovação | automático | PENDENTE | PENDENTE |

## Serviços (iguais nos três ambientes)

| Serviço | Origem | Porta interna | Health |
|---|---|---|---|
| `django` | build de `backend/`; `RUN_MODE` escolhe runserver ou gunicorn | 8000 | `/api/health/` |
| `expo` | build de `frontend/` (alvo `dev` = Metro, `server` = Nginx) | 8081 | `/healthz` (em `server`) |
| `postgres` | `postgres:17-alpine` | 5432 (sem domínio) | `pg_isready` |
| `code-server` | build de `coder/` | 8080 | `/healthz` |

## Pipeline

- Forma atual: **promoção por branch** — o EasyPanel constrói cada ambiente a partir da branch dele.
- hom: deploy de `[projeto]-hom` após merge do PR `dev → hom` (automático por webhook: PENDENTE decidir).
- prod: PR `hom → main` após "Aprovo publicação" + deploy manual de `[projeto]-prod`.
- PENDENTE: adotar os workflows da `devops` (ci/deploy/rollback com imagem imutável no GHCR).

## Aplicativo

| Alvo | Comando | Situação |
|---|---|---|
| APK Android | `eas build -p android --profile preview` | PENDENTE |
| iOS instalável | `eas build -p ios` | PENDENTE (exige Apple Developer Program) |
| Publicação em loja | `eas submit` | PENDENTE contas de loja |

**Backend sempre antes do app**: versões antigas continuam instaladas por semanas chamando a API.

## Dados e recuperação

- Backup: `make backup` no ambiente (pg_dump para `backups/`) · destino off-site: PENDENTE · frequência: PENDENTE · retenção: PENDENTE
- RPO: PENDENTE · RTO: PENDENTE · último restore testado: PENDENTE
- Dados de hom: PENDENTE (seed sintético ou cópia anonimizada — nunca cópia crua de prod)

## Credenciais de terceiros (inventário, sem valores)

| Nome da env | Serviço | Ambiente | Dono | Expira |
|---|---|---|---|---|
| `GH_TOKEN` | GitHub (Code Server) | dev · hom · prod | [ ] | [ ] |

## DNS

| Registro | Aponta para | Ambiente | Serviço |
|---|---|---|---|
| — | — | — | — |

PostgreSQL não recebe domínio público.

## Histórico de decisões

| Data | Decisão | Motivo |
|---|---|---|
| — | — | — |
