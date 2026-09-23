# Testes de API

Teste o comportamento HTTP e o contrato, não a implementação interna. A regra de negócio em si é testada na BE-01; aqui o foco é: status correto, payload correto, permissão correta, efeito correto no domínio.

## Cobertura mínima por endpoint

```text
sucesso
não autenticado        → 401 (ou fluxo definido)
sem permissão          → 403
objeto de outro tenant → 404
dados inválidos        → 400/422 com formato de erro padrão
recurso inexistente    → 404
conflito de estado     → 409
filtros                → retorna o subconjunto esperado
paginação              → count/next/previous/results
ações críticas         → efeito no domínio + repetição da chamada
```

## Teste de contrato

Para `POST /api/v1/customers/`, valide status, estrutura do JSON, campos obrigatórios, tipos, erros e efeito no domínio:

```python
@pytest.mark.django_db
def test_create_customer_returns_201_and_contract(api_client, user):
    api_client.force_authenticate(user)

    response = api_client.post(
        "/api/v1/customers/",
        {"name": "Acme", "email": "contato@acme.com"},
        format="json",
    )

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "name", "email", "created_at"}
    assert body["name"] == "Acme"
    assert Customer.objects.filter(email="contato@acme.com").exists()
```

Comparar o conjunto de chaves (`set(body)`) pega tanto campo removido quanto campo sensível adicionado sem querer.

## Teste de erro no formato padrão

```python
@pytest.mark.django_db
def test_duplicated_email_returns_409_with_stable_code(api_client, user, customer):
    api_client.force_authenticate(user)

    response = api_client.post(
        "/api/v1/customers/",
        {"name": "Outro", "email": customer.email},
        format="json",
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CUSTOMER_EMAIL_EXISTS"
```

O `code` é o que o app Expo usa para decidir a mensagem — teste-o explicitamente para que ninguém o renomeie sem perceber.

## Teste de permissão

Toda rota privada tem teste de autorização. Parametrize para não repetir:

```python
@pytest.mark.django_db
@pytest.mark.parametrize(
    "actor_fixture,expected",
    [("manager", 200), ("member_without_role", 403), (None, 401)],
)
def test_approve_order_permissions(api_client, request, order, actor_fixture, expected):
    if actor_fixture:
        api_client.force_authenticate(request.getfixturevalue(actor_fixture))

    response = api_client.post(f"/api/v1/orders/{order.id}/approve/")

    assert response.status_code == expected
```

## Teste de isolamento entre tenants

Obrigatório em sistema multiempresa — é a falha mais cara e a mais fácil de passar despercebida:

```python
@pytest.mark.django_db
def test_cannot_read_customer_from_another_tenant(api_client, user, other_tenant_customer):
    api_client.force_authenticate(user)
    response = api_client.get(f"/api/v1/customers/{other_tenant_customer.id}/")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CUSTOMER_NOT_FOUND"
```

## Teste de performance de lista

```python
@pytest.mark.django_db
def test_list_orders_has_constant_query_count(api_client, user, django_assert_num_queries):
    OrderFactory.create_batch(10, tenant=user.tenant)
    api_client.force_authenticate(user)

    with django_assert_num_queries(5):
        response = api_client.get("/api/v1/orders/")

    assert response.status_code == 200
```

Se o número de queries cresce com a quantidade de itens, há N+1.

## Teste de idempotência

Para pagamento, criação de pedido e importação: chame duas vezes com o mesmo
`Idempotency-Key` (ou identificador externo) e verifique que só houve um efeito.

```python
@pytest.mark.django_db
def test_create_payment_is_idempotent(api_client, manager, order):
    api_client.force_authenticate(manager)
    for _ in range(2):
        response = api_client.post(
            f"/api/v1/orders/{order.id}/payments/", {}, format="json", HTTP_IDEMPOTENCY_KEY="k-123"
        )
        assert response.status_code in (201, 200)

    assert Payment.objects.filter(order=order).count() == 1
```

Testes de **webhook** (assinatura, dedupe, resposta rápida) ficam na backend-integrations
(`assets/templates/test_integration.py`).

## Teste do formato de erro e do correlation id

```python
def test_error_envelope_is_stable(api_client, manager):
    api_client.force_authenticate(manager)
    body = api_client.post("/api/v1/customers/", {}, format="json").json()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message", "fields", "details"}


def test_request_id_is_echoed(api_client, manager):
    api_client.force_authenticate(manager)
    response = api_client.get("/api/v1/customers/", HTTP_X_REQUEST_ID="req-1")
    assert response["X-Request-ID"] == "req-1"
```
