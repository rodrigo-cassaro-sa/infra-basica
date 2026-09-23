# Segurança da API

## Autenticação x autorização

```text
autenticação → identifica o usuário
permissão    → autoriza a ação sobre o objeto
```

Defina autenticação globalmente em `REST_FRAMEWORK`. Endpoint público é exceção e precisa estar marcado de forma explícita (`permission_classes = [AllowAny]` com comentário do motivo), nunca público por esquecimento.

## Permissões

Negar por padrão. `DEFAULT_PERMISSION_CLASSES = ["rest_framework.permissions.IsAuthenticated"]`.

A autorização de **ação** é do core: `require_perm(actor, "app.codename")` dentro do service.
A API não repete essa checagem — senão API, task e tool MCP divergem. Permission class de DRF
só para barrar cedo algo que não depende do objeto (módulo desligado, papel mínimo para a rota).

Esconder botão no app Expo não é controle de acesso. Toda regra visível no frontend precisa ter correspondente no backend.

## Permissão por objeto e multitenant

Em sistema multiempresa, multitenant, portal, filial ou cliente/fornecedor: **ID válido não significa acesso autorizado**. Duas defesas complementares:

1. **Escopo no selector** (defesa principal, evita vazamento em lista e em detalhe). Fica no core,
   com `common.tenancy.scope_to_tenant` — a API só chama:

```python
# apps/customers/selectors.py (core)
def customer_list_for(*, actor) -> QuerySet[Customer]:
    return scope_to_tenant(Customer.objects.all(), actor).order_by("-created_at")


def customer_get(*, actor, customer_id: int) -> Customer:
    try:
        return customer_list_for(actor=actor).get(pk=customer_id)
    except Customer.DoesNotExist:
        raise CustomerNotFound(customer_id=customer_id) from None
```

Objeto de outro tenant vira `CustomerNotFound` → 404 pelo handler central — preferível a 403,
porque não confirma a existência do registro. Não use `get_object_or_404` na view: o selector já resolve.

2. Regra por objeto que depende de papel além do tenant (dono, responsável) → também no selector/service do core, não em `has_object_permission`.

Nunca carregue tudo e filtre no cliente. Nunca aceite `tenant_id` vindo do corpo, da query ou do header como fonte de verdade do escopo: o tenant sai do `actor` (usuário autenticado).

## CORS

Restritivo: apenas as origens do **Expo web** (produção e homologação). App nativo iOS/Android não passa por CORS. `*` em produção com credenciais ou dados privados é falha, não atalho. Liste as origens por ambiente via variável de ambiente.

## CSRF

Padrão da casa: **JWT no header `Authorization`** para todo o Expo (nativo e web) → CSRF não se
aplica à API. Sessão/cookie fica só para o Django Admin, que mantém CSRF ligado.
Desativar CSRF globalmente para "resolver" um erro é o caminho errado. Ver `autenticacao.md`.

## Throttling

Aplique onde o abuso é previsível ou caro: login, recuperação de senha, criação de conta, endpoints públicos, integrações e operações pesadas (relatórios, exportações, buscas amplas).

```python
"DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.ScopedRateThrottle"],
"DEFAULT_THROTTLE_RATES": {"login": "5/min", "public": "60/min"},
```

Throttling de aplicação não substitui proteção de infraestrutura (WAF, rate limit no edge) contra abuso volumétrico.

## Uploads

Valide sempre: tipo, extensão, MIME real, tamanho máximo, permissão do usuário, nome do arquivo e destino de armazenamento.

- Não confie no nome enviado — gere um nome próprio (UUID) e preserve o original só como metadado.
- Não confie na extensão nem no `Content-Type` declarado; verifique o conteúdo.
- Defina limite de tamanho explícito e rejeite antes de processar.
- Guarde em object storage (MinIO/S3), não no filesystem efêmero do container. Model `FileAsset`, upload direto por URL pré-assinada e storage em geral: dono é a **backend-integrations** (`references/storage.md`). A API só expõe os endpoints.

## Downloads

Verifique autorização **antes** de servir arquivo privado. URL difícil de adivinhar não é permissão. Para arquivos grandes, prefira URL assinada com expiração curta, gerada só depois da checagem de permissão.

## Webhooks (recebidos e enviados)

**Dono: backend-integrations (BE-05)** — model `WebhookEvent`, verificação de assinatura, dedupe,
inbox/outbox e processamento em task. A API só **monta a rota** em `api/v1/webhooks/<provider>/`
incluindo as urls da BE-05. Não implemente webhook nesta camada; siga
`backend-integrations/references/webhooks.md`.

## Dados sensíveis na resposta

Nunca devolva senha ou hash, token, chave de API, cookie, credencial de integração ou campo administrativo não autorizado. Revise os serializers de saída a cada PR — o vazamento típico vem de `ModelSerializer` com `fields = "__all__"` ou de nested serializer herdado sem revisão.

## Logs

Registre `correlation_id` (via `CorrelationIdMiddleware`, header `X-Request-ID`), método, rota, status, duração, usuário quando apropriado e erro. Não logue corpo completo indiscriminadamente: senhas, tokens e dados pessoais acabam em log retido por meses.
