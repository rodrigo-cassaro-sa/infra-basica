#!/usr/bin/env bash
set -euo pipefail
for name in CODER_PASSWORD DEV_DB_PASSWORD HOM_DB_PASSWORD PROD_DB_PASSWORD DJANGO_SECRET_KEY_DEV DJANGO_SECRET_KEY_HOM DJANGO_SECRET_KEY_PROD; do
  printf '%s=' "$name"
  openssl rand -base64 36 | tr -d '\n' | tr '/+' '_-'
  printf '\n'
done
