# Estrutura e configuração do projeto

Sumário: 1. Árvore · 2. pyproject.toml · 3. Settings · 4. .env.example · 5. Postgres local · 6. Logging · 7. common/ · 8. Comandos

---

## 1. Árvore padrão

```text
backend/
├── manage.py
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── docker-compose.dev.yml
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── test.py
│   │   └── production.py
│   ├── urls.py          # só admin + include da backend-api
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── __init__.py
│   ├── accounts/        # User customizado, papéis
│   ├── tenants/         # só em projeto multi-tenant (Tenant)
│   ├── <dominio>/       # criado com scripts/novo_modulo.py
│   ├── jobs/            # backend-async (CeleryEventBus, jobs genéricos)   — quando houver
│   ├── integrations/    # backend-integrations (base/, <provider>/, webhooks) — quando houver
│   ├── ai/  mcp/        # backend-ai-mcp — quando houver
│   └── ...
├── common/
│   ├── __init__.py
│   ├── models.py        # BaseModel, AuditedModel
│   ├── exceptions.py    # hierarquia DomainError
│   ├── permissions.py   # require_perm
│   ├── validators.py    # CPF, CNPJ, telefone BR...
│   ├── errors.py        # TransientError / PermanentError (falha técnica)
│   ├── ports.py         # get_port() + settings.PORTS
│   ├── events.py        # dispatch() + InMemoryEventBus
│   ├── jobs.py          # ProcessingStateModel, ProcessingStatus, ProgressMixin
│   ├── tenancy.py       # TenantModel, tenant_id_of, scope_to_tenant (multi-tenant)
│   └── logging.py       # correlation_id (ContextVar) + filtro + JSON
└── tests/
    ├── conftest.py
    └── factories.py     # factories compartilhadas (User)
```

Cada app em `apps/<nome>/apps.py` usa `name = "apps.<nome>"` e `label = "<nome>"`
(o label curto define o prefixo das permissões: `sales.approve_order`).

---

## 2. pyproject.toml

```toml
[project]
name = "backend"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "django>=5.2,<5.3",
    "psycopg[binary,pool]>=3.2",
    "django-environ>=0.11",
    # --- backend-api (BE-02) ---
    "djangorestframework>=3.16",
    "djangorestframework-simplejwt>=5.5",
    "drf-spectacular>=0.28",
    "django-filter>=25.1",
    "django-cors-headers>=4.7",
    # --- backend-async (BE-03): descomentar quando houver fila ---
    # "celery[redis]>=5.5",
    # "django-celery-beat>=2.8",
    # --- backend-integrations (BE-05) ---
    # "httpx>=0.28",
    # "pydantic>=2.11",
    # "boto3>=1.38",           # MinIO/S3
    # --- backend-ai-mcp (BE-04) ---
    # "pgvector>=0.4",
    # "mcp>=1.9",
    # --- devops (OPS-01, stacks/backend-django) ---
    "gunicorn>=23",
    "whitenoise>=6.9",
    "django-redis>=6.0",
    "sentry-sdk[django,celery]>=2.29",
    # "uvicorn>=0.35",         # só com ROLE=asgi (SSE/streaming de IA)
]

[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-django>=4.9",
    "pytest-cov>=5",
    "factory-boy>=3.3",
    "ruff>=0.6",
    "pre-commit>=3.8",
    "django-debug-toolbar>=4.4",
    "django-stubs[compatible-mypy]>=5.1",
    "respx>=0.22",             # testes de integração HTTP (BE-05)
]

[tool.ruff]
line-length = 110
target-version = "py313"
extend-exclude = ["**/migrations/*"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "DJ", "S", "SIM", "RUF", "T20"]
ignore = ["RUF012"]  # atributos mutáveis de classe são padrão em Meta do Django

[tool.ruff.lint.per-file-ignores]
"**/tests/**" = ["S101", "S106"]

[tool.ruff.lint.isort]
known-first-party = ["apps", "common", "config"]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
python_files = ["test_*.py"]
addopts = "--reuse-db -ra --strict-markers"

[tool.coverage.run]
source = ["apps", "common"]
omit = ["**/migrations/*", "**/tests/*"]
```

**Dono do `pyproject.toml` é o core.** As outras skills não criam arquivo de dependências
próprio: descomentam o bloco delas aqui. Versões mínimas acima são o piso da casa em set/2026;
o `uv.lock` fixa o exato.

`T20` do Ruff proíbe `print()`; `S` pega segredos hardcoded; `DJ` pega antipadrões Django.

---

## 3. Settings

### config/settings/base.py

```python
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

SECRET_KEY = env("DJANGO_SECRET_KEY")
# dev | hom | prod — hom e prod usam production.py; só a env muda (skill devops)
APP_ENV = env("APP_ENV", default="dev")
DEBUG = False
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
]
LOCAL_APPS = [
    "apps.accounts",
    # "apps.<dominio>",
]
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = False  # transação é do service
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

from common.logging import build_logging  # noqa: E402

LOGGING = build_logging(json=False, level=env("LOG_LEVEL", default="INFO"))

# Ports: o core pede, as outras skills implementam (ver contratos-entre-skills.md).
PORTS: dict[str, str] = {
    "event_bus": "apps.jobs.bus.CeleryEventBus",  # backend-async; sem fila → "common.events.InMemoryEventBus"
    # "payment_gateway": "apps.integrations.asaas.adapter.AsaasPaymentGateway",
    # providers de IA: settings.AI_PROVIDERS / AI_MODELS (backend-ai-mcp)
}
```

> Pool de conexões nativo (Django 5.1+): em ASGI ou com muitos workers, trocar
> `CONN_MAX_AGE` por `DATABASES["default"]["OPTIONS"] = {"pool": True}` e definir
> `CONN_MAX_AGE = 0` (os dois não convivem). Alternativa: PgBouncer no Easypanel/Traefik stack.

### config/settings/local.py

```python
from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
INTERNAL_IPS = ["127.0.0.1"]
```

### config/settings/test.py

```python
from .base import *  # noqa: F403

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # só teste: rápido
PORTS = {  # noqa: F405 — fakes: o core nunca depende de rede nem de fila em teste
    **PORTS,  # noqa: F405
    "event_bus": "common.events.InMemoryEventBus",
}
LOGGING = build_logging(json=False, level="WARNING")  # noqa: F405
```

Teste roda contra **PostgreSQL** (mesmo `DATABASE_URL`, o pytest-django cria `test_<nome>`).

### config/settings/production.py

```python
from .base import *  # noqa: F403

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")  # noqa: F405 — obrigatório
# O HEALTHCHECK do container chama 127.0.0.1 de dentro dele; sem isto o
# Django responde DisallowedHost e o container nunca fica healthy.
ALLOWED_HOSTS += ["127.0.0.1", "localhost"]
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])  # noqa: F405

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # atrás do Traefik
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True

LOGGING = build_logging(json=True, level=env("LOG_LEVEL", default="INFO"))  # noqa: F405
```

`DJANGO_SETTINGS_MODULE`: `config.settings.local` no dev (definir no `manage.py`),
`config.settings.production` via env no container.

---

## 4. .env.example

```dotenv
# Copie para .env — NUNCA versionar o .env
DJANGO_SETTINGS_MODULE=config.settings.local
DJANGO_SECRET_KEY=troque-por-uma-chave-longa-aleatoria
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://app:app@localhost:5432/app
LOG_LEVEL=INFO
# produção
# DJANGO_CSRF_TRUSTED_ORIGINS=https://api.exemplo.com.br
```

Gerar chave: `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`.

`.gitignore` mínimo: `.env`, `.venv/`, `__pycache__/`, `staticfiles/`, `.coverage`, `htmlcov/`.

---

## 5. Postgres local — docker-compose.dev.yml

> Só o Postgres, para começar rápido. Stack completa (web, worker, beat, redis, minio) e
> Dockerfile de hom/prod: skill **devops** (`stacks/backend-django/`).

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      retries: 10
volumes:
  pgdata:
```

O usuário `app` precisa de `CREATEDB` para o banco de teste (o superusuário do container já tem).

---

## 6. Logging — common/logging.py

```python
import json
import logging
from contextvars import ContextVar

correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)

SENSITIVE_KEYS = {"password", "senha", "token", "authorization", "cookie", "api_key", "secret", "cpf"}


class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id.get() or "-"
        return True


class JsonFormatter(logging.Formatter):
    RESERVED = set(vars(logging.makeLogRecord({})).keys()) | {"message", "correlation_id"}

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "-"),
        }
        for key, value in vars(record).items():
            if key in self.RESERVED:
                continue
            payload[key] = "***" if key.lower() in SENSITIVE_KEYS else value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=False)


def build_logging(*, json: bool, level: str = "INFO") -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {"correlation": {"()": "common.logging.CorrelationIdFilter"}},
        "formatters": {
            "json": {"()": "common.logging.JsonFormatter"},
            "plain": {"format": "%(asctime)s %(levelname)s [%(correlation_id)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "filters": ["correlation"],
                "formatter": "json" if json else "plain",
            }
        },
        "root": {"handlers": ["console"], "level": level},
        "loggers": {
            "django.db.backends": {"level": "WARNING"},
            "apps": {"level": level, "propagate": True},
        },
    }
```

Uso no domínio: `logger.info("order.approved", extra={"order_id": order.pk})` — mensagem
curta tipo evento (`entidade.ação`) + contexto em `extra`. Quem define `correlation_id.set(...)`
é a camada de entrada: `CorrelationIdMiddleware` da backend-api (header `X-Request-ID`) e o
signal `before_task_publish`/`task_prerun` da backend-async. Nome único em todas as skills:
`correlation_id` (nunca `request_id` como campo de log).

---

## 7. common/ — regras

- Só o que é **realmente** compartilhado por 2+ apps/skills: base models, exceções, erros de infraestrutura, ports, events, jobs, tenancy, permissões, validadores BR, logging.
- Regra de vendas fica em `apps/sales/`, mesmo que "pareça utilitária".
- Proibido `common/utils.py` catch-all. Se precisar, `common/utils/<assunto>.py`.

## 8. Comandos do dia a dia

```bash
docker compose -f docker-compose.dev.yml up -d
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run pytest
uv run ruff check . --fix && uv run ruff format .
uv run python manage.py makemigrations --check --dry-run
DJANGO_SETTINGS_MODULE=config.settings.production uv run python manage.py check --deploy
```
