"""apps/ai/services.py (+ runs.py, exceptions.py) — exemplo de AI Service completo.

Caminho inteiro: prompt versionado, chamada com timeout, validação por schema,
instrumentação em AIRun (via services, nunca métodos no model) e falha controlada.

Convenções da família:
- nome `<entidade>_<ação>` (message_classify); só kwargs; recebe `actor`;
- tenant sai do actor (tenant_id_of), nunca de parâmetro solto;
- erro de negócio de IA = DomainError com code MAIÚSCULO; falha de provider = AITransientError/AIPermanentError;
- NUNCA chamar dentro de transaction.atomic.
"""

import time
from decimal import Decimal

from django.conf import settings
from pydantic import ValidationError

from common.exceptions import BusinessRuleError
from common.logging import correlation_id
from common.permissions import require_perm
from common.tenancy import tenant_id_of

# ===========================================================================
# apps/ai/exceptions.py
# ===========================================================================
from apps.ai.providers.base import AIPermanentError


class AIOutputInvalid(AIPermanentError):
    """Modelo devolveu saída fora do schema (após a tentativa de reparo). API → 502."""

    code = "AI_OUTPUT_INVALID"


class AIBudgetExceeded(BusinessRuleError):
    code = "AI_BUDGET_EXCEEDED"
    default_message = "Limite de uso de IA atingido para este período."


class AIInsufficientContext(BusinessRuleError):
    code = "AI_INSUFFICIENT_CONTEXT"
    default_message = "Não há informação suficiente para responder."


# ===========================================================================
# apps/ai/runs.py — únicas funções que escrevem em AIRun
# ===========================================================================
from apps.ai.models import AIRun  # noqa: E402


def ai_run_start(*, use_case: str, actor, config: dict, prompt_version: str) -> AIRun:
    return AIRun.objects.create(
        use_case=use_case,
        tenant_id=getattr(actor, "tenant_id", None),
        actor=actor,
        provider=config["provider"],
        model=config["model"],
        prompt_version=prompt_version,
        correlation_id=correlation_id.get() or "",
    )


def ai_run_succeed(*, run: AIRun, response, latency_ms: int, estimated_cost: Decimal) -> None:
    run.status = AIRun.Status.SUCCEEDED
    run.input_tokens = response.input_tokens
    run.output_tokens = response.output_tokens
    run.latency_ms = latency_ms
    run.estimated_cost = estimated_cost
    run.save(update_fields=["status", "input_tokens", "output_tokens", "latency_ms", "estimated_cost", "updated_at"])


def ai_run_fail(*, run: AIRun, error_code: str, latency_ms: int) -> None:
    run.status = AIRun.Status.FAILED
    run.error_code = error_code
    run.latency_ms = latency_ms
    run.save(update_fields=["status", "error_code", "latency_ms", "updated_at"])


# ===========================================================================
# apps/ai/services.py
# ===========================================================================
from apps.ai.prompts import load_prompt  # noqa: E402
from apps.ai.providers.base import AITransientError, get_llm_provider  # noqa: E402
from apps.ai.schemas import MessageClassification  # noqa: E402

USE_CASE = "message_classify"
PROMPT_VERSION = "v2"


def message_classify(*, actor, text: str) -> MessageClassification:
    """Classifica uma mensagem. História: H-xxx.

    Permissão checada AQUI (não só na view): API, task e tool MCP passam pelo mesmo ponto.
    """
    require_perm(actor, "ai.use_message_classify")
    tenant_id_of(actor)  # falha fechado se o actor não tem tenant

    provider, config = get_llm_provider(USE_CASE)
    system_prompt = load_prompt(USE_CASE, PROMPT_VERSION)
    messages = [
        {"role": "system", "content": system_prompt},
        # Conteúdo do usuário entra como DADO, com fronteira explícita.
        {"role": "user", "content": f"DADOS DO USUÁRIO\n---\n{text}\n---"},
    ]

    started = time.monotonic()
    run = ai_run_start(use_case=USE_CASE, actor=actor, config=config, prompt_version=PROMPT_VERSION)

    try:
        response = provider.generate(
            messages=messages,
            model=config["model"],
            temperature=config.get("temperature", 0),
            max_output_tokens=config.get("max_output_tokens"),
            timeout=config["timeout"],
            response_schema=MessageClassification.model_json_schema(),
        )
    except AITransientError:
        ai_run_fail(run=run, error_code="AI_PROVIDER_UNAVAILABLE", latency_ms=_elapsed(started))
        raise  # task: autoretry_for=(TransientError,) · API: 503

    try:
        result = MessageClassification.model_validate_json(response.text)
    except ValidationError as exc:
        # Saída inválida é erro de aplicação, não motivo para salvar lixo.
        ai_run_fail(run=run, error_code=AIOutputInvalid.code, latency_ms=_elapsed(started))
        raise AIOutputInvalid(USE_CASE) from exc

    ai_run_succeed(
        run=run,
        response=response,
        latency_ms=_elapsed(started),
        estimated_cost=_estimate_cost(config, response),
    )
    return result


def _elapsed(started: float) -> int:
    return int((time.monotonic() - started) * 1000)


def _estimate_cost(config: dict, response) -> Decimal:
    """Preço por 1M tokens em settings.AI_PRICES; Decimal, nunca float."""
    prices = settings.AI_PRICES.get(config["model"], {})
    total = (
        Decimal(response.input_tokens or 0) * Decimal(str(prices.get("input", 0)))
        + Decimal(response.output_tokens or 0) * Decimal(str(prices.get("output", 0)))
    )
    return total / Decimal(1_000_000)
