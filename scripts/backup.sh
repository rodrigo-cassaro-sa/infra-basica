#!/usr/bin/env bash
set -euo pipefail
ENVIRONMENT="${1:-}"
case "$ENVIRONMENT" in
  dev)  SERVICE=postgres-dev;  DB_VAR=DEV_DB_NAME;  USER_VAR=DEV_DB_USER ;;
  hom)  SERVICE=postgres-hom;  DB_VAR=HOM_DB_NAME;  USER_VAR=HOM_DB_USER ;;
  prod) SERVICE=postgres-prod; DB_VAR=PROD_DB_NAME; USER_VAR=PROD_DB_USER ;;
  *) echo "Uso: $0 dev|hom|prod"; exit 1 ;;
esac
set -a
[ -f .env ] && source .env
set +a
DB_NAME="${!DB_VAR:-app_${ENVIRONMENT}}"
DB_USER="${!USER_VAR:-app_${ENVIRONMENT}}"
mkdir -p backups
FILE="backups/${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S).sql"
docker compose exec -T "$SERVICE" pg_dump -U "$DB_USER" "$DB_NAME" > "$FILE"
echo "Backup criado: $FILE"
