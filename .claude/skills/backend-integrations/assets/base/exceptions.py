"""
apps/integrations/base/exceptions.py

Exceções de integração — ramo da hierarquia ÚNICA de falhas técnicas da família
(common/errors.py no backend-core):

    InfrastructureError
    ├── TransientError   (retryable)  ← IntegrationTimeout, IntegrationUnavailable, IntegrationRateLimited
    └── PermanentError                ← todas as demais

Consequências:
- task da BE-03 usa `autoretry_for=(TransientError,)` e já cobre integrações e IA;
- a API (BE-02) traduz TransientError → 503 e PermanentError → 502 sem vazar detalhe do provider;
- o domínio nunca importa httpx/requests/SDK — só estas classes (ou nem isso: o service
  pode capturar TransientError/PermanentError de common.errors).

Regra: exceção de SDK/biblioteca HTTP morre no client e sai daqui traduzida.
"""

from __future__ import annotations

from common.errors import InfrastructureError, PermanentError, TransientError


class IntegrationError(InfrastructureError):
    """Base de qualquer falha ao falar com sistema externo."""

    code = "INTEGRATION_ERROR"

    def __init__(
        self,
        message: str = "",
        *,
        provider: str | None = None,
        operation: str | None = None,
        status_code: int | None = None,
        retry_after: float | None = None,
        payload: object | None = None,
    ) -> None:
        super().__init__(message or self.__class__.__name__, retry_after=retry_after)
        self.provider = provider
        self.operation = operation
        self.status_code = status_code
        # Nunca coloque credencial aqui: este objeto costuma ir para log.
        self.payload = payload

    def __str__(self) -> str:
        parts = [super().__str__()]
        if self.provider:
            parts.append(f"provider={self.provider}")
        if self.operation:
            parts.append(f"operation={self.operation}")
        if self.status_code is not None:
            parts.append(f"status={self.status_code}")
        return " ".join(parts)


# ----------------------------------------------------------------- transitórias
class IntegrationTimeout(IntegrationError, TransientError):
    """Provider não respondeu dentro do timeout."""

    retryable = True
    code = "INTEGRATION_UNAVAILABLE"


class IntegrationUnavailable(IntegrationError, TransientError):
    """5xx, conexão recusada, DNS, provider fora do ar."""

    retryable = True
    code = "INTEGRATION_UNAVAILABLE"


class IntegrationRateLimited(IntegrationError, TransientError):
    """429. Respeite self.retry_after quando vier preenchido."""

    retryable = True
    code = "INTEGRATION_RATE_LIMITED"


# ------------------------------------------------------------------ permanentes
class IntegrationAuthenticationError(IntegrationError, PermanentError):
    """401 — credencial inválida, expirada ou ausente. Não repetir."""

    code = "INTEGRATION_AUTH_FAILED"


class IntegrationAuthorizationError(IntegrationError, PermanentError):
    """403 — credencial válida, mas sem permissão/escopo. Não repetir."""

    code = "INTEGRATION_FORBIDDEN"


class IntegrationValidationError(IntegrationError, PermanentError):
    """400/422 — a request está errada. Repetir devolve o mesmo erro."""

    code = "INTEGRATION_REJECTED"


class IntegrationConflict(IntegrationError, PermanentError):
    """409 — estado conflitante no provider (ex.: recurso já existe)."""

    code = "INTEGRATION_CONFLICT"


class IntegrationInvalidResponse(IntegrationError, PermanentError):
    """
    Resposta sintaticamente ou semanticamente inesperada.

    Inclui HTTP 200 com JSON inválido, campo obrigatório ausente,
    tipo errado ou enum desconhecido.
    """

    code = "INTEGRATION_INVALID_RESPONSE"


class IntegrationNotFound(IntegrationError, PermanentError):
    """404 — recurso não existe no provider."""

    code = "INTEGRATION_NOT_FOUND"


class IntegrationDisabled(IntegrationError, PermanentError):
    """Integração desligada por configuração/feature flag."""

    code = "INTEGRATION_DISABLED"
