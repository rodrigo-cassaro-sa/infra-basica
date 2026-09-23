#!/bin/sh
# docker/entrypoint.sh — chmod +x. Papel definido por ROLE (web | asgi | worker | beat | manage).
set -eu

ROLE="${ROLE:-web}"

case "$ROLE" in
  web)
    if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
      echo "entrypoint: migrate"
      python manage.py migrate --noinput
    fi
    exec gunicorn config.wsgi:application -c /app/docker/gunicorn.conf.py
    ;;
  asgi)
    # só se o projeto usa SSE/streaming de IA (BE-04); exige "uvicorn" no pyproject
    if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
      python manage.py migrate --noinput
    fi
    exec gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -c /app/docker/gunicorn.conf.py
    ;;
  worker)
    exec celery -A config worker -l "${LOG_LEVEL:-INFO}" \
      -Q "${CELERY_QUEUES:-default}" \
      --concurrency "${CELERY_CONCURRENCY:-2}" \
      --max-tasks-per-child "${CELERY_MAX_TASKS_PER_CHILD:-200}" \
      --without-gossip --without-mingle
    ;;
  beat)
    # UMA réplica. Com django-celery-beat, CELERY_BEAT_ARGS="--scheduler django_celery_beat.schedulers:DatabaseScheduler"
    # shellcheck disable=SC2086
    exec celery -A config beat -l "${LOG_LEVEL:-INFO}" ${CELERY_BEAT_ARGS:-}
    ;;
  dev)
    # DEV remoto com recarga automatica: o codigo vem do workspace montado
    # (o mesmo que o code-server edita), as dependencias continuam vindo da
    # imagem. Salvar um .py reflete na API em segundos, sem deploy.
    CODIGO="${CODE_DIR:-/workspace/project/backend}"
    if [ ! -f "$CODIGO/manage.py" ]; then
      echo "entrypoint: $CODIGO sem manage.py (o code-server ja clonou o repositorio?)."
      echo "entrypoint: caindo para o codigo da imagem, sem recarga automatica."
      CODIGO=/app
    fi
    cd "$CODIGO"
    echo "entrypoint: dev, codigo em $CODIGO"
    if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
      echo "entrypoint: migrate"
      python manage.py migrate --noinput
    fi
    # --insecure serve os estaticos com DEBUG=False. O dominio e publico:
    # DEBUG continua desligado para nao expor traceback nem SQL.
    exec python manage.py runserver 0.0.0.0:8000 --insecure
    ;;
  manage)
    # uso: docker run -e ROLE=manage imagem createsuperuser
    exec python manage.py "$@"
    ;;
  *)
    echo "ROLE inválido: $ROLE" >&2
    exit 1
    ;;
esac
