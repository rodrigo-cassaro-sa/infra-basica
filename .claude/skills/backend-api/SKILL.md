---
name: backend-api
description: Padrão BE-02 da software house para construir, revisar e documentar APIs Django REST Framework em projetos desacoplados (backend separado do frontend Expo — app iOS/Android e web). Use sempre que a tarefa envolver endpoint, rota, serializer, view/ViewSet, router, permissão de API, paginação, filtro, ordenação, formato de erro, exception handler, OpenAPI/drf-spectacular, upload, download, autenticação JWT/login/refresh, client TypeScript gerado do OpenAPI, catálogo de error codes, idempotência, versionamento /api/v1/, CORS, throttling ou testes de API — mesmo que o usuário não cite "BE-02", "DRF" ou "REST" explicitamente. Use também para revisar PR de API, definir contrato antes de implementar, avaliar se uma mudança quebra compatibilidade e rodar o checklist de Definition of Done da camada HTTP.
---

# BE-02 — backend-api

Padrão para expor o domínio por API em projetos Django desacoplados.

## Escopo e fronteiras

| Camada | O que é | Onde mora |
|---|---|---|
| BE-01 backend-core | models, services, selectors, validators, exceções de domínio, transações | `apps/<módulo>/models.py`, `services.py`, `selectors.py` |
| **BE-02 backend-api** | **HTTP: rotas, serializers, views, permissões, contratos, OpenAPI, erros** | `apps/<módulo>/api/` |
| BE-03 backend-async | filas, tasks assíncronas, workers | fora desta skill |
| BE-05 backend-integrations | **webhooks** (recebidos/enviados), storage/MinIO, push | a API só monta a rota |

Convenções comuns (erro, nomes, tenant, correlation id): `backend-core/references/contratos-entre-skills.md`.
Em caso de divergência, vale o contrato.

Se a tarefa pede regra de negócio nova (cálculo, transição de estado, validação que depende de outros registros), ela pertence à BE-01: crie/ajuste o service ou selector e deixe a API apenas chamando. Se BE-01 não existir no projeto, ainda assim isole a regra em `services.py`/`selectors.py` antes de escrever a view.

## Princípio central

A API não é o domínio. A camada HTTP precisa ser substituível sem reescrever regra de negócio.

```text
HTTP → DRF (serializer/view/permission) → service | selector → domínio → PostgreSQL
```

Consequência prática: se uma view tem mais de ~15 linhas de lógica, ou importa vários models para orquestrar, a regra está no lugar errado.

## Fluxo de trabalho

Siga nesta ordem. Pular a etapa 1 é a causa mais comum de retrabalho.

1. **Contrato antes do código.** Preencha o template de `references/contrato.md` (método, URL, auth, permissão, entrada, saída, status, erros, efeitos, idempotência, paginação, filtros). Referencie a história DAH (H-xxx). Confirme com quem consome a API (app Expo) antes de implementar.
2. **Esqueleto.** Crie/ajuste os arquivos em `apps/<módulo>/api/` seguindo a estrutura abaixo.
3. **Serializers** de entrada e saída separados.
4. **View pequena** chamando service (escrita) ou selector (leitura).
5. **Permissões** explícitas, incluindo checagem por objeto/tenant quando aplicável.
6. **Testes** de sucesso, erro, permissão e contrato — ver `references/testes.md`.
7. **OpenAPI** conferido e **client TS do Expo regenerado** (`references/cliente-expo.md`).
8. **Checklists** de `references/checklists.md` antes de considerar pronto.

## Stack

`Django`, `Django REST Framework`, `djangorestframework-simplejwt`, `django-cors-headers`, `PostgreSQL`, `drf-spectacular`, `django-filter`, `pytest`. Dependências entram no `pyproject.toml` do core (bloco BE-02). Adicione outra dependência só quando houver necessidade concreta — justifique no PR.

## Estrutura de arquivos

```text
apps/customers/
├── api/
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py   # normalmente vazio — autorização é do service
│   ├── filters.py
│   └── schemas.py
├── models.py
├── services.py
└── selectors.py
```

Só quebre em `api/v1/serializers/`, `api/v1/views/` etc. quando o módulo realmente crescer. Não antecipe complexidade.

## Rotas

Toda API pública é versionada: `/api/v1/...`. Nova versão só para mudança incompatível; campo novo opcional ou endpoint novo não cria `/api/v2/`.

REST para recursos:

```text
GET    /api/v1/customers/          list
POST   /api/v1/customers/          create
GET    /api/v1/customers/{id}/     retrieve
PATCH  /api/v1/customers/{id}/     update parcial
DELETE /api/v1/customers/{id}/     delete
```

Nada de `/getCustomers`, `/createCustomer`, `/updateCustomer`.

Ações de domínio viram sub-recurso com `POST`, porque expressam a transição melhor que um PATCH genérico:

```text
POST /api/v1/orders/{id}/approve/
POST /api/v1/orders/{id}/cancel/
POST /api/v1/users/{id}/block/
```

`DELETE` só quando o significado for realmente remover. Cancelar, arquivar ou inativar são transições de negócio — use ação nomeada.

**ViewSet ou APIView:** ViewSet + router quando o recurso for CRUD convencional e as URLs previsíveis ajudarem. `APIView`/`GenericAPIView` quando o fluxo é específico, a ação tem semântica própria ou a clareza é maior. Não force ViewSet por obrigação.

## Serializers

Responsabilidade: entrada, validação **estrutural**, serialização, contrato. Regra de negócio fica no service.

Separe por uso em vez de um serializer universal cheio de `if`:

```text
CustomerCreateSerializer
CustomerUpdateSerializer
CustomerListSerializer
CustomerDetailSerializer
```

```python
class CustomerCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
```

**Mass assignment:** o serializer declara explicitamente o que entra. Nunca `Model.objects.create(**request.data)` nem `ModelSerializer` com `fields = "__all__"` em recurso que tenha campo interno, financeiro, de status ou de permissão.

**Saída:** retorne só o que o cliente precisa. Revise cada serializer de saída procurando senha/hash, token, chave de API, segredo, flag administrativa, campo interno e dado pessoal desnecessário.

## Views

A view coordena HTTP e nada mais:

```python
class CustomerCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CustomerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer = customer_create(
            actor=request.user,
            **serializer.validated_data,
        )

        return Response(
            CustomerDetailSerializer(customer).data,
            status=status.HTTP_201_CREATED,
        )
```

Roteamento de responsabilidade:

```text
POST / PATCH / DELETE / ação  →  service
GET list / retrieve           →  selector
```

Nomes seguem o core: `customer_create`, `order_approve`, `customer_list_for`, `customer_get`.
A view passa **IDs** (`customer_id=...`), nunca a instância do model.

Selector devolve queryset já escopado (tenant via `scope_to_tenant`) e com `select_related`/`prefetch_related` adequados — a view não monta filtro de autorização à mão e não usa `get_object_or_404`: `customer_get` já lança `CustomerNotFound` → 404.
Para listas, use `GenericAPIView`/`ListAPIView` (são elas que têm `paginate_queryset`), com `get_queryset()` chamando o selector.

## Status HTTP e erros

`200` `201` `202` `204` · `400` `401` `403` `404` `409` `422` `429` · `500` `502` `503`. Erro de negócio nunca volta como `200`.

Formato único de erro da família (`{"error": exc.to_dict()}`), com `code` estável em MAIÚSCULAS:

```json
{
  "error": {
    "code": "CUSTOMER_EMAIL_EXISTS",
    "message": "Já existe um cliente com este e-mail.",
    "fields": {"email": ["E-mail já cadastrado."]},
    "details": {}
  }
}
```

| Origem | HTTP |
|---|---|
| serializer (formato) | 400 `VALIDATION_ERROR` |
| `NotFoundError` / `PermissionDeniedError` | 404 / 403 |
| `ValidationError` de domínio / `BusinessRuleError` | 422 |
| `ConflictError` | 409 |
| `TransientError` / `PermanentError` (provider, IA) | 503 / 502 |
| não tratada | 500 `INTERNAL_ERROR` |

A mensagem pode mudar; o `code` não muda sem necessidade, porque o app Expo depende dele para decidir comportamento. Todo code novo vai para o catálogo (`references/cliente-expo.md`).

A tradução fica em **um** exception handler central que **importa** as classes de `common.exceptions` e `common.errors` — nunca as redefine. Não espalhe `try/except` pelas views. Handler pronto em `assets/exception_handler.py`.

## Autenticação

JWT (simplejwt) para todo o Expo: access 15 min, refresh 30 dias rotativo com blacklist, `/auth/me/`
devolvendo permissões para o app montar a UI. Endpoints, código e contrato do lado do app:
`references/autenticacao.md`.

## Segurança

Negue por padrão e leia `references/seguranca.md` antes de qualquer endpoint que envolva multitenant, upload, download privado, webhook, login ou integração externa. Resumo do que não pode faltar:

- autenticação definida globalmente; endpoint público é marcado como público de forma explícita;
- `permission_classes` sempre presente — `IsAuthenticated` é o piso, não o teto;
- autorização de ação é `require_perm` **no service** (core); a API não duplica;
- ID válido não significa acesso: escopo de tenant/dono **no selector** (`scope_to_tenant`); `tenant_id` nunca vem do request;
- CORS restrito às origens do Expo web; CSRF só no Admin (API é JWT);
- throttling em login, recuperação de senha, criação de conta, endpoints públicos e operações caras.

## Listagem, filtros e performance

Detalhes e exemplos em `references/listagem.md`. Regras que não se negociam:

- toda lista é paginada (`count`/`next`/`previous`/`results`), com paginação padrão global;
- filtros por query param, declarativos com `django-filter`;
- ordenação e busca restritas a campos permitidos e indexados;
- sem N+1: nada de serializer que consulta por item nem nested profundo sem necessidade.

## Idempotência e concorrência

Endpoints de pagamento, criação de pedido, importação e integração precisam decidir explicitamente o comportamento em chamada repetida — aceite `Idempotency-Key` ou use identificador externo único. Duas requisições simultâneas são normais: `if not exists: create()` sem constraint única ou transação é bug esperando acontecer, e a proteção real vem da BE-01.

Processo demorado não segura requisição aberta: devolva um recurso/job (`202` + identificador, job herdando `common.jobs.ProcessingStateModel`) e deixe a execução para a BE-03. O app acompanha por polling (`references/cliente-expo.md`).

**Webhooks** não são implementados aqui: dono é a BE-05 (`backend-integrations/references/webhooks.md`). A API só inclui as urls dela em `/api/v1/webhooks/<provider>/`.

## Observabilidade

A BE-02 é dona do `CorrelationIdMiddleware` (`assets/correlation_middleware.py`): lê/gera `X-Request-ID`, grava em `common.logging.correlation_id` e devolve no header. Nome no log: `correlation_id`. Logue método, rota, status, duração, usuário quando apropriado e erro — sem despejar corpo completo. Health: `/health/live/` (processo de pé) e `/health/ready/` (banco ok) sem informação sensível — implementação em `devops/stacks/backend-django/health.py`.

## OpenAPI e compatibilidade

Schema com `drf-spectacular` em `/api/schema/` e `/api/docs/`, exportado para `openapi.yaml` e usado para **gerar o client TS do Expo** (orval/openapi-typescript). Documentação divergente do comportamento real conta como bug. Para cada endpoint crítico registre entrada, saída de sucesso, erros possíveis, permissões e efeitos.

Antes de alterar um contrato existente, classifique a mudança:

- **compatível:** campo opcional novo, endpoint novo, filtro opcional novo;
- **incompatível:** remover ou renomear campo, mudar tipo, mudar semântica, tornar campo obrigatório.

App nativo publicado fica meses em versão antiga: para iOS/Android toda mudança incompatível exige nova versão ou janela longa. Incompatível exige plano: marcar deprecated, documentar substituto, definir janela de migração, monitorar uso e só então remover. Ver `references/versionamento.md`.

## Nomes

Código em inglês, consistente para a mesma entidade: `customer` em todo lugar — nunca misturar `cliente`, `cust`, `cli`.

## Anti-padrões

```text
❌ regra de negócio na view
❌ serializer gigante com condicionais para todos os casos
❌ HTTP 200 para erro
❌ endpoint sem autenticação por acidente
❌ autorização filtrada só no frontend
❌ lista sem paginação
❌ CORS aberto sem necessidade
❌ CSRF desativado por conveniência
❌ fields = "__all__" em recurso sensível
❌ retornar dado sensível na resposta
❌ webhook implementado na camada de API (é da BE-05)
❌ exception handler redefinindo DomainError
❌ tenant_id lido do request
❌ get_object_or_404 no lugar do selector do core
❌ chamada pesada bloqueando a API
❌ documentação divergente do comportamento
```

## Definition of Done

Pronto quando: API versionada; client TS do Expo regenerado; code novo no catálogo; URLs consistentes; contratos definidos e documentados; regra de negócio fora das views; serializers com responsabilidade clara; services/selectors reutilizados; autenticação e autorização explícitas; listas paginadas; filtros controlados; erros em formato único; OpenAPI fiel; nenhum dado sensível exposto; idempotência e concorrência consideradas nos endpoints críticos; testes de sucesso, erro e permissão; lint e suíte passando.

Resultado esperado: ao abrir qualquer API da casa, o dev identifica em minutos qual é a versão, o contrato, o serializer de entrada, a view, o service, o selector, a permissão, os erros possíveis, os testes e o OpenAPI.

## Arquivos de apoio

| Arquivo | Quando ler |
|---|---|
| `references/contrato.md` | antes de implementar qualquer endpoint |
| `references/autenticacao.md` | login, refresh, logout, /me, reset de senha, JWT no Expo |
| `references/cliente-expo.md` | OpenAPI → client TS, catálogo de error codes, polling/SSE, convenções de payload |
| `references/seguranca.md` | permissões por objeto, multitenant, CORS/CSRF, throttling, uploads, downloads |
| `references/listagem.md` | list endpoints, filtros, ordenação, busca, paginação, performance |
| `references/versionamento.md` | mudar contrato existente, deprecar, API pública vs interna |
| `references/testes.md` | escrever ou revisar testes de API |
| `references/checklists.md` | fechar endpoint, fechar API, revisar PR |
| `assets/exception_handler.py` | montar o handler central de erros |
| `assets/correlation_middleware.py` | middleware X-Request-ID → correlation_id |
| `assets/settings_api.py` | configurar DRF, paginação, throttling, spectacular |
| `assets/endpoint_template.py` | scaffold de serializers + view + urls |
| `assets/test_endpoint_template.py` | scaffold de testes |
