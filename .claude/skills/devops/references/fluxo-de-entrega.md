# Fluxo de entrega — CI/CD, promoção, rollback

## 1. Visão geral

```text
feat/H-023-x ──PR──▶ develop ──(CI verde)──▶ build/reuso ──▶ :hom ──▶ deploy hom ──▶ smoke hom
                                                                                  │ QA / aceite
develop ──release PR──▶ main ──▶ reuso da imagem (tree) ──▶ aprovação ──▶ :prod ──▶ deploy prod ──▶ smoke prod
hotfix/x ──PR──▶ main (build) ──▶ prod   e   main ──back-merge──▶ develop
```

Git (nomes de branch, PR, release PR, back-merge, tag): skill **git-deploy**.

## 2. Workflows (`assets/workflows/`)

| Arquivo | Dispara | Faz |
|---|---|---|
| `ci.yml` | PR para `develop` ou `main` | lint, testes, migrations check, OpenAPI sem diff, build de teste do web |
| `deploy.yml` | push em `develop` (hom) e `main` (prod) | por componente: reusa ou builda imagem, move ponteiro `:hom`/`:prod`, chama webhook do EasyPanel, smoke |
| `rollback.yml` | manual (`workflow_dispatch`) | aponta `:prod` (ou `:hom`) para uma tag `tree-…` anterior e redeploya |

Monorepo padrão: `backend/` e `app/` (Expo). Cada um vira uma imagem:
`ghcr.io/<org>/<repo>-api` e `ghcr.io/<org>/<repo>-web`. Componente sem mudança não rebuilda.

## 3. Promoção por tree hash

```bash
TREE=$(git rev-parse HEAD:backend)        # muda só se algo dentro de backend/ mudou
IMAGE=ghcr.io/org/repo-api
if docker manifest inspect $IMAGE:tree-$TREE >/dev/null 2>&1; then
  echo "reuso"                            # já foi construída (em develop)
else
  docker buildx build --build-arg RELEASE=$TREE -t $IMAGE:tree-$TREE -t $IMAGE:sha-$GITHUB_SHA --push backend
fi
docker buildx imagetools create -t $IMAGE:prod $IMAGE:tree-$TREE   # move o ponteiro
```

- `RELEASE=<tree>` vai **dentro** da imagem (build arg → env) e aparece no `/health`. O smoke
  espera até o `/health` mostrar o `release` esperado → prova que o EasyPanel puxou a imagem nova.
- A imagem de prod é, byte a byte, a que rodou em hom.

## 4. GitHub Environments

| Environment | Branch | Proteção | Secrets |
|---|---|---|---|
| `hom` | `develop` | nenhuma (automático) | `EASYPANEL_HOOK_API`, `EASYPANEL_HOOK_WORKER`, `EASYPANEL_HOOK_BEAT`, `EASYPANEL_HOOK_WEB`, `API_URL`, `WEB_URL` |
| `prod` | `main` | **required reviewers** (Ro) + só branch `main` | mesmos nomes, valores de prod |

Os mesmos nomes de secret em cada environment deixam o workflow igual para os dois.

## 5. Ordem do deploy (por ambiente)

```text
1. api (roda migrate no start, RUN_MIGRATIONS=1)   → smoke /health/ready/ com release novo
2. worker e beat                                   → mesma imagem da api
3. web                                             → smoke /health com release novo
4. app nativo: eas update --channel preview|production (se mudou JS/asset)
```

Backend antes do frontend: a API nova precisa aceitar o app velho (compatibilidade para trás,
BE-02) — o contrário quebra usuário no meio do deploy.

## 6. Smoke test

Mínimo automático (no `deploy.yml`):

```text
api: GET /health/ready/ → 200 e release == tree esperado (até 3 min de espera)
web: GET /health       → 200 e release == tree esperado
web: GET /             → 200
```

Manual em hom (antes da release PR): login, fluxo crítico da história, tela nova no app.

## 7. Rollback

- **Aplicação:** `rollback.yml` com a tag `tree-…` anterior (está no histórico de deploys do
  Actions e no `/health` antigo). Move o ponteiro e redeploya. Não precisa de git revert para
  voltar o ar; o `revert` vem depois para o código ficar coerente.
- **Migration:** não volta sozinha. Por isso migration é compatível com o código anterior
  (expandir/contrair) — ver `migrations-e-rollback.md`.
- **Gatilho de rollback:** smoke falhou, 5xx disparou no Sentry após o deploy, health instável.

## 8. App nativo (EAS)

| Branch | Ação | Canal / perfil |
|---|---|---|
| `develop` | `eas update --channel preview` (JS) | build interna `preview` aponta para API de hom |
| `main` | `eas update --channel production` | build de loja `production` aponta para API de prod |
| mudança nativa (lib nativa, permissão, SDK) | `eas build --profile preview` → teste → `eas build --profile production` + `eas submit` | — |

`runtimeVersion` com `policy: fingerprint` impede update JS incompatível com o binário.
Detalhes do app: skill expo-app (`references/builds-eas.md`).

## 9. Quality gates (bloqueiam o merge)

```text
lint · testes backend (Postgres real) · testes frontend · makemigrations --check
OpenAPI sem diff · build da imagem web · (SEC-01: audit de dependências, scan de secrets)
```
