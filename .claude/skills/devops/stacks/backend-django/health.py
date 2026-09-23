"""
Health checks (BE-06).

config/health.py            → views health_live / health_ready (rotas em config/urls.py)
common/management/commands/worker_health.py → comando para o worker (ver fim do arquivo)

Regras:
- live  = o processo responde. Nunca toca banco. Usado por uptime externo e HEALTHCHECK do Docker.
- ready = dependências PRÓPRIAS ok (Postgres; Redis se houver fila). Nunca chama provider externo.
- sem autenticação, sem dado sensível (nada de versão de libs, host, stack).
- /health/ fora do SECURE_SSL_REDIRECT (SECURE_REDIRECT_EXEMPT), pois o check interno é HTTP.
"""

import logging
import os

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@never_cache
@require_GET
def health_live(request):
    return JsonResponse({"status": "ok", "release": os.getenv("RELEASE", "")})


@never_cache
@require_GET
def health_ready(request):
    checks: dict[str, str] = {}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception:  # noqa: BLE001 — health não pode estourar
        logger.exception("health.database_failed")
        checks["database"] = "fail"

    broker = getattr(settings, "CELERY_BROKER_URL", "")
    if broker.startswith("redis"):
        try:
            import redis

            redis.Redis.from_url(broker, socket_connect_timeout=2, socket_timeout=2).ping()
            checks["broker"] = "ok"
        except Exception:  # noqa: BLE001
            logger.exception("health.broker_failed")
            checks["broker"] = "fail"

    healthy = all(v == "ok" for v in checks.values())
    return JsonResponse(
        {
            "status": "ok" if healthy else "fail",
            "checks": checks,
            "release": os.getenv("RELEASE", ""),  # o smoke do pipeline confere este valor
            "env": os.getenv("APP_ENV", ""),
        },
        status=200 if healthy else 503,
    )


# ---------------------------------------------------------------------------
# config/urls.py
# ---------------------------------------------------------------------------
# path("health/live/", health_live),
# path("health/ready/", health_ready),


# ---------------------------------------------------------------------------
# common/management/commands/worker_health.py
#   Easypanel → serviço worker → healthcheck: python manage.py worker_health
# ---------------------------------------------------------------------------
from django.core.management.base import BaseCommand, CommandError  # noqa: E402


class Command(BaseCommand):
    help = "Falha se nenhum worker Celery responder ao ping (health do serviço worker)."

    def handle(self, *args, **options):
        from config.celery import app

        replies = app.control.inspect(timeout=3).ping() or {}
        if not replies:
            raise CommandError("nenhum worker respondeu")
        self.stdout.write(f"ok: {len(replies)} worker(s)")
