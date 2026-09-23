#!/bin/sh
# Gera a configuração de runtime do web a partir das envs do serviço (EasyPanel).
# Só valores PÚBLICOS: tudo aqui é lido pelo navegador. Segredo nunca.
set -eu

: "${API_URL:?defina API_URL (ex.: https://api.hom.produto.com.br)}"
: "${APP_ENV:?defina APP_ENV (hom | prod)}"

esc() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

cat > /srv/config.js <<JS
window.__APP_CONFIG__ = {
  apiUrl: "$(esc "$API_URL")",
  appEnv: "$(esc "$APP_ENV")",
  sentryDsn: "$(esc "${SENTRY_DSN_WEB:-}")",
  release: "$(esc "${RELEASE:-dev}")"
};
JS

cat > /srv/health.json <<JSON
{"status":"ok","release":"$(esc "${RELEASE:-dev}")","env":"$(esc "$APP_ENV")"}
JSON

exec "$@"
