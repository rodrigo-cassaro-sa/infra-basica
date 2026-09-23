# syntax=docker/dockerfile:1.7
# Imagem ÚNICA para web, worker e beat (papel via ROLE) e para hom e prod (diferença só em env).
# Build: docker buildx build --build-arg RELEASE=$(git rev-parse HEAD:backend) backend/

# ---------- build ----------
FROM python:3.13-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app

# Dependências primeiro (camada cacheada enquanto o lock não muda)
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev

# collectstatic no build: não precisa de banco nem de segredo real
RUN DJANGO_SETTINGS_MODULE=config.settings.production APP_ENV=prod \
    DJANGO_SECRET_KEY=build-only DJANGO_ALLOWED_HOSTS=localhost \
    DATABASE_URL=postgres://x:x@localhost:5432/x \
    /app/.venv/bin/python manage.py collectstatic --noinput

# ---------- runtime ----------
FROM python:3.13-slim AS runtime
# Identidade do artefato (tree hash de backend/). Vai para /health e Sentry.
# É intrínseco à imagem, por isso a MESMA imagem vale para hom e prod.
ARG RELEASE=dev
ENV RELEASE=$RELEASE \
    PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.production
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r app && useradd -r -g app -d /app app
WORKDIR /app
COPY --from=build --chown=app:app /app /app
USER app

EXPOSE 8000
# Só o papel web responde HTTP; worker/beat têm health próprio (worker_health)
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD [ "sh", "-c", "case \"${ROLE:-web}\" in web|dev) curl -fsS http://127.0.0.1:8000/health/live/ >/dev/null ;; *) true ;; esac" ]
ENTRYPOINT ["/app/docker/entrypoint.sh"]
