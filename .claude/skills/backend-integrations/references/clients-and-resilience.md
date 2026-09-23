# Clients e resiliência

Índice: HTTP client · Timeout · Retry · Backoff e jitter · Camada do retry · Exceções · Status HTTP · Rate limit · Bulkhead · Circuit breaker · Fallback · Feature flags · Health check · Degradação · Batch · Protocolos não-REST · Limites de payload

---

## HTTP client

Padronize uma biblioteca só. `httpx` é a escolha para backends novos, por oferecer interface síncrona e assíncrona com a mesma API. `requests` é aceitável no legado. Não misture as duas sem necessidade.

Um client por integração, construído uma vez com base URL, auth e timeout:

```python
import httpx


class CRMClient:
    def __init__(self, *, base_url: str, api_key: str, timeout: float):
        self.client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )
```

Use `assets/base/client.py` como base — ele já resolve timeout, retry, backoff, jitter, `Retry-After` e tradução de erro.

## Timeout

Toda chamada externa tem timeout. Sem exceção. Chamada sem timeout é worker travado esperando um terceiro que talvez nunca responda.

Configure as quatro dimensões quando o perfil exigir: `connect`, `read`, `write`, `pool`.

Timeout é **por integração**, não global:

```text
API rápida            → timeout curto (2–5s)
relatório remoto      → timeout maior
upload de arquivo     → timeout específico de write
```

Em fluxo síncrono, respeite o **timeout budget**: a soma dos timeouts das chamadas externas não pode ultrapassar o tempo que a request HTTP do app pode durar. Se ultrapassar, a operação é assíncrona.

## Retry

Retry existe para falha **transitória**.

| Repetir | Não repetir |
|---|---|
| timeout | 400 request inválida |
| connection reset | 401 autenticação |
| 429 rate limit | 403 autorização |
| 502 / 503 / 504 | 422 validação |
| | erro de regra de negócio |

Repetir um 400 só gera carga e ruído — a resposta será a mesma.

### Retry + idempotência

```text
POST /charge → timeout → retry → 2 cobranças?
```

Nunca adicione retry em escrita sem avaliar duplicidade. Mecanismos, na ordem de preferência:

1. `Idempotency-Key` do provider, com chave **estável** por operação: `payment:{payment_id}:create`. Chave aleatória a cada tentativa não protege nada.
2. External operation id verificado antes de reenviar.
3. Unique constraint do nosso lado.

Para cobrança, estorno, pagamento e transferência, idempotência é obrigatória — não opcional.

## Backoff e jitter

Espera progressiva entre tentativas:

```text
1s → 2s → 4s → 8s
```

Não bombardeie serviço já indisponível.

Adicione **jitter** (aleatoriedade na espera) para evitar que dezenas de workers repitam no mesmo instante. Sem jitter, uma falha massiva vira efeito manada quando o provider volta.

## A camada certa do retry

Regra da família (fixa, não é escolha por projeto):

```text
chamada dentro de task (padrão)      → RetryPolicy() = 1 tentativa; retry é da task
                                        (autoretry_for=(TransientError,), BE-03)
chamada síncrona dentro de request   → RetryPolicy.for_request() = 2 tentativas curtas,
                                        só leitura ou escrita com idempotency_key
```

O `BaseHTTPClient` **nunca** repete POST/PUT/PATCH/DELETE sem `idempotency_key`, mesmo que a
política permita. O erro comum era ter os dois: client 3x dentro de task 5x = 15 chamadas.

## Exceções de integração

Hierarquia padrão (em `apps/integrations/base/exceptions.py`), pendurada na hierarquia
**única** de falhas técnicas da família (`common/errors.py` do core):

```text
InfrastructureError (common.errors)
├── TransientError ── IntegrationTimeout, IntegrationUnavailable, IntegrationRateLimited
└── PermanentError ── IntegrationAuthenticationError, IntegrationAuthorizationError,
                      IntegrationValidationError, IntegrationConflict,
                      IntegrationInvalidResponse, IntegrationNotFound, IntegrationDisabled
(todas também herdam de IntegrationError)
```

Consequência: task da BE-03 com `autoretry_for=(TransientError,)` cobre integração e IA; a API
traduz `TransientError` → 503 e `PermanentError` → 502 sem vazar detalhe do provider.

Fluxo de tradução:

```text
provider exception → integration exception → service
```

Exceção de SDK não circula pelo domínio. Se o service faz `except stripe.error.CardError`, o acoplamento já aconteceu.

## Status HTTP

Interprete explicitamente. Tratar "qualquer coisa diferente de 200" como o mesmo erro impede retry correto e diagnóstico.

```text
200/201 → sucesso
204     → sucesso sem conteúdo
400     → request inválida       → IntegrationValidationError
401     → autenticação           → IntegrationAuthenticationError
403     → autorização            → IntegrationAuthorizationError
404     → recurso inexistente
409     → conflito               → IntegrationConflict
429     → rate limit             → IntegrationRateLimited
5xx     → falha do provider      → IntegrationUnavailable
```

### Resposta inválida com HTTP 200

Valide o payload mesmo em 200: campo faltando, tipo errado, JSON inválido, schema inesperado → `IntegrationInvalidResponse`.

## Rate limit

Toda integração considera rate limit. Registre os headers quando existirem: `limit`, `remaining`, `reset`, `retry-after`.

Quando o provider responder 429 com `Retry-After`, use esse valor — ele é mais confiável que o nosso backoff.

Para API com limite conhecido (ex.: 100 req/min), controle throughput na origem: fila dedicada, worker dedicado ou rate limiter via BE-03. É melhor enfileirar do que colecionar 429.

## Bulkhead

Separe integrações críticas em filas/workers próprios.

```text
WhatsApp lento não pode bloquear pagamentos
```

Uma integração degradada consumindo todos os workers derruba as outras. BE-03 define as filas.

## Circuit breaker

Estados: `closed` → `open` → `half-open`.

Aplique quando falha persistente de um provider causar efeito cascata (fila entupida, latência acumulada). **Não adicione por padrão** se retry com backoff já resolve — circuit breaker mal calibrado derruba integração saudável.

## Fallback

Só quando for semanticamente seguro.

```text
e-mail provider A → provider B          geralmente OK
gateway financeiro A → gateway B        exige desenho explícito
```

Trocar de gateway no meio de uma cobrança pode gerar cobrança dupla, conciliação impossível e problema regulatório. Fallback financeiro é decisão de produto, não detalhe técnico.

Todo fallback é auditável: registre qual provider atendeu cada operação.

## Feature flags

Integração nova entra gradualmente quando o risco justificar:

```text
NEW_CRM_SYNC_ENABLED
PAYMENT_PROVIDER_V2_ENABLED
```

Toda integração deve ter mecanismo de desligar (`X_ENABLED`) sem deploy.

## Health check

Não chame todas as integrações a cada `/health/` — isso transforma o health check numa dependência externa cara e faz o serviço cair porque um terceiro caiu.

Separe:

```text
health interno          → o processo está vivo
readiness               → banco/cache próprios
integration diagnostics → endpoint específico, sob demanda
```

## Dependência indisponível e degradação graciosa

Defina o comportamento antes da falha acontecer:

- a operação falha e o usuário vê erro claro?
- a operação é enfileirada para depois?
- o sistema opera em modo reduzido?

Integração opcional (analytics, enriquecimento de dados) não pode derrubar o fluxo principal. Integração obrigatória (pagamento) deve falhar de forma explícita — nunca silenciosa.

## Batch APIs

Quando o provider oferece batch, prefira a operação em lote a N chamadas individuais. Trate erro parcial: um item do lote falhar não significa o lote inteiro falhar. Persista o resultado por item.

## Protocolos além de REST

- **GraphQL**: query em módulo isolado, schema de resposta validado igual a REST. Erros vêm em `errors` com HTTP 200 — trate isso explicitamente.
- **SOAP/XML**: parser seguro (desabilite entidades externas — XXE), mapeamento para schema interno na borda.
- **WebSocket externo**: reconexão com backoff, heartbeat, e política para mensagem perdida.
- **Polling**: intervalo configurável, cursor/checkpoint, e limite. Polling sem controle vira rate limit.

## Limites de payload

Limite tamanho de request e response. Response gigante inesperada consome memória do worker.

Cuidado com compression bombs: valide tamanho descomprimido antes de expandir.
