# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Visão geral

Repositório **base (template) de infraestrutura** da software house: cada novo projeto nasce dele. **1 repositório = 1 Code Server + Django + Expo + ambientes DEV/HOM/PROD**, implantado como um único serviço Docker Compose no EasyPanel. A documentação e o código usam português (settings `LANGUAGE_CODE = "pt-br"`, TZ `America/Sao_Paulo`).

Regras do template:
- **Stack fixa:** backend sempre Django, frontend sempre Expo (mobile + web). Não introduzir outros frameworks de backend/frontend.
- **Code Server é o ambiente de programação** do projeto; o código é editado ali e roda no DEV.
- **DEV, HOM e PROD são totalmente separados:** cada um tem seu próprio PostgreSQL, Django e Expo, com banco, volume, segredos e variáveis próprios. Nunca compartilhar banco ou segredos entre ambientes. Ao adicionar um serviço ou variável, replicar nos três ambientes, mantendo o padrão de prefixos `DEV_`/`HOM_`/`PROD_`.
- Fluxo de promoção: desenvolvimento em DEV (Code Server) → validação em HOM → publicação em PROD, sempre via Git + deploy no EasyPanel.

Estrutura:
- `backend/` — Django 5.2 + PostgreSQL 17 (psycopg 3), gunicorn, django-cors-headers. Projeto em `config/`, app inicial `core/` (expõe `GET /api/health/`).
- `frontend/` — Expo SDK 57 / React Native 0.86 / React 19.2, TypeScript 6, com suporte web via Metro (`react-native-web`). Ponto de entrada `index.js` → `App.tsx`.
- `coder/` — imagem do Code Server (Node 22, Python, pnpm, EAS CLI, gh, Claude Code, psql). É onde o Claude Code roda.
- `docker-compose.yml` — define todos os serviços; `docker-compose.local.yml` só publica portas para testes fora do EasyPanel.

## Arquitetura do workspace (importante)

O Claude Code roda **dentro do container `code-server`**, em `/home/coder/workspace`, que é o volume `coder_workspace` — uma **cópia privada** do repositório feita uma única vez pelo serviço `workspace-init` (nas execuções seguintes ele não sobrescreve nada).

- `django-dev` e `expo-dev` montam esse **mesmo volume**: edições aqui aparecem imediatamente no DEV (`runserver` com autoreload e Metro com hot reload). `django-dev` roda `migrate` ao iniciar.
- `django-hom`/`django-prod` e `expo-hom`/`expo-prod` são construídos a partir do checkout do EasyPanel/Git, **não** deste workspace. Para chegar a HOM/PROD é preciso `git push` + redeploy no EasyPanel.
- HOM/PROD do frontend são build estático (`expo export --platform web`) servido por Nginx; `EXPO_PUBLIC_API_URL` é embutida **no build** via build arg (`HOM_API_URL`/`PROD_API_URL`), então mudá-la exige rebuild.
- Git/GitHub do code-server: `coder/entrypoint.sh` aplica `GIT_USER_NAME`/`GIT_USER_EMAIL` e, com `GH_TOKEN`, configura o `gh` como credential helper do Git. Sem essas variáveis, `coder/git-bootstrap.sh` faz o login interativo no primeiro terminal.
- Não há Docker CLI nem Django instalados dentro do code-server; os hostnames dos serviços Compose (ex.: `postgres-dev`) resolvem pela rede interna. Os comandos `make` / `scripts/*.sh` usam `docker compose` e devem ser executados no host.

## Configuração do Django

- Settings divididos em `config/settings/{base,development,homologation,production}.py`, escolhidos por `DJANGO_SETTINGS_MODULE` no Compose. `base` tem `DEBUG = False`; só `development` liga o DEBUG.
- Tudo vem de variáveis de ambiente: `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` e `CORS_ALLOWED_ORIGINS` (listas separadas por vírgula), `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD`. No `.env`, cada variável tem prefixo por ambiente (`DEV_`, `HOM_`, `PROD_`, `DJANGO_SECRET_KEY_DEV` etc.) e o Compose faz o mapeamento.
- Se `CORS_ALLOWED_ORIGINS` estiver vazio, `CORS_ALLOW_ALL_ORIGINS` fica `True`.
- HOM/PROD ficam atrás do Traefik do EasyPanel (HTTPS terminado externamente), por isso `SECURE_PROXY_SSL_HEADER`. Os containers HOM/PROD rodam `migrate` + `collectstatic` na inicialização.
- `AUTH_PASSWORD_VALIDATORS` está vazio de propósito no template.

## Comandos

Não há testes, linter nem formatador configurados no projeto.

Backend dentro do code-server (usando o banco DEV pela rede do Compose):

```bash
cd backend
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=config.settings.development DB_HOST=postgres-dev \
       DB_NAME=app_dev DB_USER=app_dev DB_PASSWORD=<DEV_DB_PASSWORD>
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
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build   # local, portas 8080–8083 e 8001–8003
make up | down | ps | logs | health
make backup-dev | backup-hom | backup-prod   # pg_dump para backups/
./scripts/generate-secrets.sh                # gera segredos para o .env
```

Health checks: Django em `/api/health/`, Nginx do Expo em `/healthz`, Code Server em `/healthz`.

## Segurança / operação

- Os PostgreSQL não publicam portas no Compose principal.
- O Compose nunca deve montar `./` como gravável no code-server (evita problemas de `dubious ownership` no checkout do EasyPanel — ver `WORKSPACE-EASYPANEL.md`).
- Domínios e portas internas por serviço estão em `EASYPANEL.md`.
