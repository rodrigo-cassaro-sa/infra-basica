# Contratos entre o core e as outras 4 skills

**Este arquivo é a fonte da verdade da família BE-01…BE-05** (e do ponto de contato com a devops/OPS-01). Se qualquer outra skill
(SKILL.md, reference ou template) contradizer algo daqui, vale o que está aqui — e a outra
skill está com bug.

O core é a única fonte de regra de negócio. As outras skills são **adaptadores de entrada
ou saída** em volta dele. O consumidor final é sempre o frontend **Expo** (app iOS/Android e
painel/site web a partir da mesma base), via REST.

```text
ENTRADA (quem chama o core)              SAÍDA (o que o core pede, via ports)
backend-api      → HTTP/REST (Expo)      backend-async        → event_bus (tasks pós-commit)
backend-async    → tasks/filas/cron      backend-integrations → gateways, WhatsApp, e-mail, storage, push
backend-ai-mcp   → tools de agente/MCP   backend-ai-mcp       → AI services (providers via AI_PROVIDERS)
backend-integrations → webhooks de entrada
```

---

## 1. Regras universais (valem para as 4)

1. **Escrever** = chamar um service. Nunca `Model.objects.create/update/delete` fora de um service (vale também para os models próprios de cada skill: `WebhookEvent`, `AIRun`, jobs — cada skill tem seus services).
2. **Ler** = chamar um selector, passando `actor`.
3. Sempre passar o **`actor`** real. `actor=None` só em processo de sistema disparado pela backend-async (task/cron/webhook já validado), documentado na docstring do service.
4. Capturar `DomainError` e **traduzir** para o protocolo dela. Não reinterpretar a regra.
5. O core não importa nada delas. Precisa de algo externo → **port**. Precisa de efeito pós-commit → **evento** (`dispatch`).
6. Adaptadores (api, integrations, ai-mcp) **podem** chamar tasks da backend-async diretamente com `delay_on_commit`. Só o core é obrigado a usar `dispatch()`.

---

## 2. Tabela de convenções (única)

| Tema | Padrão da casa |
|---|---|
| Nome de service | `<entidade>_<ação>` → `order_approve`, `customer_create`, `invoice_send` |
| Nome de selector | `<entidade>_list_for`, `<entidade>_get`, `<entidade>_get_detail` |
| Nome de task | `<entidade>_<ação>_task` → `invoice_send_task` (espelha o service) |
| Nome de evento | `<entidade>.<fato_no_passado>` → `order.approved` |
| Parâmetros | só keyword (`*,`), **IDs** e primitivos. Nunca instância de model vinda de fora |
| Usuário | `settings.AUTH_USER_MODEL` / `get_user_model()` — app `accounts`. Nunca `"users.User"` |
| Tenant | `common.tenancy`: `TenantModel`, `tenant_id_of(actor)`, `scope_to_tenant(qs, actor)`. Selector nunca recebe `tenant_id` de fora |
| Correlation | nome único **`correlation_id`** (ContextVar em `common/logging.py`). Header HTTP `X-Request-ID` (entrada e saída). Task recebe em `headers`, integração envia no header |
| Error code | `MAIÚSCULAS_COM_UNDERSCORE`, estável, em inglês (`ORDER_INVALID_TRANSITION`, `AI_OUTPUT_INVALID`) |
| Falha técnica | `common.errors.TransientError` / `PermanentError` — hierarquia única |
| Retry | **uma camada**: em task, o retry é da task (`autoretry_for=(TransientError,)`), client sem retry. Em request síncrona, client com no máx. 2 tentativas e só para operação idempotente |
| Status de processamento | `common.jobs.ProcessingStatus` (`pending/processing/completed/failed/canceled/ignored`) |
| Grafia | `canceled` (um L) em todo lugar |
| Money | `Decimal`, 2 casas; na API trafega como **string** (`"123.45"`) |
| Datas | ISO 8601 com offset na API; `timezone.now()` no código |
| Confirmação humana | ação destrutiva/financeira pedida por agente → `PendingAction` (BE-04). Pela API humana → ação nomeada + confirmação no app |

---

## 3. backend-api (BE-02)

Responsável por: autenticação (JWT para o Expo), serializers, views, paginação, OpenAPI +
geração do client TS, versionamento, CORS, throttling, **middleware de correlation id**,
`/health/`.

Formato de erro **único** (corpo de toda resposta 4xx/5xx):

```json
{
  "error": {
    "code": "ORDER_INVALID_TRANSITION",
    "message": "Transição de status inválida para o pedido.",
    "fields": {},
    "details": {"current": "canceled", "target": "approved"}
  }
}
```

= `{"error": exc.to_dict()}`. O Expo decide pelo `code`, nunca pela `message`.

Tradução obrigatória (um único exception handler, que **importa** de `common.exceptions` e
`common.errors` — nunca redefine as classes):

| Exceção | HTTP |
|---|---|
| `NotFoundError` | 404 |
| `PermissionDeniedError` | 403 |
| `ValidationError` (domínio) e `django.core.exceptions.ValidationError` | **422** |
| erro de formato do serializer (DRF `ValidationError`) | 400 `VALIDATION_ERROR` |
| `ConflictError` | 409 |
| `BusinessRuleError` | 422 |
| `DomainError` (outros) | 400 |
| `TransientError` | 503 (`Retry-After` se houver) |
| `PermanentError` | 502 |
| qualquer outra | 500 `INTERNAL_ERROR`, sem stack; logada com `correlation_id` |

400 = o JSON veio no formato errado. 422 = o formato está certo, mas o domínio recusou.

Padrão da view: serializer valida **formato** → chama service/selector com kwargs e IDs →
serializa saída. Validação de **regra** fica no service.

```python
def post(self, request, order_id):
    order = services.order_approve(actor=request.user, order_id=order_id)
    return Response(OrderDetailSerializer(order).data)
```

---

## 4. backend-async (BE-03)

Responsável por: Celery, filas, retries, agendamentos, idempotência de tasks, **implementação
do port `event_bus`** (`apps/jobs/bus.py` → `CeleryEventBus`), transactional outbox quando
necessário.

```python
# dentro de um service do core
transaction.on_commit(lambda: dispatch("order.approved", order_id=order.pk))
```

- O `CeleryEventBus` lê `settings.EVENT_HANDLERS = {"order.approved": ["apps.sales.tasks.order_notify_task"]}` e enfileira cada task, propagando `correlation_id`.
- Payload só com **IDs e primitivos**: a task relê o estado atual via selector.
- Task chama service; sem usuário → service de sistema documentado (`actor=None`).
- Task idempotente: rodar 2× não duplica efeito (constraint/`idempotency_key` no core).
- Retry só `TransientError`. `PermanentError` e `DomainError` → marca falha, sem retry.

---

## 5. backend-ai-mcp (BE-04)

Responsável por: providers de LLM/embeddings, prompts, RAG, agentes, tools MCP, `AIRun`, `AIJob`, `PendingAction`.

- Providers de IA são registrados em `settings.AI_PROVIDERS` (nome → dotted path) e escolhidos por caso de uso em `settings.AI_MODELS` — mesmo princípio do `PORTS` (implementação trocada por settings, nunca import direto do SDK), com um nível a mais porque cada caso de uso escolhe provider/modelo. O core não chama LLM: chama um AI service (`apps/ai/services.py`) quando precisa.
- Tool MCP = adaptador fino sobre service/selector existente, chamado com `actor=principal.user`. Autorização é a do core (`require_perm` no service, visibilidade no selector) — a tool não reimplementa.
- Se a tool precisa de regra nova, a regra nasce no core primeiro.
- Ação destrutiva/financeira pedida por agente → cria `PendingAction`; um humano confirma pela API; só então o service roda.
- Resultado de erro devolvido ao modelo = `DomainError.to_dict()` (o `code` ajuda o agente a se corrigir).
- Chamada ao LLM **nunca** dentro de `transaction.atomic`.
- Erros de IA são `DomainError` com code em MAIÚSCULAS (`AI_OUTPUT_INVALID`, `AI_BUDGET_EXCEEDED`, `AI_INSUFFICIENT_CONTEXT`); falha do provider é `TransientError`/`PermanentError`.
- **Não** pertence à BE-05: provider de LLM é da BE-04. Servidor MCP de terceiro que é porta de entrada de um sistema externo → cliente na BE-05.

---

## 6. backend-integrations (BE-05)

Responsável por: clientes HTTP de terceiros, **webhooks de entrada e de saída (dono único)**,
gateways de pagamento, WhatsApp (Evolution API), e-mail/SMS, **push (Expo Push)**,
**storage (MinIO/S3, `FileAsset`, URLs pré-assinadas)**.

- Implementa os **ports declarados no core** (`apps/<app>/ports.py`) em `apps/integrations/<provider>/adapter.py` e registra em `settings.PORTS`. Não declara `Protocol` próprio para o domínio importar.
- `IntegrationError` herda de `TransientError`/`PermanentError`. O service decide o que isso significa no domínio.
- Webhook de entrada = adaptador de entrada: valida assinatura, persiste `WebhookEvent` (dedupe por `external_event_id`), responde 2xx rápido, processa em task que chama service do core.
- Nenhuma regra de negócio no client/adapter. Rede fora da transação.

---

## 7. devops (OPS-01, transversal — backend e frontend)

Operação não é da família BE: é da skill **devops**, que vale para backend e frontend.
O stack Django está em `devops/stacks/backend-django/` (Dockerfile com `ROLE=web|worker|beat`,
gunicorn, migrate só na api, `/health/live/` e `/health/ready/` com `release`, `worker_health`,
Sentry, cache Redis DB 1 / broker DB 0).

Pontos de contato com a família BE:

- **Ambientes:** dev (local) · hom (`develop`) · prod (`main`). hom e prod usam o mesmo
  `config.settings.production`; a diferença é só env (`APP_ENV=hom|prod`).
- **`APP_ENV`** é a única forma de o código saber o ambiente — e ele não deve ramificar regra
  de negócio por ele. Comportamento diferente vem de configuração.
- **`OUTBOUND_ALLOWLIST`** (obrigatória fora de prod): adapters da BE-05 que enviam e-mail,
  WhatsApp, SMS ou push checam `outbound_allowed(destino)` e não enviam fora da lista.
- **Migrations** passam primeiro por hom e precisam ser compatíveis com o código anterior
  (expandir → migrar → contrair), porque api nova e app nativo antigo convivem.
- **Release** = tree hash de `backend/`, embutido na imagem; aparece em `/health` e no Sentry.
- Health check nunca chama provider externo; chave de cache de dado de tenant inclui o tenant.

---

## 8. Anti-exemplos (reprovar em code review)

```python
# ❌ view escrevendo direto
Order.objects.filter(pk=pk).update(status="approved")

# ❌ task com regra de negócio própria
if order.total > 1000 and not order.customer.is_vip: ...

# ❌ service chamando HTTP dentro da transação
@transaction.atomic
def order_approve(...):
    requests.post("https://gateway/charge", ...)

# ❌ core importando adaptador ou task
from apps.integrations.asaas.adapter import AsaasPaymentGateway   # em apps/billing/services.py
from apps.notifications.tasks import send_email_task               # em apps/sales/services.py

# ❌ handler da API redefinindo exceções do core
class DomainError(Exception): ...   # em config/api/exception_handler.py

# ❌ selector recebendo tenant de fora
customer_list_for(tenant_id=request.data["tenant_id"])

# ❌ hierarquia paralela de erro transitório
class TemporaryIntegrationError(Exception): ...
```
