#!/usr/bin/env bash
set -euo pipefail
docker compose ps
printf '\nDjango:      '; docker compose exec -T django      curl -fsS http://localhost:8000/api/health/ || true
printf '\nCode Server: '; docker compose exec -T code-server curl -fsS http://localhost:8080/healthz || true
printf '\n'
