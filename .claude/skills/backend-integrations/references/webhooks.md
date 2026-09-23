# Webhooks

Índice: Webhook recebido · Assinatura · Raw body · Replay · Idempotência · Resposta rápida · Modelo WebhookEvent · Ordem e duplicidade · Webhook perdido · Webhook enviado · Outbox · Inbox

---

## Webhook recebido é entrada não confiável

Trate como request pública hostil, porque é exatamente isso: uma URL aberta na internet que qualquer um pode chamar.

Fluxo obrigatório:

```text
request
 ↓
validar assinatura
 ↓
validar schema
 ↓
persistir evento
 ↓
responder rápido (200/202)
 ↓
processar assíncrono (BE-03)
```

## Verificar assinatura

Quando o provider oferece assinatura criptográfica, ela é a autenticação. Não se contente com:

```text
IP de origem
User-Agent
URL secreta
```

URL secreta vaza em log, em proxy, em histórico de browser. Assinatura HMAC não.

### Raw body

Vários esquemas calculam a assinatura sobre os **bytes originais** do corpo. Se o framework já desserializou e reserializou o JSON, a assinatura não bate — espaçamento e ordem de chave mudam.

Em Django, leia `request.body` antes de qualquer parse e verifique a assinatura sobre ele.

### Replay attack

Quando o provider suportar, valide `timestamp`, `nonce` ou `event_id`, e rejeite eventos antigos demais (janela típica: 5 minutos). Sem isso, um payload capturado pode ser reenviado indefinidamente.

Use comparação de tempo constante (`hmac.compare_digest`) — comparação com `==` vaza informação por timing.

## Idempotência

Persista o identificador do evento do provider com unicidade:

```text
evento recebido
 ↓
external_event_id já existe?
 ├─ sim → responde sucesso (idempotente), não reprocessa
 └─ não → persiste e processa
```

Duplicidade é comportamento normal de sistema distribuído, não anomalia. Provider reenvia quando não recebe 200 a tempo, mesmo que a gente tenha processado.

## Responder rápido

Não execute trabalho pesado antes de responder. O provider tem timeout curto (geralmente 5–30s) e vai reenviar — gerando duplicidade e, no pior caso, uma avalanche.

```text
validar → persistir → commit → enqueue → 200/202
```

Processar 5.000 registros dentro do handler do webhook é anti-pattern.

## Modelo recomendado

```text
WebhookEvent(ProcessingStateModel)       ← base comum da família (common/jobs.py)
├── provider
├── external_event_id     (unique com provider)
├── event_type
├── payload / payload_hash
└── herdados: status (pending, processing, completed, failed, ignored),
              attempts, started_at, finished_at, last_error, correlation_id, created_at
```

Implementação completa (model, services, view, task) em `assets/templates/webhook.py`.
**Esta skill é a dona única de webhooks** — BE-02 só inclui a rota em
`/api/v1/webhooks/<provider>/`, BE-03 só executa a task.

Armazene o payload completo apenas quando a política de dados permitir — payload de webhook frequentemente contém PII.

## Ordem dos eventos

Não assuma ordem de chegada:

```text
evento 2 chega antes do evento 1
```

Projete para isso: use versão, timestamp do evento ou consulte o estado atual no provider antes de aplicar uma transição. "Pagamento aprovado" chegando depois de "pagamento estornado" não pode reabrir a cobrança.

## Webhook perdido

Webhook é entrega best-effort. Quando o evento é crítico, combine:

```text
webhook (rápido) + sync periódico (garantia)
```

A reconciliação recupera o que se perdeu e detecta divergência silenciosa.

---

## Webhooks que nós enviamos

Quando o nosso backend notifica terceiros (inclusive integrações do próprio cliente):

```text
Outbox → dispatcher → HTTP → retry
```

### Modelo

```text
OutgoingWebhook
├── id
├── event_type
├── destination
├── status              (pending, delivered, failed)
├── attempts
├── next_attempt_at
├── last_status_code
└── last_error
```

### Assinar nossos webhooks

```text
timestamp + "." + raw_body → HMAC-SHA256 → header de assinatura
```

Documente o procedimento de verificação para quem consome. Se a gente exige assinatura dos providers, entrega assinatura também.

### Retry de envio

Repita para timeout, 429 e 5xx, com backoff. Não repita indefinidamente: defina limite de tentativas.

### Dead endpoint

Estourado o limite, marque `failed`, gere alerta e dê visibilidade operacional. Endpoint de cliente que morreu há três semanas não pode continuar consumindo worker.

---

## Transactional Outbox

Para publicar evento externo com alta confiabilidade:

```text
transaction
├── altera domínio
└── grava OutgoingWebhook / OutboxEvent   (mesma transação, mesmo commit)

dispatcher (task periódica) → envia → marca completed
```

Não crie um outbox novo por integração: o mecanismo genérico (`OutboxEvent` + dispatcher) é da
**backend-async** (`backend-async/references/event-bus.md` §4). Para webhooks enviados, use
`OutgoingWebhook` (`assets/templates/sync_models.py`), criado na mesma transação pelo service e
entregue por task. Use quando o risco justificar — nem toda notificação precisa disso.

## Inbox Pattern

Espelho do outbox, para entrada confiável e idempotente:

```text
evento externo → WebhookEvent (inbox) → task → service do core
```

O `WebhookEvent` **é** o inbox da casa — não criar um `IncomingEvent` separado.

Serve para deduplicação, auditoria e reprocessamento — os três problemas que aparecem em toda integração por webhook depois de alguns meses em produção.
