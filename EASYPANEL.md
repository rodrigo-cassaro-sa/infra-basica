# EasyPanel

Cada projeto usa **três serviços Compose no EasyPanel, um por branch**, todos com o mesmo `docker-compose.yml`. Cada serviço sobe Django, Expo e PostgreSQL; o `<projeto>-dev` sobe também o Code Server. O que muda entre eles é só o Ambiente (`.env`).

## Serviços

| Serviço EasyPanel | Branch | Ambiente (modelo) | `RUN_MODE` | Code Server |
|---|---|---|---|---|
| `<projeto>-dev` | `dev` | `.env.dev.example` | `dev` | sim (`COMPOSE_PROFILES=coder`) |
| `<projeto>-hom` | `hom` | `.env.hom.example` | `server` | não |
| `<projeto>-prod` | `main` | `.env.prod.example` | `server` | não |

Em todos:

- Fonte: repositório do projeto, **branch do ambiente**.
- Caminho de build: `/`
- Docker Compose: `docker-compose.yml`
- Ambiente: conteúdo do `.env.<ambiente>.example`, com os segredos trocados (`./scripts/generate-secrets.sh`, uma vez por ambiente).

Cada serviço tem rede, volumes e variáveis próprios: um deploy de HOM nunca toca PROD.

## O que `RUN_MODE` muda

- `dev`: Django (`runserver`) e Expo (Metro) rodam o **workspace do Code Server**. Editou, aparece na hora.
- `server`: Django (gunicorn) e Expo (build web + Nginx) rodam o **código da branch**, construído no deploy. Só mudam com PR para a branch e redeploy.

## Branches

Uma branch por ambiente: `dev` → DEV, `hom` → HOM, `main` → PROD. Depois de criar o repositório do projeto a partir do template, crie `dev` e `hom` a partir da `main` e deixe `dev` como branch padrão:

```bash
git switch -c hom && git push -u origin hom
git switch -c dev && git push -u origin dev
gh repo edit --default-branch dev
```

Proteja `main`, `hom` e `dev` (merge só por PR). Promoção: `feat|fix/H-xxx` → `dev` → `hom` → `main`. Hotfix sai de `main` e volta por back-merge para `hom` e `dev`.

- **HOM** recebe só a promoção por PR `dev → hom`. Ative o deploy automático (webhook do GitHub) se quiser que cada merge em `hom` atualize HOM.
- **PROD** só muda com o PR `hom → main`, depois da homologação e da aprovação de publicação, e o deploy de `<projeto>-prod`. Recomendado: deploy manual em PROD.

## Domínios

Os nomes dos serviços são os mesmos nos três ambientes:

| Uso | Serviço Compose | Porta interna |
|---|---|---:|
| Code Server (só DEV) | `code-server` | `8080` |
| App Web | `expo` | `8081` |
| API | `django` | `8000` |

Exemplo:

| | `<projeto>-dev` | `<projeto>-hom` | `<projeto>-prod` |
|---|---|---|---|
| Code Server | `coder-projeto.seudominio.com` | — | — |
| App Web | `dev-projeto.seudominio.com` | `hom-projeto.seudominio.com` | `projeto.seudominio.com` |
| API | `api-dev-projeto.seudominio.com` | `api-hom-projeto.seudominio.com` | `api-projeto.seudominio.com` |

No destino do domínio use **HTTP**; o EasyPanel/Traefik termina o HTTPS externamente. O domínio da API vai em `API_URL` e `DJANGO_ALLOWED_HOSTS`; o do App Web em `CORS_ALLOWED_ORIGINS`.

## Code Server (só no DEV)

O Code Server e a cópia do workspace estão no profile `coder` do compose, ligado só no `<projeto>-dev` (`COMPOSE_PROFILES=coder`). Em HOM e PROD `COMPOSE_PROFILES` fica vazio e eles não sobem.

Ao abrir o Code Server, o workspace é `/home/coder/workspace`: uma cópia privada da branch `dev` (ver `WORKSPACE-EASYPANEL.md`).

Se `GIT_USER_NAME`, `GIT_USER_EMAIL` e `GH_TOKEN` estiverem definidos no Ambiente, o Git e o GitHub já sobem configurados (reaplicados a cada inicialização do container). Use um token fine-grained restrito ao repositório do projeto (Contents e Pull requests: read/write). Para trocar o token, altere a variável e reimplante.

Sem essas variáveis, na primeira abertura de um terminal o ambiente pede nome e e-mail do Git e faz o login no GitHub via `gh auth login`.

Ligar o Code Server em HOM ou PROD é exceção (diagnóstico): ele alcança o banco do ambiente pela rede interna. Nesse caso use `CODER_PASSWORD` forte e desligue ao terminar.

## Claude Code

A configuração do Claude é persistida no volume `coder_claude` do DEV. O entrypoint corrige as permissões automaticamente e mantém `.claude.json` dentro desse volume por meio de um link simbólico.

## Observação sobre Expo

- Em `RUN_MODE=server`, `API_URL` é embutida no build (`expo export --platform web`): mudou, reimplante.
- Para Android/iOS use EAS Build a partir do Code Server (`eas build`).
