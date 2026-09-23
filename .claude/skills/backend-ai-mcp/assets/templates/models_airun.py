"""apps/ai/models.py — instrumentação e estado de IA (dono: BE-04).

Bases comuns da família (backend-core):
- AIRun       → BaseModel (created_at/updated_at)
- AIJob       → TenantModel + ProcessingStateModel + ProgressMixin (mesmo vocabulário de
                status de ImportJob, WebhookEvent, SyncState: pending/processing/completed/
                failed/canceled)
- PendingAction → confirmação humana de ação sensível proposta por agente

Regras:
- usuário SEMPRE via settings.AUTH_USER_MODEL; tenant via "tenants.Tenant" com PROTECT;
- nenhum método com lógica nos models — transições nos services (apps/ai/runs.py, jobs.py);
- nenhum guarda prompt/output completos por padrão.
"""

from django.conf import settings
from django.db import models

from common.jobs import ProcessingStateModel, ProgressMixin
from common.models import BaseModel
from common.tenancy import TenantModel


class AIRun(BaseModel):
    """Uma chamada a provider. Criada/finalizada por apps/ai/runs.py."""

    class Status(models.TextChoices):
        RUNNING = "running", "Executando"
        SUCCEEDED = "succeeded", "Sucesso"
        FAILED = "failed", "Falhou"

    use_case = models.CharField(max_length=64, db_index=True)
    # null = execução de sistema (task sem usuário). PROTECT: histórico de custo não some.
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.PROTECT, null=True, blank=True, related_name="+")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    provider = models.CharField(max_length=32)
    model = models.CharField(max_length=64)
    prompt_version = models.CharField(max_length=16, blank=True, default="")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.RUNNING)
    input_tokens = models.IntegerField(null=True, blank=True)
    output_tokens = models.IntegerField(null=True, blank=True)
    latency_ms = models.IntegerField(null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    error_code = models.CharField(max_length=64, blank=True, default="")  # MAIÚSCULAS
    correlation_id = models.CharField(max_length=64, blank=True, default="", db_index=True)

    class Meta:
        indexes = [models.Index(fields=["use_case", "created_at"])]


class AIJob(TenantModel, ProcessingStateModel, ProgressMixin):
    """Recurso consultável pelo app Expo (202 + polling). Não depender do task id do Celery."""

    kind = models.CharField(max_length=64, db_index=True)
    provider = models.CharField(max_length=32, blank=True, default="")
    model = models.CharField(max_length=64, blank=True, default="")
    result_reference = models.CharField(max_length=255, blank=True, default="")
    error_code = models.CharField(max_length=64, blank=True, default="")


class PendingAction(TenantModel):
    """
    Ação sensível proposta por agente/tool, aguardando confirmação humana.

    agente propõe → PendingAction(pending) → app lista → humano confirma pela API
    → service do core executa com actor=quem confirmou → PendingAction(confirmed)
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Aguardando"
        CONFIRMED = "confirmed", "Confirmada"
        REJECTED = "rejected", "Rejeitada"
        EXPIRED = "expired", "Expirada"

    action = models.CharField(max_length=100)  # nome do service: "invoice_cancel"
    arguments = models.JSONField()              # kwargs validados (só IDs/primitivos)
    summary = models.CharField(max_length=300)  # texto para o humano decidir
    proposed_by_run = models.ForeignKey(AIRun, on_delete=models.PROTECT, null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
