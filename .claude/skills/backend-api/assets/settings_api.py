"""
Configuração base da camada de API (BE-02).

Importe/cole no settings do projeto. Os defaults aqui implementam as decisões
padrão da casa: negar por padrão, paginar sempre, erro em formato único,
OpenAPI fiel e CORS restrito por ambiente.
"""

import os
from datetime import timedelta

# Apps e middlewares da camada de API (somar aos de config/settings/base.py do core).
API_APPS = [
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",  # logout/rotação de refresh
    "django_filters",
    "drf_spectacular",
    "corsheaders",
]
API_MIDDLEWARE_TOP = [
    "corsheaders.middleware.CorsMiddleware",          # o mais alto possível
    "config.api.middleware.CorrelationIdMiddleware",  # define correlation_id (X-Request-ID)
]
# Em base.py:
#   INSTALLED_APPS += API_APPS
#   MIDDLEWARE = [MIDDLEWARE[0], *API_MIDDLEWARE_TOP, *MIDDLEWARE[1:]]  # depois do SecurityMiddleware

REST_FRAMEWORK = {
    # Autenticação global: JWT, porque o consumidor é o Expo (iOS/Android/web).
    # Detalhes (refresh, rotação, logout, SecureStore): references/autenticacao.md
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    # Negar por padrão: endpoint público é exceção explícita com AllowAny.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # Nenhuma lista sem paginação.
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
    # Formato único de erro.
    "EXCEPTION_HANDLER": "config.api.exception_handler.api_exception_handler",
    # Schema fiel ao comportamento real.
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "login": "5/min",
        "password_reset": "5/hour",
        "signup": "10/hour",
        "public": "60/min",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    # Claims extras (tenant) são adicionadas no serializer de token — ver autenticacao.md
}

SPECTACULAR_SETTINGS = {
    "TITLE": "API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,  # separa serializer de entrada e saída no schema
    "SCHEMA_PATH_PREFIX": "/api/v[0-9]",
    # Nomes estáveis de enum no schema → tipos TS estáveis no Expo (orval/openapi-typescript).
    "ENUM_NAME_OVERRIDES": {},
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
}

# CORS restrito por ambiente: apenas as origens que realmente consomem a API.
CORS_ALLOWED_ORIGINS = [
    origin
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin
]
# JWT no header Authorization → não precisa de cookie cross-site.
CORS_ALLOW_CREDENTIALS = False
CORS_EXPOSE_HEADERS = ["X-Request-ID", "Retry-After"]
# App nativo (iOS/Android) não envia Origin/CORS; CORS só importa para o Expo web.

# Sessão/cookie só no Django Admin → CSRF continua ligado para ele.
CSRF_TRUSTED_ORIGINS = [
    origin
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin
]

# Limite explícito de upload: rejeitar antes de processar.
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
