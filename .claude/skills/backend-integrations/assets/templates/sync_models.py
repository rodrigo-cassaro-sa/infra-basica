"""
Template: apps/integrations/base/models.py

Três estruturas que quase toda integração acaba precisando:
  - ExternalMapping  → ligação interno ↔ externo sem poluir o domínio
  - SyncState        → checkpoint e status, exposto ao app Expo via API
  - OutgoingWebhook  → webhooks que nós enviamos (usa o outbox da BE-03 para disparar)

Bases comuns da família (backend-core):
  - common.models.BaseModel           → created_at/updated_at
  - common.jobs.ProcessingStateModel  → status/attempts/started_at/finished_at/last_error/correlation_id
  - common.tenancy.TenantModel        → em projeto multi-tenant, trocar a base e incluir
                                        "tenant" nas UniqueConstraints (credencial por tenant!)

Escrita nesses models só por funções de service do módulo de integração.
"""

from __future__ import annotations

from django.db import models

from common.jobs import ProcessingStateModel
from common.models import BaseModel


class ExternalMapping(BaseModel):
    """
    Evita `Customer.stripe_customer_id`, `Customer.hubspot_id`,
    `Customer.erp_code`... espalhados pelo model de domínio.

    Vale a pena quando há mais de um provider ou mais de um tipo de entidade.
    Com um provider só e sem previsão de mudança, um campo direto é aceitável.
    """

    provider = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=50)  # "customer", "invoice"...
    internal_id = models.CharField(max_length=64)
    external_id = models.CharField(max_length=200)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "entity_type", "external_id"],
                name="uniq_mapping_provider_entity_external",
            ),
            models.UniqueConstraint(
                fields=["provider", "entity_type", "internal_id"],
                name="uniq_mapping_provider_entity_internal",
            ),
        ]
        indexes = [models.Index(fields=["provider", "entity_type"])]


class SyncState(ProcessingStateModel):
    """
    Checkpoint de sincronização longa + estado visível para operação.

    Status = common.jobs.ProcessingStatus (pending/processing/completed/failed/canceled).
    Sem checkpoint, qualquer falha na página 4.700 reinicia do zero e na
    prática a importação nunca termina.
    """

    provider = models.CharField(max_length=50)
    resource = models.CharField(max_length=50)  # "contacts", "invoices"...

    # checkpoint — preencha o que o provider oferecer
    last_cursor = models.CharField(max_length=500, blank=True, default="")
    last_external_id = models.CharField(max_length=200, blank=True, default="")
    last_updated_at = models.DateTimeField(null=True, blank=True)
    last_page = models.PositiveIntegerField(null=True, blank=True)

    # operação / app
    last_synced_at = models.DateTimeField(null=True, blank=True)
    records_processed = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "resource"], name="uniq_syncstate_provider_resource"
            )
        ]


class OutgoingWebhook(ProcessingStateModel):
    """
    Webhooks que enviamos. Persistir antes de enviar é o que impede
    "mudou no banco mas o cliente nunca soube".

    Criado pelo service NA MESMA transação da mudança de negócio (mesmo princípio do
    OutboxEvent da BE-03). A entrega é uma task que chama o client HTTP;
    status: pending → processing → completed (entregue) | failed.
    """

    event_type = models.CharField(max_length=100)
    destination = models.URLField(max_length=500)  # cadastrado e validado (anti-SSRF), nunca livre
    payload = models.JSONField()
    max_attempts = models.PositiveIntegerField(default=8)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    last_status_code = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["status", "next_attempt_at"])]


# ---------------------------------------------------------------------------
# Mixin opcional para models de domínio que dependem de integração.
# É o que o app Expo consome para representar consistência eventual
# sem mentir para o usuário. Vocabulário próprio (estado do REGISTRO em relação
# ao provider), diferente do ProcessingStatus (estado de um TRABALHO).
# ---------------------------------------------------------------------------


class SyncStatusMixin(models.Model):
    class SyncStatus(models.TextChoices):
        PENDING = "pending"
        SYNCED = "synced"
        FAILED = "failed"
        OUTDATED = "outdated"

    sync_status = models.CharField(
        max_length=20, choices=SyncStatus.choices, default=SyncStatus.PENDING
    )
    last_synced_at = models.DateTimeField(null=True, blank=True)
    last_sync_error = models.TextField(blank=True, default="")
    external_updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
