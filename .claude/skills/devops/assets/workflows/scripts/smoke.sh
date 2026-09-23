#!/usr/bin/env bash
# .github/scripts/smoke.sh <url_do_health> <release_esperado> [timeout_s]
# Espera o serviço responder 200 COM o release esperado — prova que o EasyPanel puxou a imagem nova.
set -euo pipefail
URL="$1"; EXPECTED="$2"; TIMEOUT="${3:-240}"
deadline=$(( $(date +%s) + TIMEOUT ))
while :; do
  body=$(curl -fsS --max-time 5 "$URL" 2>/dev/null || true)
  release=$(printf '%s' "$body" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("release",""))' 2>/dev/null || true)
  status=$(printf '%s' "$body" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("status",""))' 2>/dev/null || true)
  if [ "$status" = "ok" ] && [ "$release" = "$EXPECTED" ]; then
    echo "smoke ok: $URL release=$release"
    exit 0
  fi
  if [ "$(date +%s)" -ge "$deadline" ]; then
    echo "::error::smoke falhou: $URL status='$status' release='$release' (esperado $EXPECTED)"
    exit 1
  fi
  sleep 5
done
