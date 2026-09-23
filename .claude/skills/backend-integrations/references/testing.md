# Testes de integração externa

Índice: Pirâmide · Unitários · Contract tests · Sandbox · Fixtures · Matriz obrigatória · Mocks realistas · Fake provider · Desenvolvimento local

---

## O que testar em cada nível

| Nível | O que cobre | Rede |
|---|---|---|
| Unitário | adapter, mapeamento, assinatura, parsing, política de retry | não |
| Contract test | o client fala com a API real/sandbox e o schema continua válido | sim, isolado |
| Integração interna | service + adapter fake, fluxo completo do nosso lado | não |

O adapter é onde mora a maior parte do risco e é barato de testar — comece por ele.

## Unitários

Teste o adapter com payload fixo e verifique o modelo interno resultante. Teste a tradução de erro: dado um 429 do provider, o client levanta `IntegrationRateLimited`?

Assinatura HMAC se testa com vetor determinístico: entrada fixa → assinatura esperada fixa.

## Contract tests

Para integração crítica, tenha teste que valida o contrato contra a API real ou sandbox:

```text
chamar endpoint → validar schema da resposta → falhar se mudou
```

Rode fora do pipeline principal (agendado, ou em job separado) para não acoplar o deploy à disponibilidade do terceiro. O valor é descobrir a mudança do provider antes do cliente descobrir.

## Sandbox

Use o ambiente de homologação do provider antes de produção. Documente como obter credencial de sandbox no README da integração — isso economiza meio dia de cada pessoa nova no time.

## Fixtures externas

Guarde respostas reais (anonimizadas) como fixture. Elas envelhecem: quando um contract test falhar, atualize a fixture junto com o adapter.

## Matriz obrigatória de testes

Toda integração relevante cobre:

```text
[ ] sucesso
[ ] timeout                  → IntegrationTimeout, retry aplicado conforme política
[ ] 429 com Retry-After      → espera correta, não estoura tentativas
[ ] 5xx                      → IntegrationUnavailable, retry limitado
[ ] 4xx de validação         → sem retry
[ ] payload inválido em 200  → IntegrationInvalidResponse
[ ] idempotência             → segunda chamada não duplica efeito
[ ] webhook duplicado        → processa uma vez só
[ ] assinatura inválida      → rejeita, não processa
[ ] assinatura expirada      → rejeita (replay)
[ ] OAuth: token expirado    → refresh e repete uma vez
```

Esses são exatamente os casos que quebram em produção e que ninguém testa por padrão.

## Mocks realistas

Mock que sempre devolve 200 não testa nada. O mock precisa reproduzir o comportamento real do provider: os códigos de erro que ele usa, o formato de erro dele, os headers de rate limit.

Prefira interceptar no nível HTTP (`respx` para httpx, `responses` para requests) a mockar o adapter inteiro — mockar o adapter pula justamente o código que tem risco.

## Fake provider

Implementação da interface interna que roda em memória:

```python
class FakeEmailGateway:
    def __init__(self):
        self.sent = []

    def send(self, *, to: str, subject: str, body: str) -> str:
        self.sent.append((to, subject, body))
        return "fake-message-id"
```

Serve para teste de service e para desenvolvimento local. É o benefício concreto de ter interface interna: o domínio nem percebe.

## Desenvolvimento local

Ninguém deve precisar de credencial de produção para rodar o projeto. Ofereça:

- fake provider ativado por configuração (`EMAIL_PROVIDER=fake`);
- `X_ENABLED=false` desligando a integração;
- instruções de sandbox quando o teste real for necessário;
- túnel (ngrok e similares) documentado para receber webhook localmente.
