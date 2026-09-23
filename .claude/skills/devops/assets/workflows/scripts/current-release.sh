#!/usr/bin/env bash
# .github/scripts/current-release.sh <url_do_health> — imprime o release que está no ar (ou vazio)
curl -fsS --max-time 5 "$1" 2>/dev/null \
  | python3 -c 'import sys,json; print(json.load(sys.stdin).get("release",""))' 2>/dev/null || true
