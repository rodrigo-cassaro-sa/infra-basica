"""
apps/integrations/base/outbound.py

Trava de saída para ambientes que não são prod (skill devops, references/ambientes.md §4).
Todo adapter que envia mensagem para PESSOA (e-mail, WhatsApp/Evolution, SMS, push) chama
isto antes de enviar. hom nunca fala com cliente real.

settings.OUTBOUND_ALLOWLIST: lista de destinos permitidos (e-mails, telefones E.164, tokens
de push da equipe). Vazia = sem restrição — o settings de hom/prod só permite vazio em prod.
"""

from __future__ import annotations

import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def outbound_allowed(destination: str) -> bool:
    allowlist = getattr(settings, "OUTBOUND_ALLOWLIST", [])
    if not allowlist or destination in allowlist:
        return True
    logger.info(
        "outbound.blocked",
        extra={"app_env": getattr(settings, "APP_ENV", ""), "destination_suffix": destination[-4:]},
    )
    return False


# Uso num adapter:
#
#   def send(self, *, to: str, text: str) -> str | None:
#       if not outbound_allowed(to):
#           return None          # registrado, não enviado; o service trata como "não enviado"
#       return self.client.request("POST", "/message/sendText", json={...}, idempotency_key=...)
