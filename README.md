# Template de Projeto — Django + Expo + Code Server + DEV/HOM/PROD

Este repositório é um **molde para cada novo projeto** da software house. A ideia é simples:

```text
1 projeto = 1 repositório = 3 branches (dev, hom, main) = 3 serviços EasyPanel
cada serviço = Django + Expo + PostgreSQL (+ Code Server no dev), mesmo docker-compose.yml
```

## Estrutura

```text
.
├── backend/               # Django
├── frontend/              # Expo / React Native / Web
├── coder/                 # Code Server + Claude Code + GitHub CLI
├── scripts/               # operação/backup
├── backups/
├── docker-compose.yml       # o único compose (todos os ambientes)
├── docker-compose.local.yml # portas para rodar fora do EasyPanel
├── .env.dev.example         # Ambiente do <projeto>-dev  (branch dev)
├── .env.hom.example         # Ambiente do <projeto>-hom  (branch hom)
├── .env.prod.example        # Ambiente do <projeto>-prod (branch main)
├── EASYPANEL.md
└── README.md
```

## Serviços

Cada serviço EasyPanel (um por branch) sobe:

```text
<projeto>-dev | <projeto>-hom | <projeto>-prod
├── postgres
├── django        RUN_MODE=dev: runserver no workspace · server: gunicorn
├── expo          RUN_MODE=dev: Metro no workspace     · server: build web + Nginx
└── code-server   só no <projeto>-dev (COMPOSE_PROFILES=coder)
    ├── workspace = /home/coder/workspace (cópia da branch dev)
    ├── Português (Brasil), tema escuro
    ├── Claude Code, Git / GitHub CLI
    ├── Python, Node.js 22, pnpm, EAS CLI
    └── PostgreSQL Client
```

## Primeiro uso no servidor

1. Crie um novo repositório a partir deste template e crie as branches `dev` e `hom` a partir da `main`.
2. Crie três serviços Compose no EasyPanel (`<projeto>-dev`, `<projeto>-hom`, `<projeto>-prod`), cada um na sua branch, todos com `docker-compose.yml` e caminho de build `/` — ver `EASYPANEL.md`.
3. No Ambiente de cada serviço, cole o `.env.<ambiente>.example` correspondente.
4. Troque senhas e chaves (`./scripts/generate-secrets.sh`, uma vez por ambiente) e ajuste os domínios.
5. Implante.
6. Cadastre os domínios conforme `EASYPANEL.md`.

## Primeiro uso local

```bash
cp .env.dev.example .env
./scripts/generate-secrets.sh
# copie os valores gerados para .env

docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

Portas locais: `8080` Code Server · `8081` Expo · `8000` Django.

## Code Server

Acesse o domínio configurado para `code-server:8080`. A senha vem de `CODER_PASSWORD`.

O Code Server abre diretamente em:

```text
/home/coder/workspace
```

Esse caminho contém **o próprio repositório do projeto** (`backend`, `frontend`, `coder`, Compose etc.).

Na primeira abertura do terminal será executada a configuração inicial do Git/GitHub. O login é feito pelo fluxo do GitHub CLI e não grava senha em texto puro.

## API de teste

Depois do deploy, o Django de cada ambiente expõe:

```text
/api/health/
```

## Criar um novo projeto

O fluxo esperado é:

```text
Template
   ↓
Novo repositório (dev + hom + main)
   ↓
EasyPanel: <projeto>-dev, <projeto>-hom, <projeto>-prod
   ↓
Code Server daquele projeto
   ↓
Desenvolvimento DEV (branch feat/H-xxx a partir de dev) → PR para dev
   ↓
PR dev → hom → deploy HOM → homologação
   ↓
PR hom → main → deploy PROD
```

## Segurança

O PostgreSQL não publica porta no host. Use senhas fortes, restrinja os `ALLOWED_HOSTS` em HOM/PROD e configure os domínios HTTPS no EasyPanel.
