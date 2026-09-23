"""
apps/integrations/base/client.py

BaseHTTPClient: comunicação técnica padronizada com sistema externo.

Resolve de uma vez, para toda integração da casa:
  - timeout obrigatório e configurável por dimensão;
  - retry apenas de falha transitória, com teto;
  - backoff exponencial com jitter;
  - respeito ao header Retry-After em 429;
  - tradução de erro do provider para IntegrationError;
  - log sem segredo.

O que NÃO entra aqui: regra de negócio, modelo de domínio, mapeamento de campos.
Isso é responsabilidade do adapter.
"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any, Mapping

import httpx

from common.logging import correlation_id

from .exceptions import (
    IntegrationAuthenticationError,
    IntegrationAuthorizationError,
    IntegrationConflict,
    IntegrationError,
    IntegrationInvalidResponse,
    IntegrationNotFound,
    IntegrationRateLimited,
    IntegrationTimeout,
    IntegrationUnavailable,
    IntegrationValidationError,
)

logger = logging.getLogger(__name__)

#: cabeçalhos que nunca podem aparecer em log
SENSITIVE_HEADERS = frozenset(
    {
        "authorization",
        "proxy-authorization",
        "x-api-key",
        "api-key",
        "x-auth-token",
        "cookie",
        "set-cookie",
        "x-signature",
    }
)


def mask_headers(headers: Mapping[str, str]) -> dict[str, str]:
    """Versão dos headers segura para log."""
    return {
        key: ("***" if key.lower() in SENSITIVE_HEADERS else value)
        for key, value in headers.items()
    }


@dataclass(frozen=True)
class RetryPolicy:
    """
    Política de retry do client.

    Regra da família: UMA camada de retry.
      - Chamada dentro de task (BE-03): padrão max_attempts=1 — quem repete é a task
        (`autoretry_for=(TransientError,)`).
      - Chamada síncrona dentro de request da API: `RetryPolicy.for_request()`
        (2 tentativas, delays curtos), e só para operação idempotente.
    Escrita (POST/PATCH/PUT/DELETE) sem idempotency_key nunca é repetida pelo client.
    """

    max_attempts: int = 1
    base_delay: float = 1.0
    max_delay: float = 30.0
    jitter: float = 0.3  # fração do delay sorteada aleatoriamente
    retry_on_status: frozenset[int] = field(
        default_factory=lambda: frozenset({429, 502, 503, 504})
    )

    @classmethod
    def for_request(cls) -> "RetryPolicy":
        """Retry curto para chamada síncrona dentro de uma request HTTP."""
        return cls(max_attempts=2, base_delay=0.3, max_delay=2.0)

    def delay_for(self, attempt: int, *, retry_after: float | None = None) -> float:
        """Backoff exponencial com jitter. retry_after do provider tem precedência."""
        if retry_after is not None:
            return min(retry_after, self.max_delay)
        raw = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
        return raw * (1 + random.uniform(-self.jitter, self.jitter))


@dataclass(frozen=True)
class TimeoutPolicy:
    """
    Timeout por dimensão. Nenhum valor pode ser None.

    Perfis típicos:
      API rápida        → connect=3, read=5
      relatório remoto  → read=60
      upload            → write=120
    """

    connect: float = 3.0
    read: float = 10.0
    write: float = 10.0
    pool: float = 5.0

    def as_httpx(self) -> httpx.Timeout:
        return httpx.Timeout(
            connect=self.connect,
            read=self.read,
            write=self.write,
            pool=self.pool,
        )


class BaseHTTPClient:
    """
    Subclasse por integração. Exemplo em assets/templates/integration_module.py.

    Uso:
        class CRMClient(BaseHTTPClient):
            provider = "crm"

        client = CRMClient(
            base_url=settings.CRM_BASE_URL,
            auth_headers={"Authorization": f"Bearer {settings.CRM_API_KEY}"},
            timeout=TimeoutPolicy(read=15),
        )
        data = client.request("GET", "/customers", params={"page": 1})
    """

    #: nome curto usado em log, métrica e exceção
    provider: str = "unknown"

    def __init__(
        self,
        *,
        base_url: str,
        auth_headers: Mapping[str, str] | None = None,
        timeout: TimeoutPolicy | None = None,
        retry: RetryPolicy | None = None,
        default_headers: Mapping[str, str] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout or TimeoutPolicy()
        self.retry = retry or RetryPolicy()

        headers = {"Accept": "application/json"}
        headers.update(default_headers or {})
        headers.update(auth_headers or {})

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout.as_httpx(),
            follow_redirects=False,  # redirect externo é revalidado explicitamente
        )

    # ------------------------------------------------------------------ #
    # API pública
    # ------------------------------------------------------------------ #

    def request(
        self,
        method: str,
        path: str,
        *,
        operation: str | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
        content: bytes | None = None,
        headers: Mapping[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> Any:
        """
        Executa a chamada e devolve o JSON desserializado.

        idempotency_key precisa ser ESTÁVEL por operação de negócio
        (ex.: f"payment:{payment_id}:create"), nunca aleatória por tentativa —
        caso contrário o retry deixa de ser seguro para escrita.
        """
        operation = operation or f"{method} {path}"
        request_headers = dict(headers or {})
        if idempotency_key:
            request_headers["Idempotency-Key"] = idempotency_key
        # Propaga o correlation_id da família (app → API → task → provider).
        cid = correlation_id.get()
        if cid:
            request_headers.setdefault("X-Request-ID", cid)

        # Escrita sem chave de idempotência nunca é repetida pelo client.
        unsafe = method.upper() in {"POST", "PATCH", "PUT", "DELETE"} and not idempotency_key
        max_attempts = 1 if unsafe else self.retry.max_attempts

        response = self._request_with_retry(
            method=method,
            path=path,
            operation=operation,
            params=params,
            json=json,
            content=content,
            headers=request_headers,
            max_attempts=max_attempts,
        )
        return self._parse_json(response, operation=operation)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "BaseHTTPClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    # ------------------------------------------------------------------ #
    # Internos
    # ------------------------------------------------------------------ #

    def _request_with_retry(
        self,
        *,
        method: str,
        path: str,
        operation: str,
        params: Mapping[str, Any] | None,
        json: Any,
        content: bytes | None,
        headers: Mapping[str, str],
        max_attempts: int,
    ) -> httpx.Response:
        last_error: IntegrationError | None = None

        for attempt in range(1, max_attempts + 1):
            started = time.monotonic()
            try:
                response = self._client.request(
                    method,
                    path,
                    params=params,
                    json=json,
                    content=content,
                    headers=headers,
                )
            except httpx.TimeoutException as exc:
                last_error = IntegrationTimeout(
                    str(exc), provider=self.provider, operation=operation
                )
            except httpx.TransportError as exc:
                # conexão recusada, DNS, TLS, reset
                last_error = IntegrationUnavailable(
                    str(exc), provider=self.provider, operation=operation
                )
            else:
                duration_ms = int((time.monotonic() - started) * 1000)
                self._log(
                    operation=operation,
                    attempt=attempt,
                    status=response.status_code,
                    duration_ms=duration_ms,
                )

                if response.is_success:
                    return response

                error = self._translate_status(response, operation=operation)
                should_retry = (
                    error.retryable
                    and response.status_code in self.retry.retry_on_status
                    and attempt < max_attempts
                )
                if not should_retry:
                    raise error
                last_error = error

            # chegou aqui: falhou e pode haver nova tentativa
            if attempt >= max_attempts:
                break

            delay = self.retry.delay_for(
                attempt,
                retry_after=getattr(last_error, "retry_after", None),
            )
            logger.warning(
                "integration.retry",
                extra={
                    "provider": self.provider,
                    "operation": operation,
                    "attempt": attempt,
                    "delay_s": round(delay, 2),
                    "reason": type(last_error).__name__,
                },
            )
            time.sleep(delay)

        assert last_error is not None
        raise last_error

    def _translate_status(
        self, response: httpx.Response, *, operation: str
    ) -> IntegrationError:
        """Status HTTP → exceção da casa. Nunca trate 'não-200' como erro único."""
        status = response.status_code
        kwargs: dict[str, Any] = {
            "provider": self.provider,
            "operation": operation,
            "status_code": status,
        }
        body = self._safe_body_excerpt(response)

        if status == 401:
            return IntegrationAuthenticationError(body, **kwargs)
        if status == 403:
            return IntegrationAuthorizationError(body, **kwargs)
        if status == 404:
            return IntegrationNotFound(body, **kwargs)
        if status == 409:
            return IntegrationConflict(body, **kwargs)
        if status == 429:
            return IntegrationRateLimited(
                body, retry_after=self._retry_after(response), **kwargs
            )
        if 400 <= status < 500:
            return IntegrationValidationError(body, **kwargs)
        return IntegrationUnavailable(body, **kwargs)

    @staticmethod
    def _retry_after(response: httpx.Response) -> float | None:
        raw = response.headers.get("Retry-After")
        if not raw:
            return None
        try:
            return float(raw)
        except ValueError:
            # formato HTTP-date: trate conforme necessidade do provider
            return None

    def _parse_json(self, response: httpx.Response, *, operation: str) -> Any:
        """HTTP 200 não garante payload válido."""
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise IntegrationInvalidResponse(
                f"resposta não é JSON válido: {exc}",
                provider=self.provider,
                operation=operation,
                status_code=response.status_code,
            ) from exc

    @staticmethod
    def _safe_body_excerpt(response: httpx.Response, limit: int = 500) -> str:
        """Trecho curto do corpo para diagnóstico. Não use com payload sensível."""
        try:
            return response.text[:limit]
        except Exception:  # pragma: no cover - corpo binário/ilegível
            return "<corpo não legível>"

    def _log(
        self, *, operation: str, attempt: int, status: int, duration_ms: int
    ) -> None:
        logger.info(
            "integration.call",
            extra={
                "provider": self.provider,
                "operation": operation,
                "attempt": attempt,
                "status": status,
                "duration_ms": duration_ms,
            },
        )
