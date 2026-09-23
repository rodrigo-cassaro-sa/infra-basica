"""apps/mcp/server.py — esqueleto de MCP Server (dono: BE-04).

Confirme a API exata na versão do SDK fixada no pyproject.toml.

O que não muda:
- a tool é ADAPTADOR FINO sobre selector/service do core, chamado com actor=principal.user;
- autorização é a do core: require_perm (common.permissions) e visibilidade/tenant no selector;
  a tool nunca passa tenant_id solto nem reimplementa checagem;
- leitura por padrão; escrita atrás de feature flag; ação sensível → PendingAction;
- erro de domínio volta ao modelo como exc.to_dict() (o code ajuda o agente a se corrigir).
"""

from django.conf import settings
from mcp.server import MCPServer

from apps.ai.pending import pending_action_propose
from apps.crm.selectors import customer_get, opportunity_list_open_for
from apps.crm.services import followup_schedule
from apps.mcp.auth import current_principal  # autenticação do host MCP → principal.user
from common.exceptions import DomainError
from common.permissions import require_perm

mcp = MCPServer("backend")


def _call(fn, **kwargs):
    """Executa selector/service e devolve DomainError no formato padrão da família."""
    try:
        return fn(**kwargs)
    except DomainError as exc:
        return {"error": exc.to_dict()}


# --- READ TOOLS -------------------------------------------------------------

@mcp.tool()
def get_customer(customer_id: int) -> dict:
    """Dados básicos de um cliente."""
    user = current_principal().user
    require_perm(user, "crm.view_customer")  # a tool só existe para quem pode ver clientes

    customer = _call(customer_get, actor=user, customer_id=customer_id)  # tenant: selector
    if isinstance(customer, dict):
        return customer
    # Retorno explícito: nada de serializar o objeto do ORM inteiro.
    return {"id": customer.id, "name": customer.name, "status": customer.status}


@mcp.tool()
def list_opportunities(limit: int = 20) -> list[dict] | dict:
    user = current_principal().user
    require_perm(user, "crm.view_opportunity")

    qs = _call(opportunity_list_open_for, actor=user)
    if isinstance(qs, dict):
        return qs
    # limite imposto pelo servidor, não pelo cliente
    return [{"id": o.id, "title": o.title, "value": str(o.value)} for o in qs[: min(limit, 100)]]


# --- WRITE TOOLS (atrás de flag, com justificativa) -------------------------

if settings.MCP_WRITE_TOOLS_ENABLED:

    @mcp.tool()
    def schedule_followup(customer_id: int, when: str, note: str) -> dict:
        """Agenda follow-up. Ação reversível e idempotente por (customer, when) → execução direta."""
        user = current_principal().user
        followup = _call(
            followup_schedule, actor=user, customer_id=customer_id, when=when, note=note
        )  # require_perm("crm.add_followup") acontece DENTRO do service
        if isinstance(followup, dict):
            return followup
        return {"id": followup.id, "scheduled_for": followup.when.isoformat()}

    @mcp.tool()
    def cancel_invoice(invoice_id: int, reason: str) -> dict:
        """Ação financeira/irreversível: o agente só PROPÕE. Um humano confirma no app."""
        user = current_principal().user
        pending = _call(
            pending_action_propose,
            actor=user,
            action="invoice_cancel",
            arguments={"invoice_id": invoice_id, "reason": reason},
            summary=f"Cancelar fatura #{invoice_id}: {reason[:120]}",
        )
        if isinstance(pending, dict):
            return pending
        return {"pending_action_id": pending.id, "status": "awaiting_human_confirmation"}


# --- RESOURCES --------------------------------------------------------------

@mcp.resource("customer://{customer_id}")
def customer_resource(customer_id: int) -> str:
    user = current_principal().user
    require_perm(user, "crm.view_customer")

    customer = customer_get(actor=user, customer_id=customer_id)
    return f"Cliente {customer.name} — status {customer.status}"
