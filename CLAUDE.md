# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Visão geral

Repositório **base (template) de infraestrutura** da software house: cada novo projeto nasce dele. **1 repositório = 3 serviços EasyPanel, um por branch (`dev`, `hom`, `main`), todos com o mesmo `docker-compose.yml`**. Cada serviço sobe Code Server + Django + Expo + PostgreSQL; o que muda entre eles é só o Ambiente (`.env`). A documentação e o código usam português (settings `LANGUAGE_CODE = "pt-br"`, TZ `America/Sao_Paulo`).

Regras do template:
- **Stack fixa:** backend sempre Django, frontend sempre Expo (mobile + web). Não introduzir outros frameworks de backend/frontend.
- **Um compose, um `.env` por ambiente.** Nada de arquivo ou prefixo por ambiente: toda diferença entre DEV, HOM e PROD é variável, com o mesmo nome nos três. Variável nova entra no `docker-compose.yml` com default (`${VAR:-padrão}`) e nos três `.env.<ambiente>.example`.
- **DEV, HOM e PROD são totalmente separados:** cada serviço EasyPanel tem rede, volumes, banco, segredos e Code Server próprios. Nunca compartilhar banco ou segredos entre ambientes.
- **Uma branch por ambiente: `dev` → DEV, `hom` → HOM, `main` → PROD.** Trabalho em `feat|fix/H-xxx-slug` criada a partir de `dev` → PR para `dev` → promoção por PR `dev → hom` (deploy HOM, homologação) → PR `hom → main` (deploy PROD, só após "Aprovo publicação"). Hotfix: `hotfix/slug` a partir de `main` → PR para `main` → back-merge `main → hom → dev`. Nada chega a `main` sem ter passado por `hom`, exceto hotfix. Este modelo **substitui** o `develop`/`main` descrito nas skills `git-deploy` e `devops`.

Estrutura:
- `backend/` — Django 5.2 + PostgreSQL 17 (psycopg 3), gunicorn, django-cors-headers. Projeto em `config/`, app inicial `core/` (expõe `GET /api/health/`). `docker-entrypoint.sh` escolhe o modo de execução por `RUN_MODE`.
- `frontend/` — Expo SDK 57 / React Native 0.86 / React 19.2, TypeScript 6, com suporte web via Metro (`react-native-web`). Expo Router (`main: expo-router/entry`): rotas finas em `src/app/` que só reexportam a screen de `src/features/<feature>/screens/`; import absoluto `@/` → `src/`; typed routes ligadas. Padrão completo na skill `expo-app`. Um `Dockerfile` com alvos `dev` (Metro) e `server` (export web + Nginx).
- `coder/` — imagem do Code Server (Node 22, Python, pnpm, EAS CLI, gh, Claude Code, psql). É onde o Claude Code roda.
- `docker-compose.yml` — o único compose (serviços `workspace-init`, `postgres`, `django`, `expo`, `code-server`); `docker-compose.local.yml` só publica portas para rodar fora do EasyPanel.
- `.env.dev.example`, `.env.hom.example`, `.env.prod.example` — o Ambiente de cada serviço EasyPanel.

## Como cada ambiente roda (importante)

O Claude Code roda **dentro do container `code-server`**, em `/home/coder/workspace`, que é o volume `coder_workspace` — uma **cópia privada** da branch daquele serviço, feita uma única vez pelo `workspace-init` (nas execuções seguintes ele não sobrescreve nada). Cada ambiente tem o seu Code Server e o seu workspace.

`RUN_MODE` decide o que `django` e `expo` executam:

| `RUN_MODE` | Ambiente | Django | Expo | Código |
|---|---|---|---|---|
| `dev` | DEV | `runserver` com autoreload | Metro (`expo start --web`) com hot reload | workspace do Code Server |
| `server` | HOM, PROD | `migrate` + `collectstatic` + gunicorn | `expo export --platform web` servido por Nginx | checkout da branch (build da imagem) |

- Em `dev`, editar no Code Server aparece na hora no DEV. Em `server`, editar no Code Server **não** muda o que está no ar: só commit + PR na branch + redeploy.
- Em `server`, `API_URL` é embutida **no build** do Expo: mudou, reimplante.
- Os dois modos respondem nas mesmas portas: `django:8000`, `expo:8081`, `code-server:8080`.
- Git/GitHub do code-server: `coder/entrypoint.sh` aplica `GIT_USER_NAME`/`GIT_USER_EMAIL` e, com `GH_TOKEN`, configura o `gh` como credential helper do Git. Sem essas variáveis, `coder/git-bootstrap.sh` faz o login interativo no primeiro terminal.
- Não há Docker CLI nem Django instalados dentro do code-server; os hostnames dos serviços Compose (`postgres`, `django`, `expo`) resolvem pela rede interna do ambiente. `make` / `scripts/*.sh` usam `docker compose` e rodam no host.

## Configuração do Django

- Settings divididos em `config/settings/{base,development,homologation,production}.py`, escolhidos por `DJANGO_SETTINGS_MODULE` do `.env`. `base` tem `DEBUG = False`; só `development` liga o DEBUG.
- Tudo vem de variáveis de ambiente: `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` e `CORS_ALLOWED_ORIGINS` (listas separadas por vírgula), `DB_NAME/DB_USER/DB_PASSWORD` (`DB_HOST=postgres` fixo no compose).
- Se `CORS_ALLOWED_ORIGINS` estiver vazio, `CORS_ALLOW_ALL_ORIGINS` fica `True`.
- HOM/PROD ficam atrás do Traefik do EasyPanel (HTTPS terminado externamente), por isso `SECURE_PROXY_SSL_HEADER`.
- `AUTH_PASSWORD_VALIDATORS` está vazio de propósito no template.

## Comandos

Não há testes, linter nem formatador configurados no projeto.

Backend dentro do code-server (usando o banco do próprio ambiente pela rede do Compose):

```bash
cd backend
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=config.settings.development DB_HOST=postgres \
       DB_NAME=<DB_NAME> DB_USER=<DB_USER> DB_PASSWORD=<DB_PASSWORD>
python manage.py makemigrations
python manage.py test                     # todos os testes
python manage.py test core.tests.MinhaClasse.test_x   # um teste
```

Frontend (`frontend/`, gerenciado com npm — há `package-lock.json`):

```bash
npm install
npx expo install <pacote>   # adiciona dependências na versão compatível com o SDK
npx expo install --check   # valida versões contra o SDK do Expo
npx tsc --noEmit           # checagem de tipos
npm run web          # expo start --web
npm run export:web   # build estático em dist/
eas build            # builds Android/iOS (perfis em eas.json: development, preview, production)
```

No host (Docker disponível):

```bash
cp .env.dev.example .env                     # ou .env.hom / .env.prod
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build   # portas 8000, 8081 e 8080
make up | down | ps | logs | health | backup # backup = pg_dump para backups/
./scripts/generate-secrets.sh                # segredos de UM ambiente
```

Health checks: Django em `/api/health/`, Nginx do Expo em `/healthz`, Code Server em `/healthz`.

## Documentação do projeto (método DAH)

O projeto segue a DAH (Desenvolvimento Assistido por Histórias). Trilha, gates humanos, numeração, propriedade dos documentos e Definitions of Done estão no `AGENTS.md`, que vale para todo trabalho no repositório:

@AGENTS.md


`docs/` traz os **modelos em branco** da documentação que as skills leem e mantêm. No repositório do app eles são preenchidos; no template ficam vazios.

- `docs/produto.md` (visão, capítulos, papéis, vocabulário) e `docs/historias/` (`indice.md` + `H-xxx-*.md`): especificação funcional.
- Derivados das Histórias (`dah-documentacao`): `regras-de-negocio.md`, `modelo-de-dados.md`, `mapa-de-fluxos.md`, `mapa-de-telas.md`, `contratos-de-api.md`, `mapa-de-decisoes.md`.
- Governança e qualidade: `cronograma.md`, `diario-de-bordo.md`, `mapa-de-testes.md`; interface: `guia-visual.md`; operação: `deploy.md`.
- `docs/prompts/`: prompts do fluxo DAH, trilha padrão P-01 a P-06 (backlog → história → documentação → interface → implementação → homologação/publicação) e trilha de artefatos PA-01 a PA-03 (analisar código gerado por IA).
- D-001 a D-005 em `mapa-de-decisoes.md` são decisões da casa; a numeração própria de cada projeto começa em D-006.

## Skills do template

`.claude/skills/` traz as skills genéricas de desenvolvimento da casa (versionadas no template, herdadas por todo projeto novo): backend Django (`backend-core`, `backend-api`, `backend-async`, `backend-integrations`, `backend-ai-mcp`), frontend Expo (`expo-app`, `ux-ui`, `frontend-web`), método DAH (`dah-historia`, `dah-documentacao`, `project-governance`, `artifact-analysis`) e transversais (`security`, `testing-quality`, `devops`, `git-deploy`). Skills específicas de um aplicativo ficam só no repositório do app.

Atenção: `devops` e `git-deploy` descrevem imagens no GHCR, GitHub Actions e branches `develop`→HOM / `main`→PROD. Neste template valem as branches `dev`/`hom`/`main` e o build de cada ambiente pelo EasyPanel a partir da própria branch (ver `docs/deploy.md`). Adotar pipeline com imagens é decisão a registrar no projeto.

## Segurança / operação

- O PostgreSQL não publica porta; só a rede interna do ambiente o alcança.
- O Code Server de HOM e PROD alcança o banco do próprio ambiente: `CODER_PASSWORD` forte em todos.
- O Compose nunca deve montar `./` como gravável no code-server (evita problemas de `dubious ownership` no checkout do EasyPanel — ver `WORKSPACE-EASYPANEL.md`).
- Domínios e portas internas por serviço estão em `EASYPANEL.md`.
