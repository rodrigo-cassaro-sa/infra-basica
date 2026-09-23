#!/usr/bin/env bash
# Gera os segredos de UM ambiente. Rode uma vez para cada serviço (dev, hom, prod).
set -euo pipefail
for name in CODER_PASSWORD DB_PASSWORD DJANGO_SECRET_KEY; do
  printf '%s=' "$name"
  openssl rand -base64 36 | tr -d '\n' | tr '/+' '_-'
  printf '\n'
done
