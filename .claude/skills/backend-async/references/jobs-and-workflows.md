# Jobs, workflows e integrações

Conteúdo: chain/group/chord · chunks · job de negócio · resultado da task · contrato com o app · integrações (BE-05) · IA (BE-04).

---

## Workflows

Para fluxos simples pode-se usar `chain`, `group` e `chord`, com moderação. Celery Canvas não é motor de regras de negócio.

Se o workflow for crítico e longo: persistir estado, definir etapas, permitir retomada, garantir idempotência.

### Chain

Quando uma tarefa depende do resultado lógico da anterior:

```text
A → B → C
```

Avaliar se a dependência não fica mais clara como um workflow persistido no domínio.

### Group

Quando vários trabalhos independentes podem executar em paralelo:

```text
      ┌→ B
A ────┼→ C
      └→ D
```

Cuidado com explosão de milhares ou milhões de mensagens. Para grandes volumes, usar chunking.

---

## Chunks

Evitar:

```text
1 task → processa 1.000.000 registros
```

Preferir:

```text
job → lotes → tasks menores
```

Exemplo de ponto de partida: 1.000 registros por lote. O tamanho deve ser medido e ajustado.

---

## Job de negócio

Para processamento relevante, criar entidade persistente herdando a base **comum da família**
(`common/jobs.py` no core) — o mesmo vocabulário de status que `AIJob` (BE-04) e `WebhookEvent`/`SyncState` (BE-05) usam:

```python
# apps/imports/models.py
from django.db import models

from common.jobs import ProcessingStateModel, ProgressMixin
from common.tenancy import TenantModel


class ImportJob(TenantModel, ProcessingStateModel, ProgressMixin):
    file = models.ForeignKey("integrations.FileAsset", on_delete=models.PROTECT)
    kind = models.CharField(max_length=40)
```

```python
# apps/imports/services.py — transições SEMPRE por service
@transaction.atomic
def import_job_mark_processing(*, job_id: int) -> ImportJob:
    job = ImportJob.objects.select_for_update().get(pk=job_id)
    if job.status in {ProcessingStatus.COMPLETED, ProcessingStatus.CANCELED}:
        raise ImportJobAlreadyFinished(job_id=job_id)   # ConflictError → task não reprocessa
    job.status = ProcessingStatus.PROCESSING
    job.attempts = F("attempts") + 1
    job.started_at = job.started_at or timezone.now()
    job.save(update_fields=["status", "attempts", "started_at", "updated_at"])
    return job
```

Status: `pending → processing → completed | failed | canceled` (grafia `canceled`, um L).

Isso permite ao app Expo consultar progresso sem depender do backend de resultados do Celery — é o que mantém frontend e infraestrutura de fila desacoplados.

---

## Resultado da task

Por padrão, não armazenar resultado se ninguém for usar.

```python
@shared_task(ignore_result=True)
def send_email_task(...):
    ...
```

Quando o resultado representar estado de negócio, persistir em model próprio.

### Não usar `AsyncResult.get()` dentro de requisição

```text
API → publica task → fica esperando a task terminar
```

Isso elimina a principal vantagem do processamento assíncrono. Se a requisição precisa esperar o resultado, avaliar se Celery é realmente necessário naquele fluxo.

### Não bloquear worker esperando outra task

Task que publica outra task e chama `.get()` reduz capacidade e pode criar deadlock. Preferir chain, callbacks, estado persistente ou workflow explícito.

---

## Fluxo padrão da API assíncrona

```text
Cliente (painel web)
  ↓
POST /reports/
  ↓
BE-02 API
  ↓
BE-01 Service
  ↓
cria ReportJob
  ↓
commit
  ↓
BE-03 Task
  ↓
Worker
  ↓
processa
  ↓
atualiza ReportJob
```

A API responde `202 Accepted` com o identificador do job quando o processamento ocorre depois. O painel consulta o job por esse identificador — nunca por `task_id`.

---

## Integrações externas (BE-05)

```text
task → integration service/client → API externa
```

A BE-03 define execução, retry e fila. A BE-05 define o contrato com o sistema externo. A task não fala HTTP diretamente.

## IA (BE-04)

Processos longos de IA vão para fila:

```text
API → cria AIJob → task → serviço de IA → salva resultado
```

A arquitetura específica de IA pertence à BE-04.

---

## Dependências entre skills

```text
BE-01 backend-core  →  services / domínio
        ↓
BE-03 backend-async →  tasks / workers / filas
        ↓
BE-05 backend-integrations
BE-04 backend-ai-mcp

BE-02 backend-api → publica trabalho → BE-03
```

---

## Arquitetura padrão final

```text
                    CLIENTE
                       │
                       ▼
                 Django / DRF
                       │
                       ▼
                    Service
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
         PostgreSQL          on_commit
                                  │
                                  ▼
                               Celery
                                  │
                                  ▼
                                Redis
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
        Worker Default      Worker Integration    Worker Long
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                                  ▼
                               Service
                                  │
                          ┌───────┴───────┐
                          ▼               ▼
                     PostgreSQL      Integrações
```
