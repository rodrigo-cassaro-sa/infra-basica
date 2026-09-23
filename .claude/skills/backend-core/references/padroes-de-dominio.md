# Padrões de domínio — código de referência

Sumário: 1. common/models.py · 2. common/exceptions.py · 3. common/permissions.py ·
4. common/validators.py (CPF/CNPJ) · 5. accounts (User + papéis) · 6. Módulo completo de exemplo (sales) ·
7. Concorrência · 8. Soft delete · 9. Migrations seguras · 10. Ports · 11. common/errors.py (falhas de infraestrutura) ·
12. common/events.py (event bus) · 13. common/jobs.py (estado de processamento) · 14. Multi-tenant (tenants + common/tenancy.py)
---

## 1. common/models.py

```python
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models

from common.exceptions import ValidationError


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditedModel(BaseModel):
    """Quem criou/alterou. Preenchido SEMPRE pelo service a partir do actor."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        abstract = True


def validate_and_save(instance, *, update_fields: list[str] | None = None) -> None:
    """full_clean + save, convertendo erro do Django em ValidationError de domínio."""
    try:
        instance.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError.from_django(exc) from exc
    instance.save(update_fields=update_fields)
```

`null=True` em `created_by` só porque processos de sistema (`actor=None`) também criam registros.

---

## 2. common/exceptions.py

```python
from typing import Any


class DomainError(Exception):
    """Base de todo erro de negócio. `code` é contrato público: não renomear.

    Não conhece HTTP. A backend-api traduz a CATEGORIA (classe-mãe) em status.
    `fields` = erros por campo ({"email": ["Já cadastrado."]}); `details` = contexto livre.
    """

    code = "DOMAIN_ERROR"
    default_message = "Erro de domínio."

    def __init__(
        self,
        message: str | None = None,
        *,
        fields: dict[str, list[str]] | None = None,
        **details: Any,
    ) -> None:
        self.message = message or self.default_message
        self.fields = fields or {}
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Formato único usado por API (dentro de {"error": ...}), tools MCP e logs."""
        return {
            "code": self.code,
            "message": self.message,
            "fields": self.fields,
            "details": self.details,
        }


class NotFoundError(DomainError):
    code = "NOT_FOUND"
    default_message = "Recurso não encontrado."


class PermissionDeniedError(DomainError):
    code = "PERMISSION_DENIED"
    default_message = "Você não tem permissão para esta ação."


class ValidationError(DomainError):
    code = "VALIDATION_ERROR"
    default_message = "Dados inválidos."

    @classmethod
    def from_django(cls, exc) -> "ValidationError":
        """Converte django.core.exceptions.ValidationError (full_clean) em erro de domínio."""
        fields = exc.message_dict if hasattr(exc, "error_dict") else {"__all__": exc.messages}
        return cls(fields={k: [str(m) for m in v] for k, v in fields.items()})


class ConflictError(DomainError):
    code = "CONFLICT"
    default_message = "O estado atual não permite esta operação."


class BusinessRuleError(DomainError):
    code = "BUSINESS_RULE_VIOLATION"
    default_message = "Regra de negócio violada."
```

Exceções do app (ex.: `apps/sales/exceptions.py`):

```python
from common.exceptions import BusinessRuleError, ConflictError, NotFoundError


class OrderNotFound(NotFoundError):
    code = "ORDER_NOT_FOUND"
    default_message = "Pedido não encontrado."


class OrderInvalidTransition(ConflictError):
    code = "ORDER_INVALID_TRANSITION"
    default_message = "Transição de status inválida para o pedido."


class InsufficientStock(BusinessRuleError):
    code = "INSUFFICIENT_STOCK"
    default_message = "Estoque insuficiente."
```

Sobre `full_clean()`: ele lança a `ValidationError` **do Django**. O service pode deixar subir
(a backend-api mapeia as duas) ou converter com `ValidationError.from_django(exc)` quando
quiser um payload uniforme — escolha **uma** convenção por projeto. Padrão da casa: **converter**, usando `validate_and_save()` de `common/models.py` (seção 1).

---

## 3. common/permissions.py

```python
from common.exceptions import PermissionDeniedError


def require_perm(actor, perm: str) -> None:
    """Falha se o actor não tiver a permissão `app_label.codename`.

    actor=None representa processo de sistema e só é aceito quando o
    service documenta explicitamente que roda sem usuário.
    """
    if actor is None or not actor.is_active or not actor.has_perm(perm):
        raise PermissionDeniedError(perm=perm)


def require_any_perm(actor, *perms: str) -> None:
    if actor is None or not actor.is_active or not any(actor.has_perm(p) for p in perms):
        raise PermissionDeniedError(perms=list(perms))
```

Services de sistema (rodados por task/cron sem usuário) **não** chamam `require_perm`;
documentam isso na docstring e só são expostos pela backend-async, nunca pela API.

---

## 4. common/validators.py — documentos BR

```python
import re

from django.core.exceptions import ValidationError


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def _dv(digits: str, weights: range | list[int]) -> int:
    total = sum(int(d) * w for d, w in zip(digits, weights, strict=False))
    rest = total % 11
    return 0 if rest < 2 else 11 - rest


def validate_cpf(value: str) -> None:
    cpf = only_digits(value)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValidationError("CPF inválido.", code="invalid_cpf")
    d1 = _dv(cpf[:9], range(10, 1, -1))
    d2 = _dv(cpf[:9] + str(d1), range(11, 1, -1))
    if cpf[-2:] != f"{d1}{d2}":
        raise ValidationError("CPF inválido.", code="invalid_cpf")


def validate_cnpj(value: str) -> None:
    cnpj = only_digits(value)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        raise ValidationError("CNPJ inválido.", code="invalid_cnpj")
    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    w2 = [6, *w1]
    d1 = _dv(cnpj[:12], w1)
    d2 = _dv(cnpj[:12] + str(d1), w2)
    if cnpj[-2:] != f"{d1}{d2}":
        raise ValidationError("CNPJ inválido.", code="invalid_cnpj")


def validate_period(*, start, end) -> None:
    if start and end and end < start:
        raise ValidationError("A data final deve ser maior ou igual à inicial.", code="invalid_period")
```

> CNPJ alfanumérico (Receita, a partir de jul/2026): se o projeto precisar aceitar,
> tratar em validador próprio — não reaproveitar `only_digits`.

Armazenar documento **só com dígitos** (normalizar no service) e validar com
`validators=[validate_cpf]` no campo. Formatação é problema da apresentação.

---

## 5. accounts — User e papéis

```python
# apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    # Só em projeto multi-tenant (seção 14). Null = usuário de plataforma/staff.
    tenant = models.ForeignKey(
        "tenants.Tenant", on_delete=models.PROTECT, null=True, blank=True, related_name="users"
    )

    REQUIRED_FIELDS = ["email"]
```

Sempre referenciar o usuário como `settings.AUTH_USER_MODEL` (em FK) ou `get_user_model()`
(em código). **Nunca** `"users.User"` ou `"auth.User"` escrito à mão — o app é `accounts`.

Papéis como `Group`, criados por **data migration** (reprodutível em todo ambiente):

```python
# apps/accounts/migrations/000X_seed_roles.py
from django.db import migrations

ROLES = {
    "gerente": ["sales.approve_order", "sales.view_all_orders", "sales.add_order"],
    "vendedor": ["sales.add_order"],
}


def seed_roles(apps, schema_editor):
    from django.contrib.auth.management import create_permissions

    for app_config in apps.get_app_configs():  # garante que as permissions existam
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    for role, perms in ROLES.items():
        group, _ = Group.objects.get_or_create(name=role)
        for perm in perms:
            app_label, codename = perm.split(".")
            group.permissions.add(
                Permission.objects.get(content_type__app_label=app_label, codename=codename)
            )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("sales", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]
    operations = [migrations.RunPython(seed_roles, migrations.RunPython.noop)]
```

Lembrete: Django cria automaticamente `add_`, `change_`, `delete_`, `view_<model>`.
Declare em `Meta.permissions` só as **ações de negócio** extras (`approve_order`, `cancel_invoice`).

---

## 6. Módulo completo de exemplo — `apps/sales`

### models.py

```python
from decimal import Decimal

from django.db import models

from common.models import AuditedModel, BaseModel


class Product(BaseModel):
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=40, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name="product_price_gte_0"),
        ]

    def __str__(self) -> str:
        return f"{self.sku} — {self.name}"


class Order(AuditedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        APPROVED = "approved", "Aprovado"
        CANCELED = "canceled", "Cancelado"

    customer = models.ForeignKey("customers.Customer", on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        indexes = [models.Index(fields=["status", "created_at"])]
        permissions = [
            ("approve_order", "Pode aprovar pedido"),
            ("view_all_orders", "Pode ver pedidos de todos"),
        ]

    def __str__(self) -> str:
        return f"Pedido #{self.pk}"


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="+")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gt=0), name="orderitem_qty_gt_0"),
            models.UniqueConstraint(fields=["order", "product"], name="orderitem_unique_product"),
        ]
```

### constants.py (máquina de estados)

```python
from .models import Order

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    Order.Status.PENDING: {Order.Status.APPROVED, Order.Status.CANCELED},
    Order.Status.APPROVED: {Order.Status.CANCELED},
    Order.Status.CANCELED: set(),
}
```

### validators.py

```python
from .constants import ALLOWED_TRANSITIONS
from .exceptions import OrderInvalidTransition


def validate_order_transition(*, current: str, target: str) -> None:
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise OrderInvalidTransition(current=current, target=target)
```

### services.py

```python
import logging
from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction
from django.db.models import F

from common.events import dispatch
from common.models import validate_and_save
from common.permissions import require_perm

from .exceptions import InsufficientStock, OrderNotFound
from .models import Order, OrderItem, Product
from .validators import validate_order_transition

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ItemInput:
    product_id: int
    quantity: int


@transaction.atomic
def order_create(*, actor, customer_id: int, items: list[ItemInput]) -> Order:
    """Cria pedido pendente com preço congelado no momento da compra. H-010."""
    require_perm(actor, "sales.add_order")

    products = Product.objects.in_bulk([i.product_id for i in items])
    order = Order(customer_id=customer_id, created_by=actor, updated_by=actor)
    validate_and_save(order)

    total = Decimal("0.00")
    rows = []
    for item in items:
        product = products[item.product_id]
        rows.append(OrderItem(order=order, product=product, quantity=item.quantity, unit_price=product.price))
        total += product.price * item.quantity
    OrderItem.objects.bulk_create(rows)

    order.total = total
    order.save(update_fields=["total", "updated_at"])
    return order


@transaction.atomic
def order_approve(*, actor, order_id: int) -> Order:
    """Aprova e baixa estoque de forma atômica. H-012."""
    require_perm(actor, "sales.approve_order")

    try:
        order = Order.objects.select_for_update().get(pk=order_id)
    except Order.DoesNotExist:
        raise OrderNotFound(order_id=order_id) from None

    validate_order_transition(current=order.status, target=Order.Status.APPROVED)

    for item in order.items.all():
        updated = Product.objects.filter(pk=item.product_id, stock__gte=item.quantity).update(
            stock=F("stock") - item.quantity
        )
        if not updated:  # outro pedido levou o estoque antes → rollback de tudo
            raise InsufficientStock(product_id=item.product_id, requested=item.quantity)

    order.status = Order.Status.APPROVED
    order.updated_by = actor
    order.save(update_fields=["status", "updated_by", "updated_at"])

    # Efeito colateral: evento pós-commit (a backend-async decide o que fazer com ele).
    transaction.on_commit(lambda: dispatch("order.approved", order_id=order.pk))
    return order
```

Repare: o `update(... stock__gte=qty)` é **atômico no banco** — não existe janela entre ler e
gravar o estoque. É o padrão para saldo/estoque/vagas/capacidade.

### selectors.py

```python
from django.db.models import Prefetch, QuerySet

from .exceptions import OrderNotFound
from .models import Order, OrderItem


def order_list_for(*, actor, status: str | None = None) -> QuerySet[Order]:
    qs = Order.objects.select_related("customer").order_by("-created_at")
    if not actor.has_perm("sales.view_all_orders"):
        qs = qs.filter(created_by=actor)
    if status:
        qs = qs.filter(status=status)
    return qs


def order_get_detail(*, actor, order_id: int) -> Order:
    qs = order_list_for(actor=actor).prefetch_related(
        Prefetch("items", queryset=OrderItem.objects.select_related("product"))
    )
    try:
        return qs.get(pk=order_id)
    except Order.DoesNotExist:
        raise OrderNotFound(order_id=order_id) from None
```

### admin.py

Admin é ferramenta **interna**. Pode listar/filtrar à vontade; **ações que mudam estado
chamam o service** (nunca `queryset.update(status=...)` direto):

```python
@admin.action(description="Aprovar pedidos selecionados")
def approve_selected(modeladmin, request, queryset):
    for order in queryset:
        services.order_approve(actor=request.user, order_id=order.pk)
```

---

## 7. Concorrência — cardápio

| Situação | Técnica |
|---|---|
| Decrementar saldo/estoque/vagas | `filter(..., campo__gte=n).update(campo=F("campo") - n)` + checar linhas afetadas |
| Ler, decidir e gravar no mesmo registro | `select_for_update()` dentro de `atomic` |
| Evitar travar e pular o que está ocupado (fila de trabalho) | `select_for_update(skip_locked=True)` |
| Unicidade sob corrida | `UniqueConstraint` + `except IntegrityError: raise XAlreadyExists` |
| Idempotência de operação repetida (retry, webhook) | coluna `idempotency_key` com `UniqueConstraint` |
| Invariante que nunca pode quebrar | `CheckConstraint` (rede de segurança final) |

```python
from django.db import IntegrityError, transaction


def customer_create(*, actor, name: str, email: str) -> Customer:
    require_perm(actor, "customers.add_customer")
    customer = Customer(name=name, email=email.lower().strip(), created_by=actor)
    try:
        with transaction.atomic():
            validate_and_save(customer)
    except IntegrityError:
        raise CustomerAlreadyExists(email=email) from None
    return customer
```

(`full_clean` já acusa duplicidade na maioria dos casos; o `IntegrityError` cobre a corrida entre duas requisições.)

---

## 8. Soft delete (só quando justificado)

```python
from django.db import models
from django.utils import timezone


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
```

- O "apagar" é um **service** (`customer_archive`) que seta `deleted_at = timezone.now()`.
- Unicidade só entre ativos: `UniqueConstraint(fields=["email"], condition=Q(deleted_at__isnull=True), name=...)`.
- Cuidado: `base_manager_name` e relações reversas ainda enxergam removidos — revise selectors.

---

## 9. Migrations seguras

**Campo obrigatório novo em tabela com dados** (3 deploys ou 3 migrations):

1. `AddField(null=True)`.
2. Data migration preenchendo (em lotes se grande).
3. `AlterField(null=False)` / adicionar constraint.

**Data migration padrão:**

```python
from django.db import migrations


def forwards(apps, schema_editor):
    Customer = apps.get_model("customers", "Customer")  # nunca importar o model real
    batch = []
    for c in Customer.objects.filter(document="").only("pk").iterator(chunk_size=2000):
        c.document = "PENDENTE"
        batch.append(c)
        if len(batch) >= 2000:
            Customer.objects.bulk_update(batch, ["document"])
            batch.clear()
    if batch:
        Customer.objects.bulk_update(batch, ["document"])


class Migration(migrations.Migration):
    dependencies = [("customers", "0004_customer_document")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
```

**Índice em tabela grande sem travar escrita:**

```python
from django.contrib.postgres.operations import AddIndexConcurrently
from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False
    dependencies = [("sales", "0007_previous")]
    operations = [
        AddIndexConcurrently("order", models.Index(fields=["customer", "status"], name="order_cust_status_idx")),
    ]
```

Renomear/remover coluna usada em produção: primeiro deploy do código que não usa mais,
depois a migration que remove.

---

## 10. Ports — como o core pede algo do mundo externo

O core declara **o que** precisa; a backend-integrations entrega **como**.

```python
# apps/billing/ports.py
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class ChargeResult:
    external_id: str
    status: str


class PaymentGateway(Protocol):
    def create_charge(self, *, amount: Decimal, customer_document: str, idempotency_key: str) -> ChargeResult: ...
```

Resolução da implementação por settings (sem framework de DI):

```python
# common/ports.py
from functools import cache

from django.conf import settings
from django.utils.module_loading import import_string


@cache
def _port_class(dotted: str):
    return import_string(dotted)


def get_port(name: str):
    """Única forma de o core obter uma implementação externa. Nunca importar o adapter."""
    try:
        dotted = settings.PORTS[name]
    except KeyError:
        raise LookupError(f"Port '{name}' não registrado em settings.PORTS") from None
    return _port_class(dotted)()
```

```python
# settings
PORTS = {
    "event_bus": "apps.jobs.bus.CeleryEventBus",                            # backend-async
    "payment_gateway": "apps.integrations.asaas.adapter.AsaasPaymentGateway",  # backend-integrations
}
# settings/test.py
PORTS = {
    "event_bus": "common.events.InMemoryEventBus",
    "payment_gateway": "apps.billing.tests.fakes.FakePaymentGateway",
}
```

Nos testes do core, usar o **fake** — o core nunca depende de rede para ser testado.
Chamada do port que envolve rede acontece **fora** da transação (antes, ou em `on_commit`
delegando para uma task da backend-async).


Regras dos ports (valem para as 5 skills):

- O `Protocol` mora **sempre** no core, em `apps/<app>/ports.py`. Nome do nosso negócio (`PaymentGateway`, `CustomerDirectory`), nunca do provider.
- A implementação mora na backend-integrations (`apps/integrations/<provider>/adapter.py`) ou na backend-async (`event_bus`) e é **registrada em `settings.PORTS`**. (Providers de IA usam o registro análogo `settings.AI_PROVIDERS` da backend-ai-mcp.)
- Nenhuma função `get_xxx()` de composição fora de `common.ports.get_port`. Trocar provider = trocar uma linha de settings.

---

## 11. common/errors.py — falhas de infraestrutura (não são de domínio)

Uma única classificação de falha técnica, usada por integrations, ai-mcp e async. É ela que decide
se uma task faz retry — ninguém cria hierarquia paralela de "erro transitório".

```python
class InfrastructureError(Exception):
    """Falha técnica (rede, provider, IA). Não é regra de negócio."""

    retryable: bool = False
    code = "INFRASTRUCTURE_ERROR"

    def __init__(self, message: str = "", *, retry_after: float | None = None, **context) -> None:
        super().__init__(message or self.__class__.__name__)
        self.retry_after = retry_after
        self.context = context  # nunca colocar credencial aqui


class TransientError(InfrastructureError):
    """Pode dar certo se repetir: timeout, conexão, 429, 502, 503, 504."""

    retryable = True
    code = "TEMPORARILY_UNAVAILABLE"


class PermanentError(InfrastructureError):
    """Repetir devolve o mesmo erro: 400, 401, 403, 404, 422, payload inválido."""

    retryable = False
    code = "EXTERNAL_SERVICE_ERROR"
```

- `IntegrationError` (BE-05) e `AIProviderError` (BE-04) **herdam** de `TransientError`/`PermanentError`.
- Task: `autoretry_for=(TransientError,)`. Nunca `Exception`.
- API: `TransientError` → 503, `PermanentError` → 502, sempre com `code` estável e sem detalhe do provider.
- `DomainError` nunca é retentado.

---

## 12. common/events.py — event bus (core → async)

O core **não importa tasks**. Efeito colateral pós-commit = evento com IDs/primitivos.

```python
import logging
from typing import Any, Protocol

from common.ports import get_port

logger = logging.getLogger(__name__)


class EventBus(Protocol):
    def publish(self, event: str, payload: dict[str, Any]) -> None: ...


def dispatch(event: str, **payload: Any) -> None:
    """Publica um evento de domínio. Chamar SEMPRE dentro de transaction.on_commit."""
    get_port("event_bus").publish(event, payload)


class InMemoryEventBus:
    """Fake para testes (settings/test.py). Permite assert nos eventos emitidos."""

    published: list[tuple[str, dict[str, Any]]] = []

    def publish(self, event: str, payload: dict[str, Any]) -> None:
        InMemoryEventBus.published.append((event, payload))

    @classmethod
    def clear(cls) -> None:
        cls.published.clear()
```

Nomes de evento: `<entidade>.<fato_no_passado>` (`order.approved`, `invoice.paid`). Payload só
com IDs e primitivos JSON — nunca instância de model. A implementação real (`CeleryEventBus`,
que mapeia evento → tasks) é da backend-async.

Teste:

```python
@pytest.fixture(autouse=True)
def _events():
    InMemoryEventBus.clear()
    yield


def test_approve_emits_event(django_capture_on_commit_callbacks, manager, order):
    with django_capture_on_commit_callbacks(execute=True):
        services.order_approve(actor=manager, order_id=order.pk)
    assert ("order.approved", {"order_id": order.pk}) in InMemoryEventBus.published
```

---

## 13. common/jobs.py — estado de processamento (base comum)

Toda entidade que representa trabalho assíncrono ou externo acompanhado pelo app/painel
(ImportJob, ReportJob, AIJob, WebhookEvent, SyncState...) herda desta base. Um só vocabulário
de status em todas as skills.

```python
from django.db import models

from common.models import BaseModel


class ProcessingStatus(models.TextChoices):
    PENDING = "pending", "Pendente"
    PROCESSING = "processing", "Processando"
    COMPLETED = "completed", "Concluído"
    FAILED = "failed", "Falhou"
    CANCELED = "canceled", "Cancelado"
    IGNORED = "ignored", "Ignorado"


class ProcessingStateModel(BaseModel):
    status = models.CharField(
        max_length=20, choices=ProcessingStatus.choices, default=ProcessingStatus.PENDING, db_index=True
    )
    attempts = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, default="")
    correlation_id = models.CharField(max_length=64, blank=True, default="", db_index=True)

    class Meta:
        abstract = True


class ProgressMixin(models.Model):
    total = models.PositiveIntegerField(default=0)
    processed = models.PositiveIntegerField(default=0)
    failed = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
```

Transições (`pending → processing → completed|failed`) são feitas por **funções de service** do app
dono do job (ex.: `job_mark_processing`, `job_mark_completed`), nunca por métodos com lógica no model
e nunca por `queryset.update()` espalhado. Grafia da casa: **`canceled`** (um L).

---

## 14. Multi-tenant — app `tenants` + common/tenancy.py

Decidir no início. Padrão da casa: **um tenant por usuário** (`User.tenant`, seção 5). Se o produto
precisar de usuário em vários tenants, trocar por `Membership(user, tenant, role)` + tenant ativo
no token — decisão registrada no projeto antes do primeiro model.

```python
# apps/tenants/models.py
from django.db import models

from common.models import BaseModel


class Tenant(BaseModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name
```

```python
# common/tenancy.py
from django.conf import settings
from django.db import models

from common.exceptions import PermissionDeniedError
from common.models import AuditedModel


class TenantModel(AuditedModel):
    """Base de todo model que pertence a um tenant."""

    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.PROTECT, related_name="+")

    class Meta:
        abstract = True


def tenant_id_of(actor) -> int:
    """Tenant do actor. Falha fechado: sem tenant, sem acesso."""
    tenant_id = getattr(actor, "tenant_id", None)
    if tenant_id is None:
        raise PermissionDeniedError(reason="actor_without_tenant")
    return tenant_id


def scope_to_tenant(qs, actor):
    return qs.filter(tenant_id=tenant_id_of(actor))
```

Regras:

- Selector **sempre** recebe `actor` e escopa com `scope_to_tenant(qs, actor)`. Nunca recebe `tenant_id` solto vindo de fora (API, tool MCP, task) — isso permitiria pedir dado de outro tenant.
- Service que cria registro preenche `tenant_id=tenant_id_of(actor)`; nunca aceita tenant do payload.
- Task de sistema (`actor=None`) recebe o `tenant_id` do evento e documenta isso — é o único caso.
- Objeto de outro tenant = `XNotFound` (404), não 403: não confirma que o registro existe.
- `UniqueConstraint` de negócio inclui `tenant` (`fields=["tenant", "email"]`).
