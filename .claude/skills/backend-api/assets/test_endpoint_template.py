"""
Scaffold de testes de API (BE-02) — apps/customers/tests/test_api_customers.py

Cobre o mínimo exigido: sucesso, contrato, validação, autenticação, permissão,
isolamento entre tenants, filtros, paginação e performance.
"""

import pytest
from django.urls import reverse

from apps.customers.models import Customer

pytestmark = pytest.mark.django_db


# --------------------------------------------------------- sucesso e contrato
def test_create_customer_returns_201_and_expected_contract(api_client, manager):
    api_client.force_authenticate(manager)

    response = api_client.post(
        reverse("customers:customer-list"),
        {"name": "Acme", "email": "contato@acme.com"},
        format="json",
    )

    assert response.status_code == 201
    body = response.json()
    # Comparar o conjunto de chaves pega campo removido E campo sensível novo.
    assert set(body) == {"id", "name", "email", "status", "created_at"}
    assert Customer.objects.filter(email="contato@acme.com").exists()


# ------------------------------------------------------------------- validação
def test_create_customer_with_invalid_email_returns_400_in_standard_format(api_client, manager):
    api_client.force_authenticate(manager)

    response = api_client.post(
        reverse("customers:customer-list"),
        {"name": "Acme", "email": "not-an-email"},
        format="json",
    )

    assert response.status_code == 400
    error = response.json()["error"]
    # Formato único da família: {"error": {"code","message","fields","details"}}
    assert set(error) == {"code", "message", "fields", "details"}
    assert error["code"] == "VALIDATION_ERROR"
    assert "email" in error["fields"]


# ------------------------------------------------------- autenticação/permissão
@pytest.mark.parametrize(
    "actor_fixture,expected_status",
    [("manager", 201), ("member_without_role", 403), (None, 401)],
)
def test_create_customer_permissions(api_client, request, actor_fixture, expected_status):
    if actor_fixture:
        api_client.force_authenticate(request.getfixturevalue(actor_fixture))

    response = api_client.post(
        reverse("customers:customer-list"),
        {"name": "Acme", "email": "contato@acme.com"},
        format="json",
    )

    assert response.status_code == expected_status


# ------------------------------------------------------------ isolamento tenant
def test_cannot_deactivate_customer_from_another_tenant(api_client, manager, other_tenant_customer):
    api_client.force_authenticate(manager)

    response = api_client.post(
        reverse("customers:customer-deactivate", args=[other_tenant_customer.id])
    )

    # 404 e não 403: não confirmamos a existência de registro de outro tenant.
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CUSTOMER_NOT_FOUND"
    other_tenant_customer.refresh_from_db()
    assert other_tenant_customer.status == "active"


# ------------------------------------------------------- listagem e performance
def test_list_customers_is_paginated_and_scoped(api_client, manager, customer_factory, other_tenant_customer):
    customer_factory.create_batch(30, tenant=manager.tenant)
    api_client.force_authenticate(manager)

    response = api_client.get(reverse("customers:customer-list"))

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"count", "next", "previous", "results"}
    assert len(body["results"]) == 25
    assert other_tenant_customer.id not in [item["id"] for item in body["results"]]


def test_list_customers_has_constant_query_count(
    api_client, manager, customer_factory, django_assert_num_queries
):
    customer_factory.create_batch(10, tenant=manager.tenant)
    api_client.force_authenticate(manager)

    with django_assert_num_queries(4):  # ajuste ao baseline real do projeto
        api_client.get(reverse("customers:customer-list"))


def test_list_customers_filter_by_status(api_client, manager, customer_factory):
    customer_factory.create_batch(3, tenant=manager.tenant, status="active")
    customer_factory.create_batch(2, tenant=manager.tenant, status="inactive")
    api_client.force_authenticate(manager)

    response = api_client.get(reverse("customers:customer-list"), {"status": "active"})

    assert response.json()["count"] == 3


# ------------------------------------------------------------------- conflito
def test_duplicated_email_returns_409_with_stable_code(api_client, manager, customer):
    api_client.force_authenticate(manager)

    response = api_client.post(
        reverse("customers:customer-list"),
        {"name": "Outro", "email": customer.email},
        format="json",
    )

    assert response.status_code == 409
    # O code é contrato com o app Expo: renomear quebra o consumidor.
    assert response.json()["error"]["code"] == "CUSTOMER_EMAIL_EXISTS"


# ------------------------------------------------- regra de domínio → 422
def test_business_rule_violation_returns_422(api_client, manager, customer, monkeypatch):
    """BusinessRuleError / ValidationError de domínio → 422 (formato ok, domínio recusou)."""
    from apps.customers import services
    from common.exceptions import BusinessRuleError

    def boom(**kwargs):
        raise BusinessRuleError("Limite do plano atingido.", limit=10)

    monkeypatch.setattr(services, "customer_create", boom)
    monkeypatch.setattr("apps.customers.api.views.customer_create", boom)
    api_client.force_authenticate(manager)

    response = api_client.post(
        reverse("customers:customer-list"),
        {"name": "Acme", "email": "novo@acme.com"},
        format="json",
    )

    assert response.status_code == 422
    assert response.json()["error"]["details"] == {"limit": 10}


# -------------------------------------------------------- correlation id
def test_response_echoes_request_id(api_client, manager):
    api_client.force_authenticate(manager)
    response = api_client.get(reverse("customers:customer-list"), HTTP_X_REQUEST_ID="abc-123")
    assert response["X-Request-ID"] == "abc-123"
