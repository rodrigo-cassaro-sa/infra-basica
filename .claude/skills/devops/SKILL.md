---
name: devops
description: OPS-01 — padrão operacional TRANSVERSAL da software house (backend Django e frontend Expo). Ambientes dev/hom/prod isolados, fluxo de branches develop→hom e main→prod, CI/CD com GitHub Actions, imagens Docker versionadas e promovidas, GHCR, deploy no EasyPanel, migrations e rollback, health checks, smoke test, observabilidade (logs, Sentry, uptime, métricas, alertas), backup e restore, secrets, DNS/HTTPS, capacidade, runbook e incidentes. Use SEMPRE que a tarefa envolver ambiente, homologação, produção, Docker, docker-compose, EasyPanel, pipeline, deploy, promoção, rollback, variável de ambiente, domínio, health check, monitoramento, backup, worker em produção, "o sistema caiu" ou "como coloco no ar" — para backend, frontend web ou app nativo (EAS) — mesmo que o usuário não cite OPS-01 ou devops. Git (commit, branch, PR) é da git-deploy; esta skill define para onde cada branch vai e como.
---

# OPS-01 — devops

Cuida de **como o sistema roda**, nunca da regra de negócio. Vale igual para backend e
frontend; o que muda por stack está em `stacks/`.

```text
CÓDIGO → BUILD → TESTE → ARTEFATO → DEPLOY (hom) → VALIDAÇÃO → PROMOÇÃO (prod) → OBSERVAR → RECUPERAR
```

> SE NÃO PODE SER REPRODUZIDO, OBSERVADO E RECUPERADO, AINDA NÃO ESTÁ PRONTO PARA PRODUÇÃO.

## 1. Mapa das skills

| Assunto | Dono |
|---|---|
| commit, branch, PR, release PR, hotfix, tag | **git-deploy** |
| ambientes, pipeline, imagem, deploy, promoção, rollback, observabilidade, backup | **devops** (esta) |
| como o backend Django vira container | `stacks/backend-django/` |
| como o Expo vira site (web) e binário/update (EAS) | `stacks/frontend-expo/` |
| regra de negócio, migrations seguras, contratos | família BE (`backend-core/references/contratos-entre-skills.md`) |
| testes que o pipeline roda | QA-01 · controles de segurança: SEC-01 · "história pronta": DAH-01 |

## 2. Ambientes e branches (padrão da casa)

| Ambiente | Branch | Onde roda | Deploy | Dados |
|---|---|---|---|---|
| **dev** | `feat/*`, `fix/*` (local) | `docker compose up` na máquina | — | sintéticos (seed) |
| **hom** | `develop` | EasyPanel, projeto `<produto>-hom` | **automático** a cada merge em `develop` | sintéticos/anonimizados, credenciais **sandbox** |
| **prod** | `main` | EasyPanel, projeto `<produto>-prod` | release PR `develop → main` + **aprovação** no GitHub Environment | reais |

- `hotfix/*` sai da `main`, volta para `main` **e** para `develop` (fluxo na git-deploy).
- App nativo: `develop` → EAS channel `preview` (hom) · `main` → channel `production` (prod).
- Nunca compartilhar entre ambientes: banco, Redis, fila, bucket, secret, credencial externa.
- hom **nunca** fala com cliente real: e-mail, WhatsApp e push passam por allowlist (`references/ambientes.md` §4).

## 3. Artefato: build uma vez, promover

Com uma branch por ambiente, o merge `develop → main` cria outro commit — mas o **conteúdo** é o
mesmo. Por isso a imagem é identificada pelo **tree hash do diretório do componente**
(`git rev-parse HEAD:backend`), não pelo SHA do commit:

```text
develop: tree de backend/ = 7f3a… → não existe tree-7f3a… no GHCR → build → push :tree-7f3a :hom → deploy hom
main:    tree de backend/ = 7f3a… → já existe tree-7f3a…            → retag   :prod         → deploy prod
```

- Mesmo artefato testado em hom é o que vai para prod (OPS-01 §17/§47), sem rebuild.
- Hotfix direto na `main` gera tree novo → build na hora (e é o único caso).
- Frontend web também promove a mesma imagem: a URL da API vem de **config em runtime** (`/config.js`), não de `EXPO_PUBLIC_*` embutido. Ver `stacks/frontend-expo/`.
- Tags imutáveis: `tree-<hash>` e `sha-<commit>`. `:hom`/`:prod` são ponteiros móveis que o EasyPanel puxa.

Workflows prontos: `assets/workflows/ci.yml`, `deploy.yml`, `rollback.yml` (`references/fluxo-de-entrega.md`).

## 4. Regras inegociáveis

- Configuração fora do código; `.env` real nunca versionado; `.env.example` sempre atualizado.
- Imagem oficial e versionada, multi-stage, **não-root**, sem segredo em `ARG`/`ENV`.
- Deploy sem SSH/edição manual no servidor como fluxo principal.
- Gate bloqueia deploy: lint, teste crítico, build, migration faltando (`makemigrations --check`), security check.
- **Migration é aplicada primeiro em hom.** Migration destrutiva segue expandir → migrar → contrair.
- Todo deploy termina em **smoke test** que confere a versão (`release`) no `/health` — sem isso não está "no ar".
- Todo serviço relevante tem health check leve (live/ready); nunca chama integração externa.
- Logs estruturados em stdout com `correlation_id`; erros no Sentry com `environment=hom|prod`.
- Postgres e MinIO com volume persistente e **backup off-site com restore testado**.
- Banco, Redis e MinIO sem porta pública. Só web/API têm domínio. HTTPS em hom e prod.
- Beat do Celery: exatamente 1 réplica por ambiente.
- Simplicidade: 1 web + 1 postgres + 1 redis até a medição pedir mais. Prometheus/Grafana/Loki, PgBouncer, réplica, blue/green: só com necessidade registrada como decisão (D-xxx).

## 5. Fluxo ao acionar esta skill

1. Ler `docs/deploy.md` do projeto (template na git-deploy). Não existe → criar.
2. Identificar componentes (api, worker, beat, web, app nativo) e o que a história muda em deploy, migration, worker, fila, storage, secret, DNS, proxy, ambiente, monitoramento, backup, capacidade.
3. Aplicar o stack: `stacks/backend-django/README.md` e/ou `stacks/frontend-expo/README.md`.
4. Ambientes: criar/ajustar projetos `-hom` e `-prod` no EasyPanel (`references/easypanel.md`).
5. Pipeline: copiar/ajustar `assets/workflows/` e os secrets/environments do GitHub.
6. Observabilidade e backup mínimos (`references/observabilidade.md`, `references/backup-e-recuperacao.md`).
7. Rodar `references/checklists.md` (readiness) antes do primeiro deploy em prod.
8. Mudança estrutural (novo serviço, PgBouncer, trocar provider) → registrar decisão no mapa de decisões (DAH); incidente relevante → diário de bordo.

## 6. Observabilidade mínima (todo projeto em prod)

```text
logs JSON · /health live+ready (api) · /health (web) · uptime externo · Sentry (api, worker, web)
backup diário off-site · alerta de 5xx, health falhando, disco > 80%, backlog de fila
```

Madura (quando justificar): métricas Prometheus, dashboards Grafana, logs no Loki, tracing, SLO.

## 7. Anti-padrões

```text
❌ hom e prod no mesmo banco/Redis/bucket          ❌ rebuild diferente para prod sem motivo
❌ deploy em prod sem passar por hom                ❌ EXPO_PUBLIC_API_URL embutido na imagem web
❌ hom mandando WhatsApp/e-mail para cliente real   ❌ cópia de dados de prod em hom sem anonimizar
❌ deploy anunciado sem smoke conferindo release    ❌ migrate em worker/beat ou em toda réplica
❌ :latest como referência de rollback              ❌ backup nunca restaurado
❌ health check chamando provider externo           ❌ alertar por tudo (alert fatigue)
```

## Referências

| Arquivo | Quando ler |
|---|---|
| `references/ambientes.md` | dev/hom/prod, isolamento, config, dados de hom, allowlist de saída |
| `references/fluxo-de-entrega.md` | pipeline, promoção por tree hash, aprovação, smoke, rollback, hotfix, EAS |
| `references/migrations-e-rollback.md` | migration segura por ambiente, backup antes, compatibilidade front/back |
| `references/easypanel.md` | projetos por ambiente, serviços, domínios, recursos |
| `references/observabilidade.md` | logs, Sentry, métricas, alertas, uptime, custos |
| `references/backup-e-recuperacao.md` | RPO/RTO, backup, restore test, DR |
| `references/seguranca-operacional.md` | secrets, rotação, rede, firewall, SSH, certificados |
| `references/runbook.md` | deploy, rollback, incidente, restore, segredo vazado |
| `references/checklists.md` | readiness, ambiente, Docker, banco, Celery, MinIO, deploy, DoD |
| `stacks/backend-django/README.md` | Dockerfile, ROLE web/worker/beat, gunicorn, health, Sentry, cache |
| `stacks/frontend-expo/README.md` | Dockerfile.web + Caddy, config em runtime, health, EAS por ambiente |
| `assets/workflows/*.yml` | CI de PR, deploy hom/prod com promoção, rollback |
| `references/guia-ops-01.md` | guia completo OPS-01 (195 seções) — as citações "OPS-01 §N" apontam para ele |
