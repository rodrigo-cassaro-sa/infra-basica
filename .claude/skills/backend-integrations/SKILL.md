---
name: backend-integrations
description: Padrão BE-05 da software house para integrar backends Django/Python com sistemas externos de forma desacoplada. Use SEMPRE que a tarefa envolver qualquer comunicação com sistema de terceiro — API REST/GraphQL/SOAP, webhook (recebido ou enviado), gateway de pagamento, WhatsApp (Evolution API), e-mail transacional, push notification (Expo Push), ERP, CRM, storage/MinIO/S3/upload de arquivos, SMS, serviço fiscal ou bancário, servidor MCP de terceiro, OAuth, API key, sincronização, importação/exportação de dados externos, retry, timeout, rate limit, idempotência ou circuit breaker. Use também quando o desenvolvedor escrever requests/httpx/SDK de terceiro em código de domínio, quando pedir "integrar com X", "consumir a API de X", "receber webhook de X", "sincronizar com X", ou quando for expor estado de integração para o app. Provider de LLM/embeddings NÃO é desta skill (é da backend-ai-mcp). Vale mesmo que a pessoa não cite arquitetura, adapter ou BE-05.
---

# BE-05 — Backend Integrations

Padrão da casa para integrar backends Django com sistemas externos de forma segura, previsível, testável e substituível.

A premissa: **o backend é desacoplado do frontend Expo** (app iOS/Android e painel web — "painel" nesta skill = esse frontend). O app é só mais um consumidor da API. Nenhum provider externo pode vazar para dentro do domínio, e nenhum provider externo pode vazar para dentro do app.

Convenções comuns (ports, erros, retry, correlation id, status de job): `backend-core/references/contratos-entre-skills.md` — em divergência, vale o contrato.

**Esta skill é dona de:** clients/adapters de terceiros, **webhooks** (recebidos e enviados, `WebhookEvent` = inbox), storage (`FileAsset`, presigned URLs), push (Expo Push), WhatsApp/e-mail/SMS.

## Regra de ouro

```text
SERVICE DECIDE
ADAPTER TRADUZ
CLIENT ENVIA
SISTEMA EXTERNO RESPONDE
```

```text
DOMÍNIO → SERVICE → PORT (Protocol no core) ──get_port()──▶ ADAPTER → CLIENT → SISTEMA EXTERNO
```

O domínio nunca conhece URL, token, header, SDK, payload do provider, retry ou timeout. Esses detalhes pertencem à borda.

E o inverso também vale: **o provider não define o domínio**. Se o Stripe muda o nome de um campo, isso morre no adapter.

## Quando esta skill se aplica

Qualquer código que atravesse a fronteira do processo em direção a um sistema de terceiro: REST, GraphQL, SOAP, webhooks, SMTP/API de e-mail, WhatsApp, gateways de pagamento, ERP, CRM, storage, mapas/geocoding, SMS, serviços fiscais, bancários, identidade, MCP externo (quando é porta de entrada de um sistema de terceiro), push, storage, SaaS em geral.

Não se aplica a: banco de dados próprio, cache próprio, fila própria (BE-01/BE-03), provider de LLM/embeddings (BE-04).

## Dependências entre skills

| Skill | Papel |
|---|---|
| BE-01 backend-core | domínio, services, selectors, permissions, transações. BE-05 **não** duplica regra de negócio |
| BE-02 backend-api | expõe a integração para o app (`POST /api/v1/integrations/crm/sync/`) com auth e permissão; inclui as rotas de webhook desta skill |
| BE-03 backend-async | executa sync, retry, webhooks, importação, exportação, processos longos |
| BE-04 backend-ai-mcp | consome BE-05 quando a IA precisa acessar sistema externo; providers de LLM são dela |

---

## Fluxo obrigatório para uma nova integração

Siga na ordem. Pular etapa aqui é o que gera integração impossível de operar depois.

**1. Definir o contrato antes do código.** Objetivo da integração, fonte da verdade (nosso sistema? o provider? bidirecional?), e se a operação é síncrona ou assíncrona. Sem fonte da verdade definida, sincronização vira conflito.

**2. Declarar o port no core** (`apps/<app>/ports.py`, `Protocol` + DTOs). O nome é do nosso negócio, não do provider: `EmailGateway`, não `ResendService`. O port **mora no core**; esta skill importa de lá — nunca o contrário.

**3. Criar o client** — comunicação técnica pura (HTTP, headers, auth, timeout, retry, status, serialização). Herde de `BaseHTTPClient` (ver `assets/base/client.py`).

**4. Criar o adapter** — implementa o port; tradução entre modelo interno e modelo externo. É onde vive o mapeamento de campos, enums, datas e moeda. **Registrar em `settings.PORTS`** (`"payment_gateway": "apps.integrations.asaas.adapter.AsaasPaymentGateway"`). Sem função `get_xxx()` de composição própria.

**5. Configuração fora do código.** `CRM_BASE_URL`, `CRM_API_KEY`, `CRM_TIMEOUT`, `CRM_ENABLED`. Uma base URL por integração, segredo nunca no Git, credencial de homologação nunca igual à de produção.

**6. Definir resiliência explicitamente.** Timeout (sempre), retry (só para falha transitória), backoff, jitter, rate limit, idempotência. Ver `references/clients-and-resilience.md`.

**7. Traduzir erros.** Exceção do SDK morre no client e vira `IntegrationError` (ou subclasse), que já herda de `common.errors.TransientError`/`PermanentError`. O service nunca faz `except httpx.HTTPError`.

**8. Observabilidade e testes.** Métricas por provider, logs sem segredo, contract tests para integração crítica, sandbox usado antes de produção.

Antes de considerar pronto, rode a checklist de `references/checklists.md`.

---

## Estrutura de pastas

```text
backend/
├── apps/
│   └── integrations/
│       ├── base/
│       │   ├── exceptions.py     # IntegrationError e subclasses
│       │   ├── client.py         # BaseHTTPClient (timeout, retry, backoff, tradução de erro)
│       │   └── schemas.py
│       │
│       ├── asaas/                # nome do PROVIDER (a capacidade é o port no core)
│       │   ├── client.py         # fala HTTP
│       │   ├── adapter.py        # implementa apps/billing/ports.py:PaymentGateway
│       │   ├── schemas.py        # pydantic das respostas externas
│       │   ├── webhooks.py       # WebhookEvent handlers + view (se o provider manda webhook)
│       │   ├── tasks.py
│       │   └── tests/
│       │
│       ├── evolution/            # WhatsApp
│       ├── expo_push/
│       ├── storage/              # MinIO/S3
│       └── webhooks/urls.py      # incluído pela BE-02 em /api/v1/webhooks/
```

O que não é aceitável é espalhar `requests.post()` pelos `services.py` nem o core importar qualquer coisa de `apps/integrations/`.

## Client versus Adapter

| | Client | Adapter |
|---|---|---|
| Responsabilidade | comunicação técnica | tradução de modelo |
| Conhece | HTTP, headers, auth, timeout, retry, status | `Customer` ↔ `ExternalCRMContact` |
| Não conhece | o que é um Customer | que existe HTTP |

## Port (no core)

O domínio depende disto — nunca do provider:

```python
# apps/notifications/ports.py (CORE)
from typing import Protocol


class EmailGateway(Protocol):
    def send(self, *, to: str, subject: str, body: str) -> str:
        ...
```

```python
# config/settings/base.py
PORTS["email_gateway"] = "apps.integrations.resend.adapter.ResendEmailGateway"

# no service do core (fora de atomic, ou em task disparada por evento)
get_port("email_gateway").send(to=..., subject=..., body=...)
```

```text
EmailGateway
├── ResendAdapter
├── SESAdapter
└── SMTPAdapter
```

Provider muda, domínio permanece. Se trocar de provider exige tocar em `services.py`, a interface está errada.

Imports como `from stripe import ...`, `from resend import ...`, `from twilio import ...` ficam restritos ao módulo da integração. Nunca em módulo de domínio.

---

## Síncrono ou assíncrono

Decida explicitamente, por operação:

| Use síncrono quando | Use assíncrono (BE-03) quando |
|---|---|
| o usuário precisa do resultado agora | o resultado pode chegar depois |
| a operação é rápida e barata | volume alto, lote, importação, exportação |
| falhar significa falhar a request | falhar deve gerar retry controlado |

Padrão preferido para escrita externa:

```text
service (core) → commit → dispatch("evento") → EVENT_HANDLERS → task (BE-03) → adapter → provider
```

Nunca chamar API externa dentro de transação longa: os locks ficam abertos durante a latência do terceiro. E `transaction.atomic()` **não** desfaz operação já realizada em sistema externo — se precisar de compensação, modele uma Saga explicitamente.

---

## Contrato com o app (Expo)

O backend é desacoplado; o app consome só a API. Isso impõe regras próprias:

- **O app nunca fala com o provider.** Nada de token de terceiro no frontend, nada de chamada direta do navegador para o gateway. Toda integração passa pelo backend, com autenticação e permissão de BE-02.
- **Consistência eventual precisa ser representável na tela.** Exponha `sync_status` (`pending`, `synced`, `failed`, `outdated`), `last_synced_at` e `last_sync_error` nos recursos que dependem de integração. O app precisa conseguir mostrar "aguardando confirmação do provider" sem mentir para o usuário.
- **Erros externos chegam traduzidos.** O app recebe `{"error": {"code": "INTEGRATION_UNAVAILABLE", ...}}` (503/502 pelo handler da BE-02), não resposta crua do provider nem stack trace de SDK.
- **Ações operacionais são endpoints, não acesso ao banco.** Reprocessar sync, reenviar webhook, desabilitar integração — tudo via API com permissão, para que app e ferramenta administrativa usem o mesmo caminho.
- **Segredo nunca trafega para o app.** Nem na API, nem no Django Admin. No máximo `********abcd`.
- **Endpoint de webhook é do backend.** Rota `/api/v1/webhooks/<provider>/`, autenticada por assinatura, fora do JWT do app.
- **Upload direto no storage.** O app envia arquivo para o MinIO por URL pré-assinada emitida pela API (`references/storage.md`).

---

## Regras inegociáveis

1. **Toda chamada externa tem timeout.** `httpx.get(url)` sem política de timeout é risco de travar worker. Configure `connect`, `read`, `write`, `pool` conforme o perfil da integração — API rápida e relatório pesado não usam o mesmo número.
2. **Retry só para falha transitória.** Sim: timeout, connection reset, 429, 502, 503, 504. Não: 400, 401, 403, 422, regra de negócio inválida.
3. **Retry de escrita exige idempotência avaliada.** `POST /charge` + timeout + retry pode virar duas cobranças. Use idempotency key estável (`payment:{id}:create`), external operation id ou unique constraint. Chave aleatória a cada tentativa não é idempotência.
4. **Retry tem teto.** `while True` sem política de parada não existe aqui.
5. **Retry mora em uma camada só.** Padrão: a task (BE-03, `autoretry_for=(TransientError,)`) e o client com 1 tentativa. Request síncrona: `RetryPolicy.for_request()`. O client nunca repete escrita sem `idempotency_key`.
6. **Erro externo vira exceção nossa** antes de subir para o service.
7. **HTTP 200 não é garantia.** Valide o payload com schema; campo faltando ou tipo errado gera erro controlado.
8. **hom não fala com gente de verdade.** Adapter que envia e-mail, WhatsApp, SMS ou push checa `outbound_allowed(destino)` (`OUTBOUND_ALLOWLIST`, obrigatória fora de prod — skill devops) e só registra, sem enviar, quando o destino não está na lista. Credencial de hom é sempre sandbox.
9. **Segredo não vai para log.** Nunca `Authorization: Bearer ...` em log, nem refresh token.
10. **Nunca aceite URL arbitrária do usuário** para o backend acessar (SSRF). Sem `POST /fetch-url`.
11. **Webhook é entrada não confiável.** Valide assinatura, deduplique, responda rápido.

---

## Anti-patterns

| Anti-pattern | Correção |
|---|---|
| `requests.post(...)` em `services.py` | port no core + adapter aqui |
| core importando `apps.integrations...` / `get_xxx()` de composição | `get_port()` + `settings.PORTS` |
| signal disparando integração | `dispatch()` + `EVENT_HANDLERS` |
| SDK externo definindo tipos do domínio | schema interno no adapter |
| `Customer.stripe_customer_id` quando há multi-gateway | mapping table `(provider, external_id)` |
| retry infinito | limite + backoff + jitter |
| chamada sem timeout | timeout explícito por integração |
| logar token | mascarar/omitir |
| webhook pesado processado antes de responder | persistir + enfileirar + 200 |
| assumir que o webhook chega uma única vez e na ordem | dedupe por `external_event_id` + reconciliação |
| sync sem checkpoint | `last_cursor` / `last_updated_at` persistido |
| `/health/` chamando todas as integrações | separar health interno, readiness e diagnostics |

---

## Templates prontos

Copie e adapte — não reescreva do zero:

- `assets/base/exceptions.py` — hierarquia `IntegrationError` (pendurada em `common.errors`)
- `assets/base/client.py` — `BaseHTTPClient` com timeout, retry, backoff, jitter, `Retry-After` e tradução de erro
- `assets/templates/integration_module.py` — port (core) + client + schemas + adapter + registro em PORTS
- `assets/templates/webhook.py` — model `WebhookEvent` (ProcessingStateModel), services, view com assinatura HMAC e dedupe, task com retry só para `TransientError`
- `assets/templates/sync_models.py` — `ExternalMapping`, `SyncState`, `OutgoingWebhook`
- `assets/templates/test_integration.py` — testes de timeout, 429, 5xx, payload inválido, idempotência e webhook duplicado

## Referências

Leia o arquivo correspondente quando a tarefa entrar no assunto:

| Arquivo | Quando ler |
|---|---|
| `references/clients-and-resilience.md` | timeout, retry, backoff, jitter, rate limit, circuit breaker, bulkhead, fallback, feature flag, batch |
| `references/webhooks.md` | receber ou enviar webhook, assinatura, replay, dedupe, inbox/outbox |
| `references/sync-and-data.md` | paginação, importação, checkpoint, fonte da verdade, external ID, mapeamento, enums, datas, dinheiro, arquivos |
| `references/auth-and-security.md` | OAuth, API key, assinatura de request, segredos, rotação, certificados, SSRF, TLS, PII, multi-tenant |
| `references/observability-and-ops.md` | métricas, logs, correlation ID, tracing, auditoria, alertas, runbook, admin, SLA |
| `references/storage.md` | upload/download, MinIO/S3, `FileAsset`, URL pré-assinada |
| `references/push.md` | push notification (Expo Push), registro de device, receipts |
| `references/testing.md` | testes unitários, contract tests, sandbox, fake provider, fixtures, desenvolvimento local |
| `references/checklists.md` | fechar a tarefa: checklists de integração, webhook, sync, segurança, operação e Definition of Done |

---

## Definition of Done

A integração está pronta quando o domínio não conhece o provider, client/adapter estão isolados, configuração está fora do código, segredos protegidos, timeout definido, retries limitados e conscientes, idempotência avaliada, rate limit considerado, respostas validadas, erros traduzidos, fonte da verdade definida, sync com checkpoint quando necessário, webhooks com assinatura e deduplicação, processamento pesado em BE-03, logs sem segredo, métricas que detectam falha, contract tests para o que é crítico, sandbox usado, segurança de rede revisada e runbook escrito quando a integração for crítica.

A lista completa e verificável está em `references/checklists.md`.

## Resultado esperado

Ao abrir qualquer backend da casa, um desenvolvedor descobre rapidamente: quais integrações existem, qual provider está em uso, onde está o client, onde está o adapter, qual timeout se aplica, qual retry existe, como funciona idempotência e paginação, como webhooks são validados, como a sincronização é retomada, onde ficam os external IDs, como falhas são observadas, como reprocessar e como trocar de provider.

```text
DOMÍNIO NÃO CONHECE PROVIDER
PROVIDER NÃO DEFINE O DOMÍNIO
```

A integração é uma borda substituível do sistema.
