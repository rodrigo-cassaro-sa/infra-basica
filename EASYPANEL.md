# EasyPanel

Este repositório foi desenhado para ser usado como **um projeto completo por repositório**.

## Fonte

- Caminho de build: `/`
- Docker Compose: `docker-compose.yml`

## Variáveis

Copie as variáveis de `.env.example` para a área **Ambiente** do EasyPanel e troque todos os segredos.

## Domínios recomendados

| Uso | Serviço Compose | Porta interna |
|---|---|---:|
| Code Server | `code-server` | `8080` |
| App DEV Web | `expo-dev` | `8081` |
| API DEV | `django-dev` | `8000` |
| App HOM Web | `expo-hom` | `80` |
| API HOM | `django-hom` | `8000` |
| App PROD Web | `expo-prod` | `80` |
| API PROD | `django-prod` | `8000` |

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

Esse diretório é a raiz deste próprio repositório.

Na primeira abertura de um terminal, o ambiente pede:

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
