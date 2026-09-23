# Autenticação — JWT para o Expo

Padrão da casa: **um só mecanismo** para app nativo (iOS/Android) e Expo web — JWT via
`djangorestframework-simplejwt`, access curto + refresh rotativo com blacklist.
Sessão/cookie só no Django Admin.

## Endpoints

```text
POST /api/v1/auth/token/          {email, password}        → {access, refresh, user}
POST /api/v1/auth/token/refresh/  {refresh}                → {access, refresh}   (rotação)
POST /api/v1/auth/logout/         {refresh}                → 204 (refresh vai para blacklist)
GET  /api/v1/auth/me/                                        → dados do usuário + permissões
POST /api/v1/auth/password-reset/ {email}                  → 202 (sempre, não revela se existe)
POST /api/v1/auth/password-reset/confirm/ {token, password} → 204
```

Throttle scopes: `login` (5/min), `password_reset` (5/hour), `signup` (10/hour).

## Código

```python
# apps/accounts/api/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class TokenSerializer(TokenObtainPairSerializer):
    username_field = "email"

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Claim só informativa para o app. O backend NUNCA confia nela para escopo:
        # o tenant sempre vem de request.user (banco).
        token["tenant_id"] = user.tenant_id
        return token


# apps/accounts/api/views.py
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]  # público: é o login
    throttle_scope = "login"
    serializer_class = TokenSerializer


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            RefreshToken(request.data.get("refresh")).blacklist()
        except Exception:  # token inválido/expirado: logout é idempotente
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "name": user.get_full_name(),
            "tenant_id": user.tenant_id,
            # O app usa isso só para esconder/mostrar UI. A checagem real é do service.
            "permissions": sorted(user.get_all_permissions()),
        })
```

`/me` com `permissions` é o que o Expo usa para montar menus. Esconder botão não é segurança:
o service faz `require_perm` de qualquer jeito.

## Lado do Expo (contrato)

- Guardar `refresh` em **`expo-secure-store`** (nativo). No Expo web, SecureStore não existe:
  guardar o refresh em memória + `localStorage` só se o risco for aceito, ou exigir login por sessão
  do navegador. Decisão registrada no guia do projeto.
- `access` só em memória.
- Interceptor: resposta 401 com `code == "TOKEN_INVALID"` → chama `/token/refresh/` uma vez,
  repete a requisição; se o refresh falhar → logout local.
- Enviar `X-Request-ID` (UUID por ação) ajuda a rastrear bug relatado pelo usuário.

## Regras

- Login e reset **sempre** com throttling.
- Reset de senha não revela se o e-mail existe (sempre 202).
- Troca de senha/desativação de usuário → invalidar refresh tokens (blacklist de todos os outstanding).
- Nunca logar `password`, `access`, `refresh` (o filtro de `common/logging.py` mascara as chaves).
