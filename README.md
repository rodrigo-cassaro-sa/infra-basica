# Template de Projeto — Django + Expo + Code Server + DEV/HOM/PROD

Este repositório é um **molde para cada novo projeto** da software house. A ideia é simples:

```text
1 projeto = 1 repositório = 1 Code Server + Django + Expo + DEV/HOM/PROD
```

## Estrutura

```text
.
├── backend/               # Django
├── frontend/              # Expo / React Native / Web
├── coder/                 # Code Server + Claude Code + GitHub CLI
├── scripts/               # operação/backup
├── backups/
├── docker-compose.dev.yml   # EasyPanel <projeto>-dev  (branch develop)
├── docker-compose.hom.yml   # EasyPanel <projeto>-hom  (branch develop)
├── docker-compose.prod.yml  # EasyPanel <projeto>-prod (branch main)
├── docker-compose.yml       # inclui os três (uso local)
├── docker-compose.local.yml
├── .env.example
├── EASYPANEL.md
└── README.md
```

## Serviços

```text
DEV
├── postgres-dev
├── django-dev
└── expo-dev (Metro/Web)

HOM
├── postgres-hom
├── django-hom
└── expo-hom (build estático + Nginx)

PROD
├── postgres-prod
├── django-prod
└── expo-prod (build estático + Nginx)

DESENVOLVIMENTO (serviço DEV)
└── code-server
    ├── workspace = /home/coder/workspace
    ├── Português (Brasil)
    ├── tema escuro
    ├── Claude Code
    ├── Git / GitHub CLI
    ├── Python
    ├── Node.js 22
    ├── pnpm
    ├── EAS CLI
    └── PostgreSQL Client
```

## Primeiro uso no servidor

1. Crie um novo repositório a partir deste template e crie a branch `develop` a partir da `main`.
2. Crie três serviços Compose no EasyPanel (`<projeto>-dev`, `<projeto>-hom`, `<projeto>-prod`), cada um com seu arquivo e sua branch — ver `EASYPANEL.md`.
3. Use `/` como caminho de build.
4. Preencha as variáveis de cada ambiente a partir de `.env.example`.
5. Troque todas as senhas e chaves.
6. Implante.
7. Cadastre os domínios conforme `EASYPANEL.md`.

## Primeiro uso local

```bash
cp .env.example .env
./scripts/generate-secrets.sh
# copie os valores gerados para .env

docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

Portas locais do override:

- `8080` Code Server
- `8081` Expo DEV
- `8082` Expo HOM
- `8083` Expo PROD
- `8001` Django DEV
- `8002` Django HOM
- `8003` Django PROD

## Code Server

Acesse o domínio configurado para `code-server:8080`. A senha vem de `CODER_PASSWORD`.

O Code Server abre diretamente em:

```text
/home/coder/workspace
```

Esse caminho contém **o próprio repositório do projeto** (`backend`, `frontend`, `coder`, Compose etc.).

Na primeira abertura do terminal será executada a configuração inicial do Git/GitHub. O login é feito pelo fluxo do GitHub CLI e não grava senha em texto puro.

## API de teste

Depois do deploy, cada Django expõe:

```text
/api/health/
```

## Criar um novo projeto

O fluxo esperado é:

```text
Template
   ↓
Novo repositório (main + develop)
   ↓
EasyPanel: <projeto>-dev, <projeto>-hom, <projeto>-prod
   ↓
Code Server daquele projeto
   ↓
Desenvolvimento DEV (branch feat/H-xxx a partir de develop)
   ↓
PR → develop → deploy HOM → validação
   ↓
Release PR develop → main → deploy PROD
```

## Segurança

Os bancos PostgreSQL não publicam portas no host no Compose principal. Use senhas fortes, restrinja os `ALLOWED_HOSTS` em HOM/PROD e configure os domínios HTTPS no EasyPanel.
