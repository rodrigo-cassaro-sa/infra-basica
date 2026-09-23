"""
Template de uma integração completa: apps/integrations/crm/

Este arquivo reúne, para leitura, o conteúdo dos arquivos envolvidos.
Ao aplicar, separe em:

    apps/crm/ports.py                 → NO CORE (BE-01): Protocol + DTO que o domínio usa
    apps/integrations/crm/
    ├── schemas.py                    → contrato da resposta externa (pydantic)
    ├── client.py                     → HTTP
    ├── adapter.py                    → tradução; IMPLEMENTA o port do core
    └── tests/
    config/settings/base.py           → PORTS["customer_directory"] = "...CRMAdapter"

Direção de dependência (contratos-entre-skills.md):
    integrations → importa o port do core
    core         → NUNCA importa integrations; obtém com get_port("customer_directory")

Substitua "CRM" pelo nome da capacidade (não do fornecedor): o domínio depende
de CustomerDirectory, não de HubSpot.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol

from django.conf import settings
from pydantic import BaseModel, ValidationError

from apps.integrations.base.client import BaseHTTPClient, RetryPolicy, TimeoutPolicy
from apps.integrations.base.exceptions import (
    IntegrationDisabled,
    IntegrationInvalidResponse,
)

# ===========================================================================
# apps/crm/ports.py — NO CORE. Contrato interno estável que o domínio usa.
# (a integração importa daqui; o core nunca importa a integração)
# ===========================================================================


@dataclass(frozen=True)
class ContactData:
    """Modelo de transporte do NOSSO lado. Não é o payload do provider."""

    external_id: str
    name: str
    email: str | None
    phone: str | None
    lifetime_value: Decimal
    updated_at: datetime


class CustomerDirectory(Protocol):
    """
    Port declarado no core. Trocar de fornecedor não muda esta assinatura.

    O service do core faz (fora de transaction.atomic, ou numa task via evento):
        directory: CustomerDirectory = get_port("customer_directory")
        directory.upsert_contact(contact=...)
    """

    def get_contact(self, *, external_id: str) -> ContactData:
        ...

    def upsert_contact(self, *, contact: ContactData) -> str:
        ...

    def list_contacts_updated_since(
        self, *, since: datetime, cursor: str | None = None
    ) -> tuple[list[ContactData], str | None]:
        """Devolve (contatos, próximo cursor). Cursor None = fim."""
        ...


# ===========================================================================
# schemas.py — o que o provider devolve
# ===========================================================================


class ExternalContact(BaseModel):
    """Valida a resposta externa. Campo novo desconhecido é ignorado."""

    id: str
    full_name: str
    email_address: str | None = None
    phone_number: str | None = None
    ltv_cents: int = 0
    modified_at: datetime


class ExternalContactPage(BaseModel):
    results: list[ExternalContact]
    next_cursor: str | None = None


# ===========================================================================
# client.py — só HTTP
# ===========================================================================


class CRMClient(BaseHTTPClient):
    provider = "crm"

    @classmethod
    def from_settings(cls) -> "CRMClient":
        if not settings.CRM_ENABLED:
            raise IntegrationDisabled("CRM_ENABLED=false", provider=cls.provider)
        return cls(
            base_url=settings.CRM_BASE_URL,
            auth_headers={"Authorization": f"Bearer {settings.CRM_API_KEY}"},
            timeout=TimeoutPolicy(connect=3.0, read=settings.CRM_TIMEOUT),
            # Padrão da família: retry é da task (BE-03) → client com 1 tentativa.
            # Chamada síncrona dentro de request → RetryPolicy.for_request().
            retry=RetryPolicy(max_attempts=1),
        )

    def fetch_contact(self, *, contact_id: str) -> dict:
        return self.request(
            "GET", f"/v1/contacts/{contact_id}", operation="fetch_contact"
        )

    def upsert_contact(self, *, payload: dict, idempotency_key: str) -> dict:
        return self.request(
            "PUT",
            "/v1/contacts",
            operation="upsert_contact",
            json=payload,
            idempotency_key=idempotency_key,
        )

    def list_contacts(self, *, since: str, cursor: str | None) -> dict:
        params = {"updated_since": since}
        if cursor:
            params["cursor"] = cursor
        return self.request(
            "GET", "/v1/contacts", operation="list_contacts", params=params
        )


# ===========================================================================
# adapter.py — tradução nos dois sentidos
# ===========================================================================


class CRMAdapter:
    """
    Implementa CustomerDirectory.

    É o único lugar que conhece os nomes de campo do provider. Se o CRM renomear
    "full_name", a mudança termina aqui.
    """

    def __init__(self, client: CRMClient | None = None) -> None:
        self.client = client or CRMClient.from_settings()

    # ---- entrada: externo → interno ------------------------------------

    def get_contact(self, *, external_id: str) -> ContactData:
        raw = self.client.fetch_contact(contact_id=external_id)
        return self._to_internal(self._validate(raw, ExternalContact))

    def list_contacts_updated_since(
        self, *, since: datetime, cursor: str | None = None
    ) -> tuple[list[ContactData], str | None]:
        raw = self.client.list_contacts(
            since=since.astimezone().isoformat(), cursor=cursor
        )
        page = self._validate(raw, ExternalContactPage)
        return [self._to_internal(item) for item in page.results], page.next_cursor

    # ---- saída: interno → externo --------------------------------------

    def upsert_contact(self, *, contact: ContactData) -> str:
        payload = {
            "id": contact.external_id,
            "full_name": contact.name,
            "email_address": contact.email,
            "phone_number": contact.phone,
            # dinheiro em centavos: nunca float
            "ltv_cents": int(contact.lifetime_value * 100),
        }
        raw = self.client.upsert_contact(
            payload=payload,
            # chave estável: o mesmo contato gera a mesma chave em toda tentativa
            idempotency_key=f"crm:contact:{contact.external_id}:upsert",
        )
        return self._validate(raw, ExternalContact).id

    # ---- utilidades ----------------------------------------------------

    @staticmethod
    def _to_internal(external: ExternalContact) -> ContactData:
        return ContactData(
            external_id=external.id,
            name=external.full_name.strip(),
            email=(external.email_address or "").lower() or None,
            phone=normalize_phone(external.phone_number),
            lifetime_value=Decimal(external.ltv_cents) / 100,
            updated_at=external.modified_at,
        )

    def _validate(self, raw: object, schema: type[BaseModel]):
        """HTTP 200 com payload inesperado vira erro controlado."""
        try:
            return schema.model_validate(raw)
        except ValidationError as exc:
            raise IntegrationInvalidResponse(
                f"payload fora do schema {schema.__name__}: {exc.error_count()} erro(s)",
                provider=self.client.provider,
            ) from exc


def normalize_phone(value: str | None) -> str | None:
    """Normalização acontece na borda, não espalhada pelo domínio."""
    if not value:
        return None
    digits = "".join(ch for ch in value if ch.isdigit())
    return f"+{digits}" if digits else None


# ===========================================================================
# Registro — config/settings/base.py (sem função get_xxx() de composição)
# ===========================================================================
#
# PORTS = {
#     ...,
#     "customer_directory": "apps.integrations.crm.adapter.CRMAdapter",
# }
#
# settings/test.py → "apps.crm.tests.fakes.FakeCustomerDirectory"
# Trocar de fornecedor = trocar essa linha. Nenhum arquivo de domínio muda.
