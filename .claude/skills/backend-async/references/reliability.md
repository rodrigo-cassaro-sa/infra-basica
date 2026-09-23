# Confiabilidade

Conteúdo: publicação após commit · idempotência · estado explícito · retry · backoff · jitter · timeouts · `acks_late` · entrega at-least-once · falhas permanentes · dead letter · reprocessamento · circuit breaker · banco dentro da task · locks · eventos internos · outbox · webhooks.

---

## Publicar somente depois do commit

O problema:

```text
1. Django cria Order
2. task.delay(order.id)
3. worker começa
4. transaction ainda não commitou
5. worker não encontra Order
```

O padrão:

```text
TRANSACTION → COMMIT → PUBLICAR TASK
```

Quando disponível, preferir:

```python
order_process_task.delay_on_commit(order_id=order.id)
```

Ou:

```python
from django.db import transaction

transaction.on_commit(
    lambda: order_process_task.delay(order_id=order.id)
)
```

Nunca publicar uma task dependente de um registro antes de garantir que ele foi commitado.

### `delay()` versus `delay_on_commit()`

`delay()` quando a tarefa não depende de transação pendente.

`delay_on_commit()` quando o registro acabou de ser criado, acabou de ser alterado, ou a task precisa observar o estado commitado.

```python
invoice = invoice_create(...)

invoice_send_task.delay_on_commit(invoice_id=invoice.id)
```

### Padrão service + evento (core) / adaptador + task (borda)

O **core não importa tasks**. O service emite um evento depois do commit e o `CeleryEventBus`
(implementação do port `event_bus`, dono: esta skill) enfileira as tasks registradas:

```python
# apps/customers/services.py (core)
@transaction.atomic
def customer_create(*, actor, name: str, email: str) -> Customer:
    customer = Customer(name=name, email=email, tenant_id=tenant_id_of(actor), created_by=actor)
    validate_and_save(customer)
    transaction.on_commit(lambda: dispatch("customer.created", customer_id=customer.pk))
    return customer
```

```python
# config/settings/base.py
EVENT_HANDLERS = {
    "customer.created": ["apps.notifications.tasks.customer_welcome_send_task"],
}
```

Adaptadores de borda (view da API, webhook da BE-05, tool da BE-04) **podem** chamar
`alguma_task.delay_on_commit(...)` direto — só o core é obrigado a passar pelo evento.
Implementação completa: `references/event-bus.md`.

---

## Idempotência

```text
executar uma vez  ou  executar novamente  →  resultado final consistente
```

Essencial porque sistemas distribuídos repetem mensagens e reexecutam trabalhos.

Ruim:

```python
def order_charge(*, order_id):
    payment_gateway.charge(...)
```

Duas execuções → duas cobranças.

Melhor:

```text
order → payment_operation → idempotency_key → gateway
```

Registrar uma chave única da operação.

### Idempotência no banco

Usar quando adequado: `UniqueConstraint`, identificador externo único, `status`, `processed_at`, `operation_id`.

```text
webhook_event_id UNIQUE
```

Se o mesmo evento chegar de novo, não duplicar o efeito.

### Estado explícito de processamento

```text
pending → processing → completed → failed
```

Campos úteis: `status`, `attempts`, `started_at`, `finished_at`, `last_error`, `external_id`.

Não depender apenas do estado interno do Celery para processos de negócio críticos.

---

## Retry

Retry é adequado para falha transitória:

```text
timeout
connection error
HTTP 429 / 502 / 503
serviço temporariamente indisponível
```

Não usar retry automático para:

```text
CPF inválido
payload inválido
401 definitivo
403
regra de negócio violada
registro inexistente definitivo
```

### Retry explícito

```python
@shared_task(
    bind=True,
    max_retries=5,
)
def customer_sync_task(self, *, customer_id: int):
    try:
        customer_sync(customer_id=customer_id)
    except TransientError as exc:  # common.errors — hierarquia única da família
        raise self.retry(
            exc=exc,
            countdown=30,
        )
```

### Retry automático

```python
from common.errors import TransientError


@shared_task(
    autoretry_for=(TransientError,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def customer_sync_task(*, customer_id: int):
    customer_sync(customer_id=customer_id)
```

`autoretry_for=(Exception,)` sem classificação é anti-pattern. A classificação é **única na
família** e mora no core:

| Exceção | Origem | Na task |
|---|---|---|
| `common.errors.TransientError` | `IntegrationTimeout`, `IntegrationUnavailable`, `IntegrationRateLimited` (BE-05), `AITransientError` (BE-04) | retry com backoff + jitter (respeitar `exc.retry_after`) |
| `common.errors.PermanentError` | `IntegrationValidationError`, 401/403 do provider, `AIPermanentError` | sem retry → job `failed` |
| `common.exceptions.DomainError` | regra de negócio (core) | sem retry → job `failed` ou `ignored` |

Não criar `TemporaryIntegrationError`, `BusinessError` ou similares.

### Uma camada de retry só

Dentro de task, **o retry é da task**. O client HTTP da BE-05 é instanciado com
`RetryPolicy(max_attempts=1)` (padrão do `BaseHTTPClient` quando chamado de task) para as
tentativas não se multiplicarem (5 da task × 3 do client = 15 chamadas ao provider).

### Backoff

Retries não devem bombardear um serviço indisponível.

```text
tentativa 1 → espera
tentativa 2 → espera maior
tentativa 3 → espera maior
```

Exponential backoff quando apropriado.

### Jitter

Sem jitter:

```text
10.000 tasks falham → todas repetem em 30 segundos → novo pico
```

Com jitter: retries distribuídos no tempo. Adicionar sempre que muitos workers puderem falhar simultaneamente.

### Limite de retries

Toda política de retry tem limite. Nunca criar repetição infinita sem motivo deliberado.

Após esgotar retries: registrar falha, atualizar status, gerar métrica, permitir reprocessamento controlado quando apropriado.

---

## Timeouts

Toda operação de rede dentro de task tem timeout.

```python
response = client.get(url, timeout=10)
```

Quando a biblioteca permitir separar `connect timeout` e `read timeout`, configurar ambos. Não confiar apenas no time limit do Celery.

### Soft e hard time limit

```text
soft_time_limit  → dá chance de tratar/encerrar
time_limit       → limite duro
```

```python
@shared_task(
    soft_time_limit=50,
    time_limit=60,
)
def generate_report_task(report_id: int):
    ...
```

### Ordem dos limites

```text
HTTP connect timeout:   3s     (padrão BaseHTTPClient da BE-05)
HTTP read timeout:    5–20s    (por integração; relatório remoto até 60s → aumentar os limites da task)
soft task limit:       50s
hard task limit:       60s
```

O timeout da integração é sempre menor que o limite total da task, para que a task tenha oportunidade de tratar a falha antes de ser encerrada à força.

---

## `acks_late` e entrega at-least-once

Não habilitar `acks_late` globalmente sem entender as consequências. Ele é útil quando a mensagem só deve ser confirmada após a execução, mas exige task idempotente.

```text
acks_late + task idempotente + tratamento consciente de falha
```

`acks_late` não substitui retry.

Não projetar o negócio assumindo entrega exatamente uma vez. Projetar para:

```text
at-least-once possível
+ idempotência
+ constraints
+ estado explícito
```

A confiabilidade mora no domínio, não no broker.

---

## Falhas permanentes

Quando a task esgota os retries, `status = failed`, registrado de forma estruturada:

```text
task
entidade
erro
tentativas
timestamp
correlation_id
```

Isso permite investigação e reprocessamento manual controlado quando fizer sentido.

### Dead letter / fila de falhas

Redis como broker não oferece todas as características de mensageria avançada. Para dead-letter routing complexo, avaliar RabbitMQ.

No padrão inicial, é mais simples persistir falhas importantes no domínio:

```text
FailedOperation
IntegrationAttempt
ImportJob
WebhookEvent
```

### Reprocessamento manual

```text
falha → operador analisa → corrige causa → reprocessar
```

Nunca permitir reprocessamento que ignore idempotência ou permissões.

### Circuit breaker

Para integrações críticas e instáveis, considerar circuit breaker quando a complexidade justificar:

```text
serviço externo fora → parar chamadas repetidas → aguardar recuperação
```

Não adicionar biblioteca de circuit breaker em todo projeto por padrão.

### Falhas esperadas

Toda task que usa rede deve assumir que:

```text
DNS pode falhar
API pode responder 500
conexão pode cair
timeout pode acontecer
broker pode reconectar
worker pode reiniciar
mensagem pode reaparecer
```

Projetar para falha é parte da BE-03.

---

## Banco dentro das tasks

Tasks podem usar o ORM normalmente, mas devem manter transações curtas, evitar carregar milhares de objetos, evitar conexões desnecessariamente longas, trabalhar em lotes e respeitar concorrência.

### Locks

Quando apenas um processamento puder ocorrer por entidade (ex.: pedido 123), avaliar: status transacional, `select_for_update()`, constraint, lock distribuído, chave única de operação.

Não usar lock distribuído quando uma constraint no PostgreSQL resolve.

---

## Eventos internos e Outbox

O caminho padrão é `dispatch()` → `CeleryEventBus` → task (ver `event-bus.md`). Se o processo
morrer entre o commit e a publicação no Redis, o evento se perde — aceitável para a maioria
dos efeitos (e-mail, notificação), porque existe reconciliação/reprocessamento.

Para fluxos em que **perder uma mensagem após o commit é inaceitável** (cobrança, fiscal,
integração financeira), trocar o port por `OutboxEventBus`: o evento é gravado em `OutboxEvent`
**na mesma transação** e um dispatcher periódico publica. Dono do model e do dispatcher: **esta
skill** (`event-bus.md` §4). A BE-05 reutiliza para webhooks enviados (`OutgoingWebhook`) em vez de
criar um outbox próprio.

---

## Webhooks

**Dono: backend-integrations** (`WebhookEvent`, assinatura, dedupe, inbox). Aqui só vale a regra
de execução: a task de processamento chama service do core, é idempotente pelo `WebhookEvent`,
retry só para `TransientError`. Ver `backend-integrations/references/webhooks.md`.
