"""
Trecho a COLAR NO FIM de config/settings/production.py (usado por hom E prod) (o do backend-core já faz
`from .base import *`, HSTS, cookies seguros e LOGGING JSON). Não substitui aquele arquivo.
"""

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

# ---------------------------------------------------------------- ambiente
# Obrigatória (sem default): hom sem APP_ENV não pode "virar prod" e falar com cliente real.
APP_ENV = env("APP_ENV")  # noqa: F405 — hom | prod; hom e prod usam ESTE arquivo
if APP_ENV not in {"hom", "prod"}:
    raise RuntimeError(f"APP_ENV inválido para production.py: {APP_ENV!r} (use hom ou prod)")
# hom: destinos permitidos para e-mail/WhatsApp/SMS/push (vazio = sem restrição, só em prod)
OUTBOUND_ALLOWLIST = env.list("OUTBOUND_ALLOWLIST", default=[])  # noqa: F405
if APP_ENV != "prod" and not OUTBOUND_ALLOWLIST:
    raise RuntimeError("OUTBOUND_ALLOWLIST obrigatória fora de prod (hom não fala com cliente real)")

# ---------------------------------------------------------------- estáticos
# Só o Django Admin/DRF browsable usam estáticos (o frontend é o Expo).
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405 — logo após SecurityMiddleware
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},  # arquivos de usuário: MinIO (BE-05)
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# ---------------------------------------------------------------- HTTPS (SECURE_PROXY_SSL_HEADER já está no core)
SECURE_REDIRECT_EXEMPT = [r"^health/"]  # health check interno do Easypanel é HTTP

# ---------------------------------------------------------------- cache (Redis DB 1; broker usa DB 0)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_CACHE_URL", default="redis://redis:6379/1"),  # noqa: F405
        "KEY_PREFIX": env("CACHE_KEY_PREFIX", default="app"),  # noqa: F405
        "TIMEOUT": 300,
        "OPTIONS": {
            "SOCKET_CONNECT_TIMEOUT": 2,
            "SOCKET_TIMEOUT": 2,
            "IGNORE_EXCEPTIONS": True,  # cache fora do ar não derruba o sistema
        },
    }
}
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True

# ---------------------------------------------------------------- Sentry
SENTRY_DSN = env("SENTRY_DSN", default="")  # noqa: F405
if SENTRY_DSN:
    from common.logging import correlation_id

    def _tag_correlation(event, hint):
        cid = correlation_id.get()
        if cid:
            event.setdefault("tags", {})["correlation_id"] = cid
        return event

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=APP_ENV,
        release=env("RELEASE", default=None),  # noqa: F405 — tree hash embutido na imagem
        integrations=[DjangoIntegration(), CeleryIntegration(monitor_beat_tasks=True)],
        send_default_pii=False,  # LGPD: sem IP, cookie, corpo de request
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.05),  # noqa: F405
        before_send=_tag_correlation,
    )

# ---------------------------------------------------------------- Celery (BE-03)
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="")  # noqa: F405
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_WORKER_CANCEL_LONG_RUNNING_TASKS_ON_CONNECTION_LOSS = True
