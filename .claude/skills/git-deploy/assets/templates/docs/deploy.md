# Deploy — [NOME DO PRODUTO]

> Lido pelas skills `git-deploy` (fluxo git) e `devops` (ambientes, pipeline, operação).
> Campo desconhecido: `PENDENTE`. Nunca colocar valor de segredo aqui — só o NOME e onde está.

## Repositório
- Remoto: [https://github.com/<conta>/<repo>.git] · visibilidade: privado
- Estrutura: [monorepo: `app/` (Expo) + `backend/` (Django) + `docs/`]
- Branches: `develop` → hom · `main` → prod · trabalho `feat|fix/H-xxx-slug` · `hotfix/slug`
- Branch padrão no GitHub: `develop` · protegidas: `main`, `develop` (PR + status `ci`)
- Line endings: LF (`.gitattributes` com `* text=auto eol=lf`)

## Ambientes
| | hom | prod |
|---|---|---|
| Branch | develop | main |
| Projeto EasyPanel | [produto]-hom | [produto]-prod |
| API | https://api.hom.[dominio] | https://api.[dominio] |
| Web | https://app.hom.[dominio] | https://app.[dominio] |
| MinIO | https://minio.hom.[dominio] | https://minio.[dominio] |
| App nativo (EAS channel) | preview | production |
| Aprovação | automático | required reviewers: [ ] |
| OUTBOUND_ALLOWLIST | [e-mails/telefones da equipe] | vazio |

## Serviços (por ambiente)
| Serviço | Imagem | Papel | Health |
|---|---|---|---|
| api | ghcr.io/<org>/<repo>-api:<hom|prod> | ROLE=web, RUN_MIGRATIONS=1 | /health/ready/ |
| worker | mesma da api | ROLE=worker | manage.py worker_health |
| beat | mesma da api (1 réplica) | ROLE=beat | — |
| web | ghcr.io/<org>/<repo>-web:<hom|prod> | API_URL, APP_ENV | /health |
| postgres · redis · minio | templates EasyPanel | — | — |

## Pipeline
- Forma: [workflows da devops (ci/deploy/rollback) | manual pelo painel — PENDENTE adotar pipeline]
- GitHub Environments `hom` e `prod`, mesmos nomes:
  - secrets: EASYPANEL_HOOK_API, EASYPANEL_HOOK_WORKER, EASYPANEL_HOOK_BEAT, EASYPANEL_HOOK_WEB, EXPO_TOKEN
  - vars: API_URL, WEB_URL
- Registry: GHCR (credencial de leitura cadastrada no EasyPanel)

## Dados e recuperação
- Backup prod: [destino off-site] · frequência: diário · retenção: 7d/4s/6m
- RPO: [24 h] · RTO: [4 h] · último restore testado: [data]
- Dados de hom: [seed sintético | cópia anonimizada via script `<nome>`]

## Credenciais de terceiros (inventário, sem valores)
| Nome da env | Serviço | Ambiente | Dono | Expira |
|---|---|---|---|---|
| ASAAS_API_KEY | gateway | hom=sandbox / prod | [ ] | [ ] |

## DNS
| Registro | Aponta para | Ambiente | Serviço |
|---|---|---|---|

## Histórico de decisões
| Data | Decisão | Motivo |
|---|---|---|
