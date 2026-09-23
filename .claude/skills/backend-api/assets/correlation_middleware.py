"""
Middleware de correlation id (BE-02) — config/api/middleware.py

Único ponto que DEFINE o correlation_id numa requisição HTTP. Nome único da família:
`correlation_id` (ContextVar em common/logging.py). Header de entrada/saída: X-Request-ID.

- aceita o X-Request-ID do cliente (Expo pode gerar um por ação) se for seguro;
- senão gera um UUID4;
- devolve no header da resposta;
- a backend-async propaga para as tasks e a backend-integrations envia ao provider.

Registro (logo após SecurityMiddleware):
    MIDDLEWARE.insert(1, "config.api.middleware.CorrelationIdMiddleware")
"""

import re
import uuid

from common.logging import correlation_id

_SAFE = re.compile(r"^[A-Za-z0-9\-_.]{1,64}$")
HEADER = "HTTP_X_REQUEST_ID"


class CorrelationIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        incoming = request.META.get(HEADER, "")
        value = incoming if _SAFE.match(incoming) else uuid.uuid4().hex
        token = correlation_id.set(value)
        request.correlation_id = value
        try:
            response = self.get_response(request)
        finally:
            correlation_id.reset(token)
        response["X-Request-ID"] = value
        return response
