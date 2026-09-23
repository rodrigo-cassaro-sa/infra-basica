"""
Template: apps/integrations/crm/tests/test_client.py

Cobre a matriz obrigatória: timeout, 429, 5xx, 4xx, payload inválido,
idempotência, camada única de retry, correlation id, hierarquia de erros da
família e webhook (duplicado, assinatura, replay, task). São exatamente os casos que quebram em
produção e que ninguém testa por padrão.

Requer: pytest, respx (mock em nível HTTP para httpx).
Mockar o adapter inteiro pula justamente o código que tem risco.
"""

from __future__ import annotations

import httpx
import pytest
import respx

from apps.integrations.base.client import RetryPolicy, TimeoutPolicy
from apps.integrations.base.exceptions import (
    IntegrationInvalidResponse,
    IntegrationRateLimited,
    IntegrationTimeout,
    IntegrationUnavailable,
    IntegrationValidationError,
)
from apps.integrations.crm.client import CRMClient

BASE_URL = "https://crm.test"


@pytest.fixture
def client() -> CRMClient:
    return CRMClient(
        base_url=BASE_URL,
        auth_headers={"Authorization": "Bearer test"},
        timeout=TimeoutPolicy(connect=1, read=1, write=1, pool=1),
        retry=RetryPolicy(max_attempts=3, base_delay=0.01, max_delay=0.05),
    )


# --------------------------------------------------------------------------
# Caminho feliz
# --------------------------------------------------------------------------


@respx.mock
def test_sucesso(client):
    respx.get(f"{BASE_URL}/v1/contacts/1").mock(
        return_value=httpx.Response(200, json={"id": "1"})
    )
    assert client.fetch_contact(contact_id="1") == {"id": "1"}


# --------------------------------------------------------------------------
# Falhas transitórias → repetem
# --------------------------------------------------------------------------


@respx.mock
def test_timeout_vira_integration_timeout(client):
    respx.get(f"{BASE_URL}/v1/contacts/1").mock(
        side_effect=httpx.ReadTimeout("timeout")
    )
    with pytest.raises(IntegrationTimeout):
        client.fetch_contact(contact_id="1")


@respx.mock
def test_5xx_repete_ate_o_limite(client):
    route = respx.get(f"{BASE_URL}/v1/contacts/1").mock(
        return_value=httpx.Response(503)
    )
    with pytest.raises(IntegrationUnavailable):
        client.fetch_contact(contact_id="1")
    assert route.call_count == 3  # respeita max_attempts, não tenta para sempre


@respx.mock
def test_5xx_seguido_de_sucesso(client):
    respx.get(f"{BASE_URL}/v1/contacts/1").mock(
        side_effect=[httpx.Response(502), httpx.Response(200, json={"id": "1"})]
    )
    assert client.fetch_contact(contact_id="1") == {"id": "1"}


@respx.mock
def test_429_respeita_retry_after(client, monkeypatch):
    dormiu: list[float] = []
    monkeypatch.setattr(
        "apps.integrations.base.client.time.sleep", lambda s: dormiu.append(s)
    )
    respx.get(f"{BASE_URL}/v1/contacts/1").mock(
        return_value=httpx.Response(429, headers={"Retry-After": "2"})
    )
    with pytest.raises(IntegrationRateLimited):
        client.fetch_contact(contact_id="1")
    # usou o valor do provider, não o backoff próprio
    assert all(delay == 2 for delay in dormiu)


# --------------------------------------------------------------------------
# Falhas permanentes → NÃO repetem
# --------------------------------------------------------------------------


@respx.mock
def test_400_nao_repete(client):
    route = respx.get(f"{BASE_URL}/v1/contacts/1").mock(
        return_value=httpx.Response(400, json={"error": "bad request"})
    )
    with pytest.raises(IntegrationValidationError):
        client.fetch_contact(contact_id="1")
    assert route.call_count == 1  # repetir devolveria o mesmo erro


@respx.mock
def test_200_com_json_invalido(client):
    respx.get(f"{BASE_URL}/v1/contacts/1").mock(
        return_value=httpx.Response(200, content=b"<html>erro</html>")
    )
    with pytest.raises(IntegrationInvalidResponse):
        client.fetch_contact(contact_id="1")


# --------------------------------------------------------------------------
# Idempotência
# --------------------------------------------------------------------------


@respx.mock
def test_idempotency_key_estavel_entre_tentativas(client):
    chaves: list[str] = []

    def capturar(request: httpx.Request) -> httpx.Response:
        chaves.append(request.headers.get("Idempotency-Key", ""))
        if len(chaves) == 1:
            return httpx.Response(503)
        return httpx.Response(200, json={"id": "abc"})

    respx.put(f"{BASE_URL}/v1/contacts").mock(side_effect=capturar)
    client.upsert_contact(payload={"id": "abc"}, idempotency_key="crm:contact:abc:upsert")

    # a MESMA chave em toda tentativa — chave aleatória por retry não protege nada
    assert len(set(chaves)) == 1


# --------------------------------------------------------------------------
# Segurança: segredo não vaza em log
# --------------------------------------------------------------------------


def test_headers_sensiveis_mascarados():
    from apps.integrations.base.client import mask_headers

    mascarado = mask_headers({"Authorization": "Bearer segredo", "Accept": "json"})
    assert mascarado["Authorization"] == "***"
    assert mascarado["Accept"] == "json"


# --------------------------------------------------------------------------
# Webhook: duplicidade e assinatura
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_webhook_duplicado_processa_uma_vez(client_django, webhook_payload, assinar):
    headers = assinar(webhook_payload)

    primeira = client_django.post(
        "/api/v1/webhooks/provider/", data=webhook_payload,
        content_type="application/json", **headers,
    )
    segunda = client_django.post(
        "/api/v1/webhooks/provider/", data=webhook_payload,
        content_type="application/json", **headers,
    )

    assert primeira.status_code == 202
    assert segunda.status_code == 200
    assert segunda.json()["status"] == "duplicate"


@pytest.mark.django_db
def test_webhook_com_assinatura_invalida_e_rejeitado(client_django, webhook_payload):
    resposta = client_django.post(
        "/api/v1/webhooks/provider/",
        data=webhook_payload,
        content_type="application/json",
        HTTP_X_PROVIDER_SIGNATURE="assinatura-errada",
        HTTP_X_PROVIDER_TIMESTAMP="1700000000",
    )
    assert resposta.status_code == 401


@pytest.mark.django_db
def test_webhook_antigo_e_rejeitado_replay(client_django, webhook_payload, assinar):
    headers = assinar(webhook_payload, timestamp=1)  # 1970
    resposta = client_django.post(
        "/api/v1/webhooks/provider/", data=webhook_payload,
        content_type="application/json", **headers,
    )
    assert resposta.status_code == 401


# --------------------------------------------------------------------------
# Contratos da família (backend-core/references/contratos-entre-skills.md)
# --------------------------------------------------------------------------


def test_excecoes_seguem_hierarquia_unica():
    from common.errors import PermanentError, TransientError

    assert issubclass(IntegrationTimeout, TransientError)
    assert issubclass(IntegrationRateLimited, TransientError)
    assert issubclass(IntegrationValidationError, PermanentError)
    assert not issubclass(IntegrationValidationError, TransientError)


@respx.mock
def test_padrao_do_client_nao_repete(settings):
    """Padrão = 1 tentativa: quem repete é a task (BE-03)."""
    rota = respx.get(f"{BASE_URL}/v1/contacts/1").mock(return_value=httpx.Response(503))
    padrao = CRMClient(base_url=BASE_URL)
    with pytest.raises(IntegrationUnavailable):
        padrao.fetch_contact(contact_id="1")
    assert rota.call_count == 1


@respx.mock
def test_escrita_sem_idempotency_key_nunca_repete(client):
    rota = respx.post(f"{BASE_URL}/v1/notes").mock(return_value=httpx.Response(503))
    with pytest.raises(IntegrationUnavailable):
        client.request("POST", "/v1/notes", json={"text": "x"})
    assert rota.call_count == 1  # mesmo com RetryPolicy(max_attempts=3)


@respx.mock
def test_correlation_id_vai_para_o_provider(client):
    from common.logging import correlation_id

    rota = respx.get(f"{BASE_URL}/v1/contacts/1").mock(return_value=httpx.Response(200, json={"id": "1"}))
    token = correlation_id.set("req-42")
    try:
        client.fetch_contact(contact_id="1")
    finally:
        correlation_id.reset(token)
    assert rota.calls.last.request.headers["X-Request-ID"] == "req-42"


@pytest.mark.django_db
def test_task_de_webhook_erro_permanente_nao_repete(mocker, webhook_event):
    from apps.integrations.provider.webhooks import (
        WEBHOOK_HANDLERS,
        WebhookEvent,
        process_webhook_event_task,
    )

    mocker.patch.dict(
        WEBHOOK_HANDLERS,
        {webhook_event.event_type: mocker.Mock(side_effect=IntegrationValidationError("x"))},
    )
    process_webhook_event_task.apply(kwargs={"event_id": webhook_event.pk}, throw=True)
    webhook_event.refresh_from_db()
    assert webhook_event.status == "failed"
    assert webhook_event.attempts == 1
