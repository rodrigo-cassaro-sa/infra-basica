# EasyPanel

Este repositório foi desenhado para ser usado como **um projeto completo por repositório**.

## Um serviço Compose por ambiente, cada um na sua branch

Crie **três serviços Compose** no EasyPanel, todos apontando para o repositório do projeto, com caminho de build `/`:

| Serviço EasyPanel | Branch | Arquivo Compose | Serviços |
|---|---|---|---|
| `<projeto>-dev` | `develop` | `docker-compose.dev.yml` | `code-server`, `django-dev`, `expo-dev`, `postgres-dev` |
| `<projeto>-hom` | `develop` | `docker-compose.hom.yml` | `django-hom`, `expo-hom`, `postgres-hom` |
| `<projeto>-prod` | `main` | `docker-compose.prod.yml` | `django-prod`, `expo-prod`, `postgres-prod` |

- Cada serviço tem rede, volumes e variáveis próprios: um deploy de HOM nunca toca PROD.
- **HOM** recebe o que foi mesclado em `develop`. Ative o deploy automático (webhook do GitHub) se quiser que cada merge em `develop` atualize HOM.
- **PROD** só muda com o release PR `develop → main` aprovado e o deploy de `<projeto>-prod`. Recomendado: deploy manual em PROD.
- **DEV** roda o código do workspace do Code Server (volume `coder_workspace`), não o checkout. A branch só alimenta a cópia inicial do workspace; depois o trabalho acontece em branches `feat/H-xxx-*` criadas a partir de `develop` dentro do Code Server.
- O `docker-compose.yml` inclui os três arquivos e serve para rodar tudo junto localmente.

### Branches

Depois de criar o repositório do projeto a partir do template, crie a `develop` a partir da `main` e deixe-a como branch padrão:

```bash
git switch -c develop && git push -u origin develop
gh repo edit --default-branch develop
```

Proteja `main` e `develop` (merge só por PR). Fluxo completo na skill `git-deploy`.

## Variáveis

Use `.env.example` como modelo. No Ambiente de cada serviço EasyPanel, preencha as variáveis do próprio ambiente (prefixo `DEV_`, `HOM_` ou `PROD_`) e as comuns (`TZ`). As do Code Server (`CODER_PASSWORD`, `GIT_USER_NAME`, `GIT_USER_EMAIL`, `GH_TOKEN`) vão só no `<projeto>-dev`. Troque todos os segredos.

## Domínios recomendados

| Uso | Serviço EasyPanel | Serviço Compose | Porta interna |
|---|---|---|---:|
| Code Server | `<projeto>-dev` | `code-server` | `8080` |
| App DEV Web | `<projeto>-dev` | `expo-dev` | `8081` |
| API DEV | `<projeto>-dev` | `django-dev` | `8000` |
| App HOM Web | `<projeto>-hom` | `expo-hom` | `80` |
| API HOM | `<projeto>-hom` | `django-hom` | `8000` |
| App PROD Web | `<projeto>-prod` | `expo-prod` | `80` |
| API PROD | `<projeto>-prod` | `django-prod` | `8000` |

Exemplo:

- `coder-projeto.seudominio.com` -> `code-server:8080`
- `dev-projeto.seudominio.com` -> `expo-dev:8081`
- `api-dev-projeto.seudominio.com` -> `django-dev:8000`
- `hom-projeto.seudominio.com` -> `expo-hom:80`
- `api-hom-projeto.seudominio.com` -> `django-hom:8000`
- `projeto.seudominio.com` -> `expo-prod:80`
- `api-projeto.seudominio.com` -> `django-prod:8000`

No destino do domínio use **HTTP**; o EasyPanel/Traefik termina o HTTPS externamente.

## Code Server

Ao abrir o Code Server, o workspace é:

```text
/home/coder/workspace
```

Esse diretório é a raiz deste próprio repositório (cópia privada, ver `WORKSPACE-EASYPANEL.md`).

Se `GIT_USER_NAME`, `GIT_USER_EMAIL` e `GH_TOKEN` estiverem definidos no Ambiente do EasyPanel, o Git e o GitHub já sobem configurados (reaplicados a cada inicialização do container). Use um token fine-grained restrito ao repositório do projeto (Contents e Pull requests: read/write). Para trocar o token, altere a variável e reimplante.

Sem essas variáveis, na primeira abertura de um terminal o ambiente pede:

1. nome do Git;
2. e-mail do Git;
3. autenticação segura no GitHub via `gh auth login`.

Depois ficam disponíveis `git commit`, `git pull`, `git push`, `gh repo create` etc.

## Claude Code

A configuração do Claude é persistida no volume `coder_claude`. O entrypoint corrige as permissões automaticamente e mantém `.claude.json` dentro desse volume por meio de um link simbólico.

## Observação sobre Expo

- DEV usa Metro e porta `8081`.
- HOM e PROD fazem `expo export --platform web` durante o build e são servidos por Nginx na porta `80`.
- Para Android/iOS use EAS Build a partir do Code Server (`eas build`).
