#!/usr/bin/env python3
"""Cria um app de domínio no padrão BE-01 (backend-core).

Uso:
    python novo_modulo.py <nome_app> --entidade <NomeEntidade> [--raiz backend/] [--extras validators,ports,constants] [--tenant]

Exemplo:
    python novo_modulo.py sales --entidade Order --raiz backend/ --extras validators,constants

Gera apps/<nome_app>/ com models, services, selectors, exceptions, admin, apps,
migrations/ e tests/ já ligados ao common/ (BaseModel, exceções, require_perm).
Não sobrescreve nada que já exista.
"""

import argparse
import re
import sys
from pathlib import Path


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def templates(app: str, ent: str, tenant: bool = False) -> dict[str, str]:
    e = snake(ent)
    base_cls = "TenantModel" if tenant else "AuditedModel"
    base_imp = "from common.tenancy import TenantModel" if tenant else "from common.models import AuditedModel"
    tenant_kw = ", tenant_id=tenant_id_of(actor)" if tenant else ""
    tenant_imp = "from common.tenancy import tenant_id_of\n" if tenant else ""
    scope_imp = "from common.tenancy import scope_to_tenant\n\n" if tenant else ""

    E = ent
    upper = e.upper()
    return {
        "__init__.py": "",
        "apps.py": f'''from django.apps import AppConfig


class {app.title().replace("_", "")}Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.{app}"
    label = "{app}"
    verbose_name = "{app.replace("_", " ").title()}"
''',
        "models.py": f'''from django.db import models

{base_imp}


class {E}({base_cls}):
    class Status(models.TextChoices):
        ACTIVE = "active", "Ativo"
        INACTIVE = "inactive", "Inativo"

    name = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # models.UniqueConstraint(fields=[...], name="{e}_unique_..."),
            # models.CheckConstraint(condition=models.Q(...), name="{e}_..."),
        ]
        indexes = [
            # models.Index(fields=["status", "created_at"]),
        ]
        permissions = [
            # ("approve_{e}", "Pode aprovar {e}"),
        ]

    def __str__(self) -> str:
        return self.name
''',
        "exceptions.py": f'''from common.exceptions import ConflictError, NotFoundError


class {E}NotFound(NotFoundError):
    code = "{upper}_NOT_FOUND"
    default_message = "{E} não encontrado."


class {E}AlreadyExists(ConflictError):
    code = "{upper}_ALREADY_EXISTS"
    default_message = "{E} já existe."
''',
        "services.py": f'''"""Casos de uso que ALTERAM estado de {E}. Sempre keyword-only, com actor."""

import logging

from django.db import transaction

from common.models import validate_and_save
from common.permissions import require_perm
{tenant_imp}
from .exceptions import {E}NotFound
from .models import {E}
from .selectors import {e}_list_for

logger = logging.getLogger(__name__)


@transaction.atomic
def {e}_create(*, actor, name: str) -> {E}:
    """Cria {E}. História: H-xxx."""
    require_perm(actor, "{app}.add_{e}")
    obj = {E}(name=name.strip(), created_by=actor, updated_by=actor{tenant_kw})
    validate_and_save(obj)
    transaction.on_commit(lambda: logger.info("{e}.created", extra={{"{e}_id": obj.pk}}))
    return obj


def {e}_list_for_update(*, actor):
    """Lock pessimista respeitando a visibilidade do actor."""
    return {e}_list_for(actor=actor).select_for_update()


@transaction.atomic
def {e}_update(*, actor, {e}_id: int, name: str) -> {E}:
    """Atualiza {E}. História: H-xxx."""
    require_perm(actor, "{app}.change_{e}")
    try:
        obj = {e}_list_for_update(actor=actor).get(pk={e}_id)
    except {E}.DoesNotExist:
        raise {E}NotFound({e}_id={e}_id) from None
    obj.name = name.strip()
    obj.updated_by = actor
    validate_and_save(obj, update_fields=["name", "updated_by", "updated_at"])
    return obj
''',
        "selectors.py": f'''"""Consultas de {E}. Aplicam visibilidade do actor; não gravam nada."""

from django.db.models import QuerySet

{scope_imp}from .exceptions import {E}NotFound
from .models import {E}


def {e}_list_for(*, actor, status: str | None = None) -> QuerySet[{E}]:
    qs = {E}.objects.all()
    {"qs = scope_to_tenant(qs, actor)" if tenant else "# TODO: regra de visibilidade (ex.: dono) — nunca deixe aberto por padrão"}
    if status:
        qs = qs.filter(status=status)
    return qs


def {e}_get(*, actor, {e}_id: int) -> {E}:
    try:
        return {e}_list_for(actor=actor).get(pk={e}_id)
    except {E}.DoesNotExist:
        raise {E}NotFound({e}_id={e}_id) from None
''',
        "admin.py": f'''from django.contrib import admin

from .models import {E}


@admin.register({E})
class {E}Admin(admin.ModelAdmin):
    list_display = ["id", "name", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at", "created_by", "updated_by"]
    # Ações que mudam estado devem chamar services, nunca queryset.update().
''',
        "migrations/__init__.py": "",
        "tests/__init__.py": "",
        "tests/factories.py": f'''import factory

from apps.{app}.models import {E}


class {E}Factory(factory.django.DjangoModelFactory):
    class Meta:
        model = {E}

    name = factory.Sequence(lambda n: f"{E} {{n}}")
''',
        "tests/test_services.py": f'''import pytest

from apps.{app} import services
from apps.{app}.models import {E}
from common.exceptions import PermissionDeniedError

pytestmark = pytest.mark.django_db


def test_{e}_create_persists_with_audit(user_with_perms):
    actor = user_with_perms("{app}.add_{e}")
    obj = services.{e}_create(actor=actor, name="  Exemplo  ")
    assert {E}.objects.filter(pk=obj.pk, name="Exemplo", created_by=actor).exists()


def test_{e}_create_requires_permission(user):
    with pytest.raises(PermissionDeniedError):
        services.{e}_create(actor=user, name="Exemplo")
''',
        "tests/test_selectors.py": f'''import pytest

from apps.{app} import selectors
from apps.{app}.exceptions import {E}NotFound
from apps.{app}.tests.factories import {E}Factory

pytestmark = pytest.mark.django_db


def test_{e}_get_raises_domain_error_when_missing(user):
    with pytest.raises({E}NotFound):
        selectors.{e}_get(actor=user, {e}_id=999999)


def test_{e}_list_filters_by_status(user):
    active = {E}Factory()
    {E}Factory(status="inactive")
    assert list(selectors.{e}_list_for(actor=user, status="active")) == [active]
''',
    }


EXTRAS = {
    "validators": '''from django.core.exceptions import ValidationError


# Regras de validação reutilizáveis deste domínio.
# def validate_xxx(value) -> None:
#     if ...:
#         raise ValidationError("Mensagem.", code="invalid_xxx")
''',
    "constants": '''# Constantes e máquinas de estado deste domínio.
# ALLOWED_TRANSITIONS: dict[str, set[str]] = {}
''',
    "ports": '''"""Interfaces que este domínio precisa do mundo externo.
Implementação concreta vive em apps/integrations/<provider>/adapter.py (ou async/ai-mcp)
e é registrada em settings.PORTS. O domínio obtém com common.ports.get_port("<nome>").
Nunca importar o adapter aqui.
"""

# from typing import Protocol
#
#
# class AlgumGateway(Protocol):
#     def fazer_algo(self, *, param: str) -> str: ...
''',
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("app", help="nome do app em snake_case (ex.: sales)")
    p.add_argument("--entidade", required=True, help="entidade principal em PascalCase (ex.: Order)")
    p.add_argument("--raiz", default=".", help="pasta do backend (onde está manage.py)")
    p.add_argument("--extras", default="", help="lista: validators,constants,ports")
    p.add_argument("--tenant", action="store_true", help="entidade pertence a um tenant (herda TenantModel)")
    a = p.parse_args()

    if not re.fullmatch(r"[a-z][a-z0-9_]*", a.app):
        print("Nome do app deve ser snake_case.", file=sys.stderr)
        return 1
    if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", a.entidade):
        print("Entidade deve ser PascalCase.", file=sys.stderr)
        return 1

    base = Path(a.raiz) / "apps" / a.app
    files = templates(a.app, a.entidade, tenant=a.tenant)
    for extra in filter(None, (x.strip() for x in a.extras.split(","))):
        if extra not in EXTRAS:
            print(f"Extra desconhecido: {extra}", file=sys.stderr)
            return 1
        files[f"{extra}.py"] = EXTRAS[extra]

    created, skipped = [], []
    for rel, content in files.items():
        path = base / rel
        if path.exists():
            skipped.append(rel)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        created.append(rel)

    apps_init = Path(a.raiz) / "apps" / "__init__.py"
    if not apps_init.exists():
        apps_init.write_text("", encoding="utf-8")

    print(f"App apps/{a.app} — criados: {len(created)}, já existiam: {len(skipped)}")
    for f in skipped:
        print(f"  (mantido) {f}")
    print("\nPróximos passos:")
    print(f'  1. Adicionar "apps.{a.app}" em LOCAL_APPS (config/settings/base.py)')
    print("  2. Ajustar campos, constraints, índices e permissões em models.py")
    print("  3. Definir a regra de visibilidade em selectors.py (TODO)")
    print(f"  4. uv run python manage.py makemigrations {a.app} && revisar a migration")
    print(f"  5. uv run pytest apps/{a.app}")
    print("  6. Apagar arquivos que não forem usados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
