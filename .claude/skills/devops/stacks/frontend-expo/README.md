# Stack frontend-expo (OPS-01)

Um código Expo, três saídas: **web** (site estático no EasyPanel), **Android/iOS** (EAS
Build/Submit) e **updates JS** (EAS Update). As mesmas regras de ambiente do backend.

## Arquivos

| Arquivo | Vai para | Função |
|---|---|---|
| `Dockerfile.web` | `app/Dockerfile` | `expo export -p web` + Caddy não-root na porta 8080; `ARG RELEASE` = tree de `app/` |
| `Caddyfile` | `app/Caddyfile` | rotas do Expo Router, cache (assets imutáveis, páginas no-cache), `/health`, `/config.js` |
| `docker-entrypoint.sh` | `app/docker-entrypoint.sh` | escreve `/srv/config.js` e `/srv/health.json` a partir das envs |
| `html.tsx` | `app/app/+html.tsx` | carrega `/config.js` antes do bundle |
| `env.ts` | `app/src/config/env.ts` | único ponto que lê configuração (web runtime / nativo EAS / dev) |
| `eas.json` | `app/eas.json` | perfis development / preview (hom) / production (prod) com channels |
| `dockerignore` | `app/.dockerignore` | fora: node_modules, dist, nativo gerado, .env |

## Web: mesma imagem em hom e prod

`EXPO_PUBLIC_*` é embutido no build — se a URL da API entrasse na imagem, prod precisaria de
outro build e a promoção de artefato (OPS-01 §17) quebraria. Por isso no web:

```text
EasyPanel (serviço web) envs: API_URL, APP_ENV, SENTRY_DSN_WEB (opcional)
        │  container sobe
        ▼
docker-entrypoint.sh → /srv/config.js  { apiUrl, appEnv, sentryDsn, release }
                     → /srv/health.json { status, release, env }
        ▼
+html.tsx carrega /config.js → env.ts lê window.__APP_CONFIG__
```

- Só valor **público** em `config.js` (vai para o navegador). Segredo nunca.
- Mudou a URL da API? Troca a env e reinicia o serviço — sem rebuild.
- `GET /health` → `{"status":"ok","release":"<tree>","env":"hom"}`: o smoke confere o release.
- Código do app nunca lê `process.env.EXPO_PUBLIC_API_URL` direto: sempre `config` de `env.ts`.
- Caddy roda como usuário `web` (uid 10001), porta **8080**, sem admin API.

## Nativo: um binário por ambiente

Binário não tem "container" para trocar config, então aqui é build por perfil (é a exceção
correta, não um desvio):

| Perfil EAS | Channel | Ambiente | API | Distribuição |
|---|---|---|---|---|
| `development` | development | dev | IP local | dev client |
| `preview` | preview | **hom** | `api.hom…` | interna (link/TestFlight interno) |
| `production` | production | **prod** | `api…` | lojas |

- No `app.json`: `"runtimeVersion": {"policy": "fingerprint"}` → update JS nunca cai num binário incompatível.
- `develop` → `eas update --channel preview`; `main` → `eas update --channel production` (no `deploy.yml`).
- Mudança nativa (lib nativa, permissão, SDK) → `eas build --profile preview`, testar, depois `production` + `eas submit`.
- Deixar `app.hom` distinguível: nome/ícone com sufixo "HOM" via `app.config.ts` lendo `EXPO_PUBLIC_APP_ENV` (evita testar em prod achando que é hom).

## Regras do stack

- Build de web **só no Actions** (o `expo export` estoura memória em servidor pequeno).
- Backend deployado antes do web e do update do app (compatibilidade para trás).
- Sentry do app com `environment = config.appEnv` e `release = config.release`.
- Chamada à API envia `X-Request-ID` (UUID por ação) e mostra no erro para o usuário reportar.
- Autenticação: JWT (BE-02 `autenticacao.md`); web em domínio próprio (`app.…`) chamando `api.…` com CORS restrito.
