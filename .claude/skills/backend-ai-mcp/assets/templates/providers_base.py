"""apps/ai/providers/base.py

Contrato interno de provider de IA (dono: BE-04). O código de IA importa daqui —
nunca do SDK. O domínio (core) nem isso: chama AI services.

Erros pendurados na hierarquia ÚNICA de falhas técnicas da família (common/errors.py):
    AITransientError  → TransientError  (task da BE-03 faz retry; API responde 503)
    AIPermanentError  → PermanentError  (sem retry; API responde 502)
"""

from dataclasses import dataclass
from functools import cache
from typing import Protocol

from django.conf import settings
from django.utils.module_loading import import_string

from common.errors import InfrastructureError, PermanentError, TransientError


class AIProviderError(InfrastructureError):
    """Erro de provider já traduzido para o vocabulário da aplicação."""

    code = "AI_PROVIDER_ERROR"


class AITransientError(AIProviderError, TransientError):
    """Timeout, 429, 502, 503, falha de conexão. Elegível a retry."""

    retryable = True
    code = "AI_PROVIDER_UNAVAILABLE"


class AIPermanentError(AIProviderError, PermanentError):
    """Prompt inválido, schema incompatível, credencial inválida. Não repetir."""

    code = "AI_PROVIDER_REJECTED"


@dataclass(frozen=True)
class LLMResponse:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    model: str = ""
    provider: str = ""


class LLMProvider(Protocol):
    def generate(
        self,
        *,
        messages: list[dict],
        model: str,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        timeout: float,
        response_schema: dict | None = None,
    ) -> LLMResponse:
        ...


class EmbeddingProvider(Protocol):
    def embed(self, *, texts: list[str], model: str, timeout: float) -> list[list[float]]:
        ...


# ---------------------------------------------------------------------------
# Resolução por settings — mesmo princípio do settings.PORTS do core, com um nível
# a mais porque cada caso de uso escolhe seu provider/modelo:
#
#   AI_PROVIDERS = {                       # nome → implementação (dotted path)
#       "anthropic": "apps.ai.providers.anthropic.AnthropicProvider",
#       "openai": "apps.ai.providers.openai.OpenAIProvider",
#   }
#   AI_MODELS = {                          # caso de uso → provider + modelo + limites
#       "message_classify": {"provider": "anthropic", "model": "...", "timeout": 20, "temperature": 0},
#   }
#   settings/test.py: AI_PROVIDERS = {"anthropic": "apps.ai.tests.fakes.FakeLLMProvider", ...}
# ---------------------------------------------------------------------------


@cache
def _provider_class(dotted: str) -> type:
    return import_string(dotted)


def get_llm_provider(use_case: str) -> tuple[LLMProvider, dict]:
    """Resolve provider + config do caso de uso. Nunca instancie SDK fora do adapter."""
    try:
        config = settings.AI_MODELS[use_case]
        dotted = settings.AI_PROVIDERS[config["provider"]]
    except KeyError as exc:
        raise AIPermanentError(f"caso de uso/provider não configurado: {exc}") from None
    return _provider_class(dotted)(), config
