# Testes e qualidade do núcleo

Sumário: 1. Prioridades · 2. conftest + factories · 3. Exemplos de teste · 4. pre-commit · 5. CI (GitHub Actions)

---

## 1. O que testar (nessa ordem)

1. Regras de negócio dos services (caminho feliz + cada exceção de domínio).
2. Permissões (actor sem permissão recebe `PermissionDeniedError`; visibilidade dos selectors).
3. Transações (falha no meio ⇒ nada persistido).
4. Constraints do banco (o banco recusa o dado inválido mesmo sem passar pelo service).
5. Casos críticos de concorrência/idempotência.
6. Consultas complexas (resultado certo + número de queries).

Teste **comportamento** pela interface pública (service/selector), não detalhes internos.
Nenhum teste do core faz HTTP, sobe fila ou chama API real — ports usam fakes.

Nome do teste diz a regra: `test_order_approve_fails_when_stock_is_insufficient`.

---

## 2. tests/conftest.py e factories

```python
# tests/conftest.py
import pytest
from django.contrib.auth.models import Permission

from common.events import InMemoryEventBus
from tests.factories import TenantFactory, UserFactory


@pytest.fixture(autouse=True)
def _clear_events():
    """Eventos emitidos por dispatch() (settings/test.py usa InMemoryEventBus)."""
    InMemoryEventBus.clear()
    yield
    InMemoryEventBus.clear()


@pytest.fixture
def tenant(db):
    return TenantFactory()


@pytest.fixture
def user(db, tenant):
    return UserFactory(tenant=tenant)


@pytest.fixture
def other_tenant_user(db):
    return UserFactory(tenant=TenantFactory())


@pytest.fixture
def user_with_perms(db, tenant):
    def _make(*perms: str, tenant=tenant):
        u = UserFactory(tenant=tenant)
        for perm in perms:
            app_label, codename = perm.split(".")
            u.user_permissions.add(
                Permission.objects.get(content_type__app_label=app_label, codename=codename)
            )
        return type(u).objects.get(pk=u.pk)  # recarrega: limpa cache de permissões

    return _make
```

```python
# tests/factories.py
import factory
from django.contrib.auth import get_user_model


class TenantFactory(factory.django.DjangoModelFactory):  # só em projeto multi-tenant
    class Meta:
        model = "tenants.Tenant"

    name = factory.Sequence(lambda n: f"Empresa {n}")
    slug = factory.Sequence(lambda n: f"empresa-{n}")


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        skip_postgeneration_save = True

    tenant = factory.SubFactory(TenantFactory)
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@exemplo.com")
    password = factory.django.Password("senha-teste-123")
```

```python
# apps/sales/tests/factories.py
from decimal import Decimal

import factory

from apps.sales.models import Order, Product


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker("word", locale="pt_BR")
    sku = factory.Sequence(lambda n: f"SKU{n:05d}")
    price = Decimal("10.00")
    stock = 10


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    customer = factory.SubFactory("apps.customers.tests.factories.CustomerFactory")
```

Factories por app em `apps/<app>/tests/factories.py`; compartilhadas em `tests/factories.py`.

---

## 3. Exemplos

```python
# apps/sales/tests/test_services.py
from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.sales import services
from apps.sales.exceptions import InsufficientStock, OrderInvalidTransition
from apps.sales.models import Order, Product
from apps.sales.tests.factories import OrderFactory, ProductFactory
from common.exceptions import PermissionDeniedError

pytestmark = pytest.mark.django_db


def _order_with(product, qty):
    order = OrderFactory()
    order.items.create(product=product, quantity=qty, unit_price=product.price)
    return order


def test_order_approve_reduces_stock(user_with_perms):
    manager = user_with_perms("sales.approve_order")
    product = ProductFactory(stock=5)
    order = _order_with(product, 3)

    services.order_approve(actor=manager, order_id=order.pk)

    product.refresh_from_db()
    order.refresh_from_db()
    assert product.stock == 2
    assert order.status == Order.Status.APPROVED
    assert order.updated_by == manager


def test_order_approve_requires_permission(user):
    order = OrderFactory()
    with pytest.raises(PermissionDeniedError):
        services.order_approve(actor=user, order_id=order.pk)


def test_order_approve_rolls_back_everything_when_one_item_lacks_stock(user_with_perms):
    manager = user_with_perms("sales.approve_order")
    ok, short = ProductFactory(stock=5), ProductFactory(stock=1)
    order = _order_with(ok, 2)
    order.items.create(product=short, quantity=3, unit_price=short.price)

    with pytest.raises(InsufficientStock):
        services.order_approve(actor=manager, order_id=order.pk)

    ok.refresh_from_db()
    order.refresh_from_db()
    assert ok.stock == 5  # a baixa do 1º item foi desfeita
    assert order.status == Order.Status.PENDING


def test_canceled_order_cannot_be_approved(user_with_perms):
    manager = user_with_perms("sales.approve_order")
    order = OrderFactory(status=Order.Status.CANCELED)
    with pytest.raises(OrderInvalidTransition):
        services.order_approve(actor=manager, order_id=order.pk)


def test_db_rejects_negative_price():
    with pytest.raises(IntegrityError):
        Product.objects.create(name="x", sku="NEG", price=Decimal("-1"))
```

```python
# apps/sales/tests/test_selectors.py
import pytest

from apps.sales import selectors
from apps.sales.tests.factories import OrderFactory

pytestmark = pytest.mark.django_db


def test_seller_sees_only_own_orders(user, user_with_perms):
    mine = OrderFactory(created_by=user)
    OrderFactory()  # de outra pessoa
    assert list(selectors.order_list_for(actor=user)) == [mine]


def test_order_list_has_no_n_plus_one(user_with_perms, django_assert_num_queries):
    boss = user_with_perms("sales.view_all_orders")
    OrderFactory.create_batch(5)
    boss.has_perm("sales.view_all_orders")  # aquece o cache de permissões fora da contagem
    with django_assert_num_queries(1):
        orders = list(selectors.order_list_for(actor=boss))
        _ = [o.customer.name for o in orders]
```

Concorrência real (duas conexões simultâneas) exige `@pytest.mark.django_db(transaction=True)`
e threads — use só para as 1–2 regras mais críticas (ex.: estoque, saldo); o resto se cobre com
constraint + teste de `update` condicional.

Rodar: `uv run pytest` · cobertura: `uv run pytest --cov --cov-report=term-missing`.
Meta prática: services e selectors com cobertura alta; não perseguir 100% global.

---

## 4. .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9   # atualizar com `pre-commit autoupdate`
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-merge-conflict
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: detect-private-key
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.0
    hooks:
      - id: gitleaks
```

Instalar: `uv run pre-commit install` e depois `uv run pre-commit autoupdate`.

---

## 5. CI mínimo — .github/workflows/backend.yml

```yaml
name: backend
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_USER: app
          POSTGRES_PASSWORD: app
          POSTGRES_DB: app
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U app" --health-interval 5s --health-retries 10
    env:
      DJANGO_SETTINGS_MODULE: config.settings.test
      DJANGO_SECRET_KEY: ci-only-not-secret
      DATABASE_URL: postgres://app:app@localhost:5432/app
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --frozen
      - name: Lint
        run: uv run ruff check . && uv run ruff format --check .
      - name: Migrations em dia
        run: uv run python manage.py makemigrations --check --dry-run
      - name: Testes
        run: uv run pytest --cov
      - name: Check de deploy
        env:
          DJANGO_SETTINGS_MODULE: config.settings.production
          DJANGO_ALLOWED_HOSTS: exemplo.com.br
        run: uv run python manage.py check --deploy --fail-level WARNING
```

Pipeline mínimo obrigatório: **lint → migrations check → testes**. O `check --deploy`
é recomendado; se algum aviso for aceito conscientemente, silenciar via `SILENCED_SYSTEM_CHECKS` com comentário do motivo.
