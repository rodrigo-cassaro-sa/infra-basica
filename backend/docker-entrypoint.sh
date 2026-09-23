#!/bin/sh
# RUN_MODE=dev    → código do workspace do Code Server, runserver com autoreload.
# RUN_MODE=server → código da imagem (branch), gunicorn.
set -eu

if [ "${RUN_MODE:-server}" = "dev" ]; then
  cd /workspace/backend
  python manage.py migrate --noinput
  exec python manage.py runserver 0.0.0.0:8000
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-60}"
