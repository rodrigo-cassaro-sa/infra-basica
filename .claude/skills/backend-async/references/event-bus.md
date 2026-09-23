# Event bus — implementação do port `event_bus` (dono: BE-03)

O core só conhece `common.events.dispatch(event, **payload)`. Esta skill entrega a
implementação real e decide quais tasks cada evento dispara.

```text
service (core) ──on_commit──▶ dispatch("order.approved", order_id=1)
                                   │  get_port("event_bus")
                                   ▼
                          CeleryEventBus.publish()
                                   │  settings.EVENT_HANDLERS
                                   ▼
             order_notify_task.apply_async(kwargs=..., headers={"correlation_id": ...})
```

## 1. apps/jobs/bus.py

```python
import logging
from typing import Any

from celery import current_app
from django.conf import settings

from common.logging import correlation_id

logger = logging.getLogger(__name__)


class CeleryEventBus:
    """Port event_bus → Celery. Registrado em settings.PORTS["event_bus"]."""

    def publish(self, event: str, payload: dict[str, Any]) -> None:
        handlers = settings.EVENT_HANDLERS.get(event, [])
        if not handlers:
            logger.debug("event.no_handlers", extra={"event": event})
            return
        for task_name in handlers:
            current_app.send_task(
                task_name,
                kwargs=payload,
                headers={"correlation_id": correlation_id.get() or ""},
            )
            logger.info("event.published", extra={"event": event, "task": task_name})
```

`send_task` por nome evita importar o módulo da task (sem import circular, sem acoplamento).
O `dispatch()` já roda dentro de `on_commit` — por isso aqui é `send_task` direto, não `delay_on_commit`.

## 2. settings

```python
# config/settings/base.py
PORTS["event_bus"] = "apps.jobs.bus.CeleryEventBus"

# evento → tasks (nome completo registrado no Celery)
EVENT_HANDLERS: dict[str, list[str]] = {
    "order.approved": [
        "apps.notifications.tasks.order_approved_notify_task",
        "apps.integrations.erp.tasks.order_export_task",
    ],
}

# config/settings/test.py → PORTS["event_bus"] = "common.events.InMemoryEventBus"
```

Convenções: evento `<entidade>.<fato_no_passado>`; task `<entidade>_<ação>_task`; payload só
IDs/primitivos JSON. A task relê o estado atual via selector.

## 3. Correlation id nas tasks

```python
# config/celery.py (depois de app = Celery(...))
from celery.signals import before_task_publish, task_postrun, task_prerun

from common.logging import correlation_id

_tokens: dict[str, object] = {}


@before_task_publish.connect
def _inject(headers=None, **_):
    if headers is not None and not headers.get("correlation_id"):
        headers["correlation_id"] = correlation_id.get() or ""


@task_prerun.connect
def _bind(task_id=None, task=None, **_):
    value = getattr(task.request, "correlation_id", None) or task_id
    _tokens[task_id] = correlation_id.set(value)


@task_postrun.connect
def _unbind(task_id=None, **_):
    token = _tokens.pop(task_id, None)
    if token is not None:
        correlation_id.reset(token)
```

Assim o log da task tem o mesmo `correlation_id` da requisição do app que originou o evento,
e a BE-05 envia o mesmo valor no `X-Request-ID` para o provider.

## 4. Outbox (quando perder evento é inaceitável)

```python
# apps/jobs/models.py
from django.db import models

from common.jobs import ProcessingStateModel


class OutboxEvent(ProcessingStateModel):
    event = models.CharField(max_length=100, db_index=True)
    payload = models.JSONField()

    class Meta:
        indexes = [models.Index(fields=["status", "created_at"])]


# apps/jobs/bus.py
class OutboxEventBus:
    """Grava o evento na MESMA transação do service. Publicação fica com o dispatcher."""

    def publish(self, event: str, payload: dict) -> None:
        OutboxEvent.objects.create(event=event, payload=payload, correlation_id=correlation_id.get() or "")
```

Com outbox, o service chama `dispatch()` **dentro** da transação (não em `on_commit`) — é
exatamente isso que garante atomicidade. Documentar no service quando o projeto usa outbox.
Dispatcher: task periódica (Beat, a cada 5–10 s) que pega `pending` com
`select_for_update(skip_locked=True)`, faz `send_task` e marca `completed` via service de job.

## 5. Teste

```python
def test_order_approved_routes_to_tasks(settings, mocker):
    settings.EVENT_HANDLERS = {"order.approved": ["apps.x.tasks.a_task"]}
    send = mocker.patch("apps.jobs.bus.current_app.send_task")
    CeleryEventBus().publish("order.approved", {"order_id": 1})
    send.assert_called_once()
    assert send.call_args.kwargs["kwargs"] == {"order_id": 1}
```

Nos testes do core, `InMemoryEventBus` (ver `backend-core/references/padroes-de-dominio.md` §12).
