#!/usr/bin/env bash
# Backup do PostgreSQL do ambiente em execução (lê DB_NAME/DB_USER do .env).
set -euo pipefail
set -a
[ -f .env ] && source .env
set +a
DB_NAME="${DB_NAME:-app}"
DB_USER="${DB_USER:-app}"
mkdir -p backups
FILE="backups/${COMPOSE_PROJECT_NAME:-app}-$(date +%Y%m%d-%H%M%S).sql"
docker compose exec -T postgres pg_dump -U "$DB_USER" "$DB_NAME" > "$FILE"
echo "Backup criado: $FILE"
