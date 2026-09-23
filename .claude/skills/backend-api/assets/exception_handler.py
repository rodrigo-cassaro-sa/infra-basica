"""
Handler central de exceções da API (BE-02) — config/api/exception_handler.py

Traduz exceções do core (BE-01), falhas de infraestrutura (common.errors) e erros
do DRF para o formato ÚNICO da família:

    {
      "error": {
        "code": "CUSTOMER_EMAIL_EXISTS",
        "message": "Já existe um cliente com este e-mail.",
        "fields": {"email": ["E-mail já cadastrado."]},
        "details": {}
      }
    }

Regras:
- NÃO redefine DomainError & cia. Importa de common.exceptions (fonte única).
- O status HTTP é decidido pela CATEGORIA (classe-mãe), nunca guardado na exceção.
- 400 = formato inválido (serializer). 422 = formato ok, domínio recusou.

Registro:
    REST_FRAMEWORK = {"EXCEPTION_HANDLER": "config.api.exception_handler.api_exception_handler"}
"""

import logging

from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from common.errors import PermanentError, TransientError
from common.exceptions import (
    BusinessRuleError,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
)
from common.exceptions import ValidationError as DomainValidationError

logger = logging.getLogger(__name__)

# Ordem importa: da categoria mais específica para a mais genérica.
DOMAIN_STATUS: tuple[tuple[type[DomainError], int], ...] = (
    (NotFoundError, status.HTTP_404_NOT_FOUND),
    (PermissionDeniedError, status.HTTP_403_FORBIDDEN),
    (DomainValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY),
    (ConflictError, status.HTTP_409_CONFLICT),
    (BusinessRuleError, status.HTTP_422_UNPROCESSABLE_ENTITY),
    (DomainError, status.HTTP_400_BAD_REQUEST),
)


def error_payload(*, code: str, message: str, fields=None, details=None) -> dict:
    return {"error": {"code": code, "message": message, "fields": fields or {}, "details": details or {}}}


def _status_for(exc: DomainError) -> int:
    for klass, http_status in DOMAIN_STATUS:
        if isinstance(exc, klass):
            return http_status
    return status.HTTP_400_BAD_REQUEST


def api_exception_handler(exc, context):
    # 1) Erro de domínio (esperado): categoria → status, corpo = to_dict().
    if isinstance(exc, DjangoValidationError):
        exc = DomainValidationError.from_django(exc)  # full_clean que escapou do service

    if isinstance(exc, DomainError):
        http_status = _status_for(exc)
        logger.info("api.domain_error", extra={"code": exc.code, "status": http_status})
        return Response({"error": exc.to_dict()}, status=http_status)

    # 2) Falha técnica de provider/IA: nunca vazar detalhe do terceiro.
    if isinstance(exc, TransientError):
        logger.warning("api.transient_error", extra={"code": exc.code, "error": str(exc)})
        response = Response(
            error_payload(code=exc.code, message="Serviço temporariamente indisponível. Tente novamente."),
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        if exc.retry_after:
            response["Retry-After"] = str(int(exc.retry_after))
        return response

    if isinstance(exc, PermanentError):
        logger.error("api.permanent_error", extra={"code": exc.code, "error": str(exc)})
        return Response(
            error_payload(code=exc.code, message="Falha ao comunicar com serviço externo."),
            status=status.HTTP_502_BAD_GATEWAY,
        )

    # 3) Erros do Django/DRF (autenticação, formato, throttling...).
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = drf_exception_handler(exc, context)

    if response is None:
        # Exceção não tratada: sem stacktrace nem mensagem interna para o cliente.
        # O correlation_id entra no log pelo filtro de common/logging.py.
        logger.exception("api.unhandled_error")
        return Response(
            error_payload(code="INTERNAL_ERROR", message="Erro interno."),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    response.data = _normalize_drf_error(exc, response)
    return response


_DEFAULT_CODES = {
    400: "VALIDATION_ERROR",
    401: "NOT_AUTHENTICATED",
    403: "PERMISSION_DENIED",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    415: "UNSUPPORTED_MEDIA_TYPE",
    429: "THROTTLED",
}


def _normalize_drf_error(exc, response) -> dict:
    code = _DEFAULT_CODES.get(response.status_code, "ERROR")
    fields: dict = {}
    details: dict = {}
    message = "Requisição inválida."

    # Token expirado/inválido (simplejwt) → code específico para o Expo renovar o token.
    if getattr(exc, "default_code", None) == "token_not_valid":
        code = "TOKEN_INVALID"

    detail = getattr(exc, "detail", None)
    if isinstance(detail, dict) and response.status_code == 400:
        fields = {key: _as_list(value) for key, value in detail.items()}
        message = "Alguns campos estão inválidos."
    elif isinstance(detail, dict):
        message = str(detail.get("detail", message))  # ex.: 401 do simplejwt
    elif isinstance(detail, (list, str)):
        message = " ".join(_as_list(detail))

    wait = getattr(exc, "wait", None)
    if wait:
        details["retry_after"] = int(wait)

    return error_payload(code=code, message=message, fields=fields, details=details)


def _as_list(value):
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    return [str(value)]
