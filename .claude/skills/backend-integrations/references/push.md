# Push notifications — Expo Push (dono: BE-05)

O frontend é Expo, então push usa o **Expo Push Service** (um token por dispositivo, o Expo
entrega via APNs/FCM). O domínio só conhece o port `PushSender`.

## Registro do dispositivo

```text
App → obtém ExponentPushToken[...] (expo-notifications)
    → POST /api/v1/devices/  {token, platform: "ios"|"android", app_version}
```

```python
# apps/notifications/models.py (core)
class Device(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="devices")
    token = models.CharField(max_length=200, unique=True)
    platform = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(auto_now=True)
```

Logout (`/auth/logout/`) desativa o device do token atual — usuário deslogado não recebe push.

## Port e adapter

```python
# apps/notifications/ports.py (core)
@dataclass(frozen=True)
class PushMessage:
    token: str
    title: str
    body: str
    data: dict  # só IDs/rotas ("screen": "order", "order_id": 12) — nunca dado sensível


class PushSender(Protocol):
    def send(self, *, messages: list[PushMessage]) -> list[PushResult]: ...
```

```python
# apps/integrations/expo_push/adapter.py
class ExpoPushSender:
    """POST https://exp.host/--/api/v2/push/send em lotes de até 100."""

    def __init__(self) -> None:
        self.client = ExpoPushClient(
            base_url="https://exp.host",
            auth_headers={"Authorization": f"Bearer {settings.EXPO_ACCESS_TOKEN}"},
            timeout=TimeoutPolicy(connect=3, read=10),
        )

    def send(self, *, messages):
        results = []
        for batch in chunked(messages, 100):
            raw = self.client.request("POST", "/--/api/v2/push/send", json=[m.__dict__ for m in batch],
                                      idempotency_key=None, operation="push_send")
            results += self._translate(raw, batch)   # DeviceNotRegistered → marcar device inativo
        return results
```

## Fluxo

```text
service (core) → dispatch("order.approved") → task order_approved_notify_task (BE-03)
              → service notification_send → get_port("push_sender").send(...)
```

- Envio sempre em task (nunca na request).
- Resposta `DeviceNotRegistered` → service desativa o `Device` (não é erro de retry).
- Receipts (`/push/getReceipts`) consultados por tarefa periódica após ~15 min para limpar tokens mortos.
- Texto do push não carrega dado sensível (aparece na tela bloqueada). O app busca o detalhe via API.
- WhatsApp (Evolution API) e e-mail seguem o mesmo desenho: port no core, adapter aqui, envio em task.
