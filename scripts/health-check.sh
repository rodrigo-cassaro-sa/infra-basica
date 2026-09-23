#!/usr/bin/env bash
set -euo pipefail
docker compose ps
printf '\nDjango DEV:  '; docker compose exec -T django-dev  curl -fsS http://localhost:8000/api/health/ || true
printf '\nDjango HOM:  '; docker compose exec -T django-hom  curl -fsS http://localhost:8000/api/health/ || true
printf '\nDjango PROD: '; docker compose exec -T django-prod curl -fsS http://localhost:8000/api/health/ || true
printf '\nCode Server: '; docker compose exec -T code-server curl -fsS http://localhost:8080/healthz || true
printf '\n'
