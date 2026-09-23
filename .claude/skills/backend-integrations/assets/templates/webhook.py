"""
Template de webhook recebido: apps/integrations/<provider>/  (dono: BE-05)

Separe em models.py / services.py / signature.py / views.py / tasks.py ao aplicar.

Fluxo: assinatura → schema → persistência idempotente → 2xx rápido → task → service do core.
Nada de trabalho pesado antes de responder: o provider tem timeout curto e
reenvia, gerando duplicidade.

Contratos da família (backend-core/references/contratos-entre-skills.md):
- WebhookEvent herda common.jobs.ProcessingStateModel (status/attempts/last_error/correlation_id);
- toda escrita em WebhookEvent passa pelos services deste módulo (nada de .objects.update solto);
- task: retry só para common.errors.TransientError; DomainError/PermanentError → failed sem retry;
- a rota é incluída pela BE-02 em /api/v1/webhooks/<provider>/.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time

from django.conf import settings
from django.db import IntegrityError, models, transaction
from django.db.models import F
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from common.errors import PermanentError, TransientError
from common.exceptions import DomainError
from common.jobs import ProcessingStateModel, ProcessingStatus
from common.logging import correlation_id

logger = logging.getLogger(__name__)

#: janela aceita entre o timestamp assinado e agora (anti-replay)
SIGNATURE_TOLERANCE_SECONDS = 300


# ===========================================================================
# models.py
# ===========================================================================


class WebhookEvent(ProcessingStateModel):
    """
    Registro de todo evento recebido (inbox). É o que permite deduplicar, auditar
    e reprocessar — os três problemas que aparecem depois de alguns meses.

    Status (common.jobs.ProcessingStatus):
      pending → processing → completed | failed | ignored
    created_at (BaseModel) = momento do recebimento; finished_at = fim do processamento.
    """

    provider = models.CharField(max_length=50)
    external_event_id = models.CharField(max_length=200)
    event_type = models.CharField(max_length=100)
    # guarde payload apenas se a política de dados permitir (PII!)
    payload = models.JSONField(null=True, blank=True)
    payload_hash = models.CharField(max_length=64)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "external_event_id"],
                name="uniq_webhook_provider_event",
            )
        ]
        indexes = [
            models.Index(fields=["provider", "status", "created_at"]),
        ]


# ===========================================================================
# services.py — únicas funções que escrevem em WebhookEvent
# ===========================================================================


def webhook_event_register(
    *, provider: str, external_event_id: str, event_type: str, payload: dict, raw_body: bytes
) -> WebhookEvent | None:
    """Persiste o evento. Devolve None se já era conhecido (dedupe pela constraint)."""
    try:
        with transaction.atomic():
            event = WebhookEvent.objects.create(
                provider=provider,
                external_event_id=external_event_id,
                event_type=event_type,
                payload=payload,
                payload_hash=hashlib.sha256(raw_body).hexdigest(),
                correlation_id=correlation_id.get() or "",
            )
    except IntegrityError:
        return None
    return event


@transaction.atomic
def webhook_event_start(*, event_id: int) -> WebhookEvent | None:
    """Marca processing. Devolve None se já terminou (task repetida é no-op)."""
    event = WebhookEvent.objects.select_for_update().get(pk=event_id)
    if event.status in {ProcessingStatus.COMPLETED, ProcessingStatus.IGNORED}:
        return None
    event.status = ProcessingStatus.PROCESSING
    event.attempts = F("attempts") + 1
    event.started_at = event.started_at or timezone.now()
    event.save(update_fields=["status", "attempts", "started_at", "updated_at"])
    event.refresh_from_db(fields=["attempts"])
    return event


def webhook_event_finish(*, event_id: int, status: str, error: str = "") -> None:
    event = WebhookEvent.objects.get(pk=event_id)
    event.status = status
    event.last_error = error[:2000]
    event.finished_at = timezone.now()
    event.save(update_fields=["status", "last_error", "finished_at", "updated_at"])


# ===========================================================================
# signature.py
# ===========================================================================


def verify_signature(
    *, raw_body: bytes, signature_header: str, timestamp_header: str, secret: str
) -> None:
    """
    Verifica HMAC sobre os BYTES ORIGINAIS do corpo.

    Reserializar o JSON antes de verificar quebra a assinatura: espaçamento e
    ordem de chave mudam. Leia request.body antes de qualquer parse.

    Ajuste o formato da string canônica ao que o provider documenta.
    """
    try:
        sent_at = int(timestamp_header)
    except (TypeError, ValueError):
        raise PermissionError("timestamp ausente ou inválido")

    if abs(time.time() - sent_at) > SIGNATURE_TOLERANCE_SECONDS:
        raise PermissionError("timestamp fora da janela aceita (replay)")

    signed_payload = f"{sent_at}.".encode() + raw_body
    expected = hmac.new(
        secret.encode(), signed_payload, hashlib.sha256
    ).hexdigest()

    # comparação em tempo constante: "==" vaza informação por timing
    if not hmac.compare_digest(expected, signature_header or ""):
        raise PermissionError("assinatura inválida")


# ===========================================================================
# views.py
# ===========================================================================


@csrf_exempt
@require_POST
def provider_webhook(request: HttpRequest) -> HttpResponse:
    """
    Endpoint público. Trate como entrada hostil: qualquer um pode chamar.

    Autenticação é a assinatura — não IP, não User-Agent, não URL secreta.
    """
    raw_body = request.body  # antes de qualquer parse

    try:
        verify_signature(
            raw_body=raw_body,
            signature_header=request.headers.get("X-Provider-Signature", ""),
            timestamp_header=request.headers.get("X-Provider-Timestamp", ""),
            secret=settings.PROVIDER_WEBHOOK_SECRET,
        )
    except PermissionError as exc:
        logger.warning(
            "webhook.rejected", extra={"provider": "provider", "reason": str(exc)}
        )
        return JsonResponse({"detail": "invalid signature"}, status=401)

    try:
        payload = json.loads(raw_body)
        external_event_id = payload["id"]
        event_type = payload["type"]
    except (ValueError, KeyError, TypeError):
        # 400 aqui: repetir não vai melhorar um payload malformado
        return JsonResponse({"detail": "invalid payload"}, status=400)

    # webhook_event_register faz o próprio atomic → ao retornar, o evento já está commitado.
    event = webhook_event_register(
        provider="provider",
        external_event_id=str(external_event_id),
        event_type=event_type,
        payload=payload,
        raw_body=raw_body,
    )

    # evento repetido → responde sucesso sem reprocessar.
    # Duplicidade é comportamento normal, não anomalia.
    if event is None:
        return JsonResponse({"status": "duplicate"}, status=200)

    # Adaptador de borda pode enfileirar a task direto (só o core usa dispatch()).
    process_webhook_event_task.delay(event_id=event.pk)
    return JsonResponse({"status": "accepted"}, status=202)


# ===========================================================================
# tasks.py (executado pela BE-03)
# ===========================================================================

from celery import shared_task  # noqa: E402


@shared_task(
    autoretry_for=(TransientError,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=8,
    ignore_result=True,
)
def process_webhook_event_task(*, event_id: int) -> None:
    """
    Processamento pesado vive aqui, não no handler HTTP.

    Idempotente: webhook_event_start devolve None se o evento já terminou, e o
    service do core recebe idempotency_key derivada do evento.
    """
    event = webhook_event_start(event_id=event_id)
    if event is None:
        return

    handler = WEBHOOK_HANDLERS.get(event.event_type)
    if handler is None:
        # evento que não nos interessa não é erro
        webhook_event_finish(event_id=event_id, status=ProcessingStatus.IGNORED)
        return

    try:
        # Não assuma ordem de chegada: o service decide com base no estado atual.
        handler(event)
    except TransientError as exc:
        webhook_event_finish(event_id=event_id, status=ProcessingStatus.FAILED, error=str(exc))
        raise  # autoretry_for reenfileira; webhook_event_start volta para processing
    except (DomainError, PermanentError) as exc:
        # Repetir não muda nada: registra e para. Reprocessamento é manual/operacional.
        webhook_event_finish(event_id=event_id, status=ProcessingStatus.FAILED, error=str(exc))
        logger.warning("webhook.failed", extra={"event_id": event_id, "error": str(exc)})
        return

    webhook_event_finish(event_id=event_id, status=ProcessingStatus.COMPLETED)


def handle_payment_succeeded(event: WebhookEvent) -> None:
    """Normaliza o payload e chama o service do core — a regra não mora aqui."""
    from apps.billing.services import payment_confirm  # service do core (BE-01)

    data = event.payload["data"]
    payment_confirm(
        actor=None,  # processo de sistema, documentado no service
        external_payment_id=str(data["id"]),
        idempotency_key=f"{event.provider}:{event.external_event_id}",
    )


WEBHOOK_HANDLERS = {
    "payment.succeeded": handle_payment_succeeded,
}
