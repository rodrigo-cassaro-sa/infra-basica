---
name: backend-async
description: Padrão BE-03 da software house para processamento assíncrono em backends Django headless (API desacoplada do frontend Expo — app e painel web) — Celery, Redis como broker, workers, filas, roteamento, retries, backoff, jitter, idempotência, timeouts, Celery Beat, publicação após commit, event bus (dispatch → tasks), outbox, jobs de longa duração, observabilidade e deploy de workers. Use sempre que aparecer Celery, shared_task, worker, fila, broker, celery beat, tarefa agendada, retry, job em background, processamento em lote, importação/exportação, geração de relatório ou PDF, execução em background de envio de e-mail/WhatsApp/SMS, processamento de webhook, sincronização ou integração externa demorada (o cliente/adapter do provider é da backend-integrations) — e também quando a pessoa não citar Celery e apenas pedir para "rodar em background", "não travar a request", "processar depois", "agendar para todo dia" ou "mostrar progresso no painel". Use igualmente para revisar, refatorar ou auditar tasks já existentes.
---

# BE-03 — backend-async

Padrão de processamento assíncrono para os backends Django da software house.

Contexto: o backend é **headless**. Ele expõe API (BE-02) e é consumido pelo **frontend Expo** (app iOS/Android e painel/site web — "painel" nesta skill = esse frontend). O app nunca fala com Celery, nunca lê o result backend e nunca conhece `task_id`. Tudo que ele precisa enxergar tem que estar persistido no PostgreSQL.

Dependências: **BE-01** backend-core (domínio/services), **BE-02** backend-api (endpoints). Integrações externas: **BE-05**. IA: **BE-04**.
Convenções comuns (nomes, erros, correlation id, status de job): `backend-core/references/contratos-entre-skills.md` — em divergência, vale o contrato.

**Esta skill é dona de:** port `event_bus` (`CeleryEventBus`), `EVENT_HANDLERS`, outbox (`OutboxEvent`), propagação de `correlation_id` para tasks, política de retry (a camada de retry é a task).

---

## Princípio central

```text
Task  →  Service  →  Domínio  →  Banco / Integração
```

E nunca:

```text
Task  →  300 linhas de regra de negócio
```

| A **task** decide | O **service** decide |
|---|---|
| quando executar | o que a operação faz |
| em qual fila | quais regras respeitar |
| como repetir | quais dados mudam |
| como tratar falha transitória | |
| quais limites aplicar | |

A task é um **adaptador de execução**. Não duplique aqui regra que pertence à BE-01.

---

## Passo 1 — Confirmar que precisa ser assíncrono

Antes de escrever qualquer `@shared_task`, pergunte se a operação realmente se encaixa. Assíncrono cobra um preço: broker, workers, latência, eventual consistency, duplicidade possível, monitoramento, complexidade operacional.

**Vá para fila quando** a operação demora mais que uma requisição deveria durar, não precisa terminar antes da resposta HTTP, depende de serviço externo, precisa de retry, roda em lote, é agendada, consome muitos recursos ou merece worker especializado.

Casos típicos: e-mail, WhatsApp, geração de PDF, importação, exportação, sincronização, processamento de arquivo/imagem, webhook, relatório, IA, tarefa periódica, integração externa.

**Mantenha síncrono** validação de campo, consulta de banco, criação de registro simples, mudança de status simples, consulta comum.

Não confunda `async/await` com background job. `async/await` ajuda na concorrência de I/O dentro da própria execução; Celery tira o trabalho do processo da requisição. Leia `references/setup.md` se precisar justificar essa diferença para alguém.

---

## Passo 2 — Escrever a task

A task fica em `apps/<dominio>/tasks.py`, ao lado do `services.py` daquele domínio. Ela deve caber na tela.

```python
from celery import shared_task

from apps.notifications.services import customer_email_send


@shared_task(ignore_result=True)
def customer_email_send_task(*, customer_id: int, template: str) -> None:
    customer_email_send(customer_id=customer_id, template=template)
```

Regras que não abrem exceção:

- **Argumentos simples e pequenos.** IDs, strings, números, booleanos, dicts pequenos — sempre JSON serializável. `invoice_send_task.delay(invoice_id=123)`, nunca `delay(invoice_object)`. O worker busca o estado atual quando executar.
- **Nada de payload gigante na fila.** Arquivo vai para o MinIO e a task recebe `file_id`; dados vão para o PostgreSQL e a task recebe `job_id`. A fila transporta a referência ao trabalho, não o trabalho.
- **Nada de segredo como argumento.** Senha, API key, token, cookie e credencial aparecem em log, trace, monitoramento e mensagem de erro. A task busca isso no ambiente ou no serviço de secrets.
- **Nome estável:** `<entidade>_<ação>_task` (`invoice_send_task`, `order_process_task`), espelhando o service do core (`invoice_send`, `order_process`). Renomear task com mensagens ainda no broker quebra consumo.
- **Argumentos por keyword** (`kwargs`), como os services: é assim que o `CeleryEventBus` entrega o payload do evento.
- **Serialização JSON.** Nunca pickle sem necessidade excepcional e revisão de segurança.

---

## Passo 3 — Confiabilidade

Este é o passo onde as tasks da casa costumam falhar. Trate os quatro itens abaixo explicitamente em toda task nova.

**Publicar só depois do commit — e o core não importa task.** Se a task for disparada dentro de uma transação aberta, o worker pode começar antes do commit e não encontrar o registro. No **core**, o service emite um evento; esta skill liga evento → task:

```python
# apps/customers/services.py (core) — nunca importa tasks
@transaction.atomic
def customer_create(*, actor, name: str, email: str) -> Customer:
    customer = Customer(name=name, email=email, tenant_id=tenant_id_of(actor), created_by=actor)
    validate_and_save(customer)
    transaction.on_commit(lambda: dispatch("customer.created", customer_id=customer.pk))
    return customer
```

```python
# config/settings/base.py (esta skill)
PORTS["event_bus"] = "apps.jobs.bus.CeleryEventBus"
EVENT_HANDLERS = {"customer.created": ["apps.notifications.tasks.customer_welcome_send_task"]}
```

Adaptadores de borda (view, webhook da BE-05, tool da BE-04) podem chamar `task.delay_on_commit(...)` direto. Use `delay()` apenas quando a task não depende de nada pendente na transação. Implementação do bus, correlation id e outbox: `references/event-bus.md`.

**Idempotência.** Assuma entrega *at-least-once*: executar duas vezes tem que dar o mesmo resultado final. Garanta isso no domínio, com `UniqueConstraint`, identificador externo único (`webhook_event_id`), `idempotency_key` de operação, ou estado explícito (`pending → processing → completed → failed`) com `attempts`, `started_at`, `finished_at`, `last_error`. Não projete o negócio assumindo "exactly once" do broker.

**Retry só para falha transitória.** Timeout, connection error, 429, 502, 503, indisponibilidade temporária. Nunca para payload inválido, 401 definitivo, 403, regra de negócio violada ou registro inexistente definitivo. Todo retry tem limite, e `autoretry_for=(Exception,)` é proibido. A classificação é **única na família** (`common/errors.py` do core): `TransientError` → retry; `PermanentError` e `DomainError` → sem retry. `IntegrationTimeout` (BE-05) e `AITransientError` (BE-04) já herdam de `TransientError`.

```python
from common.errors import TransientError


@shared_task(
    autoretry_for=(TransientError,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=5,
)
def customer_sync_task(*, customer_id: int) -> None:
    customer_sync(customer_id=customer_id)
```

**Uma camada de retry só:** dentro de task, o client HTTP da BE-05 roda sem retry próprio (`RetryPolicy(max_attempts=1)`); quem repete é a task.

**Timeouts encaixados.** Toda chamada de rede dentro de task tem timeout próprio, menor que o limite da task:

```text
HTTP connect 3s  <  HTTP read 5–20s  <  soft_time_limit 50s  <  time_limit 60s
```

Assim a task tem chance de tratar a falha antes de ser morta. Não confie apenas no time limit do Celery.

Detalhes de `acks_late`, outbox pattern, locks, circuit breaker e reprocessamento manual estão em `references/reliability.md`.

---

## Passo 4 — Fila e worker

Comece com a fila `default`. Crie fila nova só quando houver necessidade real — tipicamente quando uma carga pode bloquear outra (relatório pesado atrás de reset de senha).

Roteie de forma central, não espalhado em `apply_async()`:

```python
CELERY_TASK_ROUTES = {
    "apps.notifications.tasks.*": {"queue": "emails"},
    "apps.integrations.*": {"queue": "integrations"},  # tasks dos providers da BE-05
    "apps.ai.*": {"queue": "ai"},                      # BE-04 (quando houver)
}
```

Rate limit serve para proteger integração externa e é aplicado **por worker** — para teto global, desenhe a fila/worker de acordo. Concorrência, pool, prefetch e reciclagem de processo: meça antes de mexer, ver `references/queues-and-workers.md`.

---

## Passo 5 — Job persistente e contrato com o app

Este é o ponto que sustenta o desacoplamento. Para qualquer processamento que o usuário acompanha, crie uma entidade de negócio:

```python
from common.jobs import ProcessingStateModel, ProgressMixin
from common.tenancy import TenantModel


class ReportJob(TenantModel, ProcessingStateModel, ProgressMixin):  # base comum da família
    kind = models.CharField(max_length=40)
```

`ProcessingStateModel` traz `status` (`pending/processing/completed/failed/canceled/ignored`), `attempts`, `started_at`, `finished_at`, `last_error`, `correlation_id`. Mesma base de `AIJob` (BE-04) e `WebhookEvent`/`SyncState` (BE-05). Transições por service, nunca `queryset.update()` solto.

Fluxo padrão da API assíncrona:

```text
Painel → POST /reports/ → API (BE-02) → Service (BE-01) → cria ReportJob
      → commit → publica task (BE-03) → worker processa → atualiza ReportJob
Painel ← 202 Accepted + job_id ... depois consulta GET /reports/{job_id}/
```

Consequências que valem como regra:

- Nunca chamar `AsyncResult.get()` dentro de uma requisição — isso destrói a vantagem do assíncrono.
- Nunca bloquear um worker esperando `.get()` de outra task.
- `ignore_result=True` em fire-and-forget; habilite result backend só quando alguém realmente consultar.
- Estado de negócio mora no PostgreSQL, não no Celery e não no Flower.
- Trabalho grande é dividido em chunks com progresso persistido, nunca uma task de horas processando 1.000.000 de registros.

---

## Passo 6 — Observabilidade

Toda task relevante precisa permitir descobrir: qual task executou, qual entidade processou, quando começou e terminou, quantas tentativas, qual erro, e o `correlation_id` que veio da requisição do app (propagado por signals do Celery — `references/event-bus.md`). Não logue payload sensível completo.

Métricas mínimas: publicadas, executadas, concluídas, falhas, retries, tempo de execução, backlog da fila, idade da mensagem mais antiga, workers disponíveis. Fila crítica com backlog crescente gera alerta.

Deploy, health check de worker, graceful shutdown, segurança do broker e isolamento por ambiente: `references/operations.md`.

---

## Checklist de task nova

Rode isto antes de dar a task por pronta:

```text
[ ] precisa realmente ser assíncrona?
[ ] regra de negócio está no service?
[ ] core dispara via dispatch()/EVENT_HANDLERS (sem importar task)?
[ ] argumentos são simples e pequenos?
[ ] nenhum segredo vai na mensagem?
[ ] publicação ocorre após commit quando necessário?
[ ] task é idempotente? duplicidade foi considerada?
[ ] retry só para common.errors.TransientError? client sem retry próprio?
[ ] retry tem limite? backoff e jitter avaliados?
[ ] integração tem timeout? task tem time limit quando necessário?
[ ] fila correta escolhida? rate limit avaliado?
[ ] resultado precisa ser armazenado / job persistido para o painel?
[ ] logs e métricas suficientes?
[ ] testes criados?
```

Checklists de tarefa periódica, checklist operacional e a Definition of Done completa (20 itens) estão em `references/checklists.md`.

---

## Anti-patterns a recusar em revisão

| Anti-pattern | Correção |
|---|---|
| Task com 300 linhas de regra | mover para service, task só chama |
| Service do core importando task | `dispatch()` + `EVENT_HANDLERS` |
| Hierarquia própria de erro transitório | `common.errors.TransientError` |
| Task gigante de horas | chunks com progresso persistido |
| `autoretry_for=(Exception,)` | classificar transitório vs permanente |
| Fila como banco | estado de negócio no PostgreSQL |
| `countdown` de 30 dias | `ScheduledAction` + dispatcher periódico |
| Polling agressivo a cada poucos segundos | webhook, evento interno ou consulta agrupada |
| Dois Celery Beat na mesma agenda | uma única instância por schedule |
| `AsyncResult.get()` na view | 202 + job_id + polling do painel |

---

## Onde está o detalhe

Leia o arquivo correspondente quando a tarefa entrar no assunto:

- `references/setup.md` — stack, Redis vs RabbitMQ, estrutura de pastas, `config/celery.py`, settings por ambiente, serialização, `async/await` vs Celery.
- `references/event-bus.md` — `CeleryEventBus`, `EVENT_HANDLERS`, correlation id em tasks, outbox (`OutboxEvent`), testes do bus.
- `references/reliability.md` — commit, idempotência, retry, backoff, jitter, timeouts, `acks_late`, falhas permanentes, dead letter, reprocessamento, circuit breaker, locks, outbox.
- `references/queues-and-workers.md` — filas, roteamento, prioridade, rate limit, concorrência, pool, Windows, prefetch, memória.
- `references/scheduling.md` — Celery Beat, `django-celery-beat`, timezone, `countdown`/`eta`, agendamentos de negócio persistidos.
- `references/jobs-and-workflows.md` — chain/group/chord, chunks, models de job, resultados, webhooks, integrações (BE-05), IA (BE-04).
- `references/operations.md` — logs, correlation ID, métricas, backlog, Flower, deploy, health check, graceful shutdown, segurança do broker, ambientes.
- `references/testing.md` — o que testar no service vs na task, teste de publicação após commit, teste de retry, eager mode, ambiente local.
- `references/checklists.md` — checklists de task nova, tarefa periódica, operação, Definition of Done e o resultado esperado ao abrir qualquer backend da casa.

---

## Regra de ouro

```text
CELERY EXECUTA
SERVICE DECIDE
POSTGRESQL GUARDA O ESTADO
REDIS TRANSPORTA O TRABALHO
```

A fila não é a fonte da verdade. O app lê o PostgreSQL (via API), nunca o broker.
