---
name: backend-core
description: Padrão da software house para o NÚCLEO DE DOMÍNIO de backends Python + Django + PostgreSQL (BE-01) — models, constraints, services, selectors, validators, exceções de domínio, permissões, transações, concorrência, auditoria, migrations, settings por ambiente, logging e testes do núcleo. Use SEMPRE que for criar, revisar ou refatorar um backend Django, iniciar projeto/app/módulo Django, modelar entidades, escrever regra de negócio, service, selector, constraint, migration ou teste de domínio, mesmo que o usuário não cite "backend-core" ou "BE-01". É a base da família de skills de backend (backend-core, backend-api, backend-async, backend-ai-mcp, backend-integrations), dona do contrato comum entre elas, e deve ser lida ANTES das outras. Deploy e ambientes (dev/hom/prod) são da skill transversal devops.
---

# BE-01 — backend-core

Núcleo de domínio de um backend Django **desacoplado do frontend**, organizado como
**monólito modular**, com **PostgreSQL** em todos os ambientes.

O núcleo tem que funcionar sozinho: dá pra criar um pedido, aprovar, cancelar e
testar tudo isso **sem HTTP, sem fila, sem IA e sem API externa**. Se a camada de
API for trocada amanhã, nada aqui muda.

---

## 1. Lugar na família de skills

```text
            ┌──────────────┐ ┌───────────────┐ ┌────────────────┐ ┌──────────────────────┐
            │ backend-api  │ │ backend-async │ │ backend-ai-mcp │ │ backend-integrations │
            │ (BE-02)      │ │ (BE-03)       │ │ (BE-04)        │ │ (BE-05)              │
            └──────┬───────┘ └───────┬───────┘ └───────┬────────┘ └──────────┬───────────┘
                   │ chamam services/selectors          │                     │ implementa ports
                   └─────────────────┴──────────┬───────┴─────────────────────┘
                                                ▼
                                   ┌─────────────────────────┐
                                   │ backend-core (BE-01)    │  ← não importa NENHUMA das outras
                                   └─────────────────────────┘
```

Regra de dependência: **as outras 4 importam o core; o core não importa nenhuma delas.**

`references/contratos-entre-skills.md` é a **fonte da verdade da família**: formato de erro,
nomenclatura, tenant, correlation id, event bus, ports, retry, status de job. Se outra skill
divergir dele, vale o contrato. Ler sempre que a tarefa tocar api, async, ai-mcp ou integrations.

| Pertence ao core | NÃO pertence (vai para) |
|---|---|
| models, constraints, índices, migrations | serializers, views, rotas, OpenAPI → **backend-api** |
| services, selectors, validators | Celery, filas, agendamentos, retries → **backend-async** |
| exceções de domínio, permissões de domínio | LLM, agentes, tools MCP, embeddings → **backend-ai-mcp** |
| transações, locks, concorrência | clientes HTTP, webhooks, gateways, WhatsApp, e-mail provider → **backend-integrations** |
| auditoria, soft delete, settings, logging, testes do domínio | |
| **ports** (interfaces `Protocol`) que o domínio precisa | implementação concreta dos ports → **integrations / async / ai-mcp** (registrada em `settings.PORTS`) |
| `common/`: errors, ports, events, jobs, tenancy, logging | ambientes dev/hom/prod, Docker, deploy, Sentry, EasyPanel → **devops** (OPS-01, `stacks/backend-django`) |

---

## 2. Versões padrão (setembro/2026)

| Item | Padrão | Observação |
|---|---|---|
| Python | 3.13 | `requires-python = ">=3.13"`, Ruff `py313` |
| Django | **5.2 LTS** (suporte até abr/2028) | Política LTS→LTS: migrar para **6.2 LTS** quando sair (abr/2027). Projeto novo que precise de `FETCH_PEERS`/`DB_CASCADE` pode nascer em 6.1 e ir pra 6.2. |
| PostgreSQL | 17 | Django 6.1 já exige PG 15+ |
| Driver | `psycopg[binary]` 3.x | nunca psycopg2 em projeto novo |
| Gerenciador | `uv` | `pyproject.toml` + `uv.lock` versionados |
| Qualidade | Ruff, pytest + pytest-django, factory-boy, pre-commit | mypy + django-stubs opcional |

Se o usuário já tem projeto com outra versão, **respeitar a versão existente** e só sugerir upgrade.

---

## 3. Fluxo de trabalho ao acionar esta skill

1. **Identificar o domínio.** Listar módulos (apps) por área de negócio, não por tipo técnico. Se existirem histórias DAH (`H-xxx`), cada história que altera estado vira ≥1 service; cite o código da história na docstring do service.
2. **Projeto novo?** Montar estrutura, `pyproject.toml`, settings por ambiente, `.env.example`, docker-compose do Postgres e `common/` → copiar de `references/estrutura-e-config.md`.
3. **Módulo novo?** Rodar o scaffold:
   ```bash
   python scripts/novo_modulo.py <nome_do_app> --entidade <NomeEntidade> --raiz backend/
   ```
   Depois preencher os arquivos gerados. Apagar o que não for usado (não manter arquivo vazio).
4. **Models + constraints + índices** (seção 5).
5. **Exceções** do módulo herdando de `common.exceptions` (seção 8).
6. **Services** para tudo que altera estado (seção 6).
7. **Selectors** para toda consulta relevante (seção 7).
8. **Permissões** de domínio no `Meta.permissions` + checagem no service (seção 9).
9. **Testes** das regras, permissões, constraints e consultas (`references/testes-e-qualidade.md`).
10. **Migrations**: `makemigrations`, revisar o arquivo gerado, commitar junto.
11. Rodar **checklist** (seção 15) e entregar.

Padrões de código completos (base models, hierarquia de exceções, permissões,
módulo de exemplo com concorrência, validador de CPF/CNPJ, migrations seguras):
`references/padroes-de-dominio.md`.

---

## 4. Princípios e "onde fica cada coisa"

```text
clareza > abstração            domínio > framework
regra explícita > mágica       segurança > conveniência
consistência > gosto pessoal   teste > confiança manual
monólito modular > microserviço prematuro
```

| Preciso de... | Vai em | Nome típico |
|---|---|---|
| Alterar estado (criar, aprovar, cancelar, transferir) | `services.py` | `order_approve()`, `customer_create()` |
| Ler dados com regra (filtro, visibilidade, joins) | `selectors.py` | `order_list_for()`, `customer_get()` |
| Regra reutilizável de validação | `validators.py` (do app ou `common/`) | `validate_cpf()` |
| Integridade que o banco garante | `Meta.constraints` do model | `UniqueConstraint`, `CheckConstraint` |
| Propriedade simples só com campos do próprio model | `@property` no model | `is_overdue` |
| Propriedade que cruza relações | selector (evita N+1) | `order_total_for()` |
| Erro de negócio | `exceptions.py` do app | `OrderAlreadyApproved` |
| Constantes/choices | `constants.py` ou `TextChoices` no model | `OrderStatus` |
| Falar com mundo externo | **port** (`ports.py`) + `get_port("...")` | `PaymentGateway` |
| Efeito depois do commit (e-mail, sync, notificação) | `transaction.on_commit(lambda: dispatch("order.approved", order_id=...))` | evento `<entidade>.<fato>` |
| Estado de job/processamento | herdar `common.jobs.ProcessingStateModel` | `ImportJob` |
| Dado de tenant | herdar `common.tenancy.TenantModel`; selector usa `scope_to_tenant` | — |

Nomenclatura: `<entidade>_<ação>` (ex.: `order_approve`) → fica fácil de grepar e agrupa por entidade.

---

## 5. Models

Contêm: campos, relacionamentos, constraints, índices, choices, `__str__`, propriedades simples.
**Não contêm**: fluxos de negócio, chamadas externas, lógica em `save()` ou signals.

Todo model de negócio herda de `common.models.BaseModel` (timestamps) ou
`AuditedModel` (timestamps + `created_by`/`updated_by`). Ver `references/padroes-de-dominio.md`.

```python
class Order(AuditedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        APPROVED = "approved", "Aprovado"
        CANCELED = "canceled", "Cancelado"

    customer = models.ForeignKey("customers.Customer", on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(total__gte=0), name="order_total_gte_0"),
        ]
        indexes = [models.Index(fields=["status", "created_at"])]
        permissions = [("approve_order", "Pode aprovar pedido")]
```

Regras fixas:

- **Dinheiro**: `DecimalField(max_digits=12, decimal_places=2)`. Nunca `float`. Cálculo com `Decimal`.
- **Datas**: `USE_TZ = True`, `TIME_ZONE = "America/Sao_Paulo"`, sempre `timezone.now()`; nunca `datetime.now()`.
- **Status**: `TextChoices`. Transições validadas no service (ou validator de transição).
- **`on_delete`**: padrão `PROTECT` para dados de negócio; `CASCADE` só para filhos que não existem sem o pai.
- **Strings**: `CharField(blank=True, default="")` em vez de `null=True` (um só "vazio").
- **IDs**: `BigAutoField` (`DEFAULT_AUTO_FIELD`). UUID só com motivo real (exposição pública, geração externa, anti-enumeração) — nesse caso, `public_id = UUIDField(unique=True, default=uuid.uuid4)` ao lado do PK inteiro.
- **Usuário customizado** desde o 1º commit: `AUTH_USER_MODEL = "accounts.User"` (`AbstractUser`). Nunca trocar no meio do projeto.
- **Constraints no banco** para toda regra que o banco consegue garantir (`UniqueConstraint` com `condition=` para unicidade parcial, `CheckConstraint`). Constraint > código.
- **Índices** só com base em consulta real (filtros frequentes, FKs de filtro, status+data, identificadores externos).
- **Multi-tenant**: decidir no início. Padrão da casa: app `tenants` + `User.tenant` + models herdando `TenantModel` + selectors com `scope_to_tenant(qs, actor)`. Selector **nunca** recebe `tenant_id` de fora. Detalhes: `references/padroes-de-dominio.md` §14. Nunca adaptar depois sem planejamento.
- **Referência ao usuário**: sempre `settings.AUTH_USER_MODEL`, nunca string `"users.User"`.

---

## 6. Services — tudo que altera estado

```python
import logging
from django.db import transaction

from common.events import dispatch
from common.permissions import require_perm
from .exceptions import OrderInvalidTransition
from .models import Order

logger = logging.getLogger(__name__)


@transaction.atomic
def order_approve(*, actor, order_id: int) -> Order:
    """Aprova um pedido pendente. História: H-012."""
    require_perm(actor, "sales.approve_order")

    order = Order.objects.select_for_update().get(pk=order_id)
    if order.status != Order.Status.PENDING:
        raise OrderInvalidTransition(current=order.status, target=Order.Status.APPROVED)

    order.status = Order.Status.APPROVED
    order.updated_by = actor
    order.full_clean()
    order.save(update_fields=["status", "updated_by", "updated_at"])

    transaction.on_commit(lambda: dispatch("order.approved", order_id=order.pk))
    return order
```

Contrato de todo service:

- **Só keyword args** (`*,`), com type hints e retorno tipado.
- Recebe **`actor`** (usuário que executa) quando há permissão ou auditoria envolvida. Processos de sistema passam `actor=None` explicitamente e o service documenta isso.
- `@transaction.atomic` quando grava mais de uma coisa ou lê-para-escrever.
- Checa permissão → valida → grava → agenda efeitos colaterais com `transaction.on_commit`.
- `full_clean()` antes de `save()`; `save(update_fields=[...])` em updates.
- Lança **exceção de domínio**; nunca retorna `None`/`False` para indicar erro; nunca `raise Exception("...")`.
- **Nenhuma chamada externa** (HTTP, fila, LLM) dentro da transação. Efeito externo = `on_commit` + `dispatch(evento)`. O core **nunca** importa task (`from apps.x.tasks import ...` é proibido aqui).
- Não conhece `request`, `Response`, serializer nem status HTTP.
- Pequeno e orientado a caso de uso. Service pode chamar outro service.

`ATOMIC_REQUESTS = False`: a transação é responsabilidade do service, não da view.

---

## 7. Selectors — toda leitura relevante

```python
def order_list_for(*, actor, status: str | None = None) -> QuerySet[Order]:
    qs = Order.objects.select_related("customer").order_by("-created_at")
    if not actor.has_perm("sales.view_all_orders"):
        qs = qs.filter(created_by=actor)
    if status:
        qs = qs.filter(status=status)
    return qs


def order_get(*, actor, order_id: int) -> Order:
    try:
        return order_list_for(actor=actor).get(pk=order_id)
    except Order.DoesNotExist:
        raise OrderNotFound(order_id=order_id)
```

- Retornam `QuerySet` (lista, para a camada externa paginar) ou instância.
- Aplicam **visibilidade** (quem vê o quê) — a API não filtra por conta própria.
- `get` que falha vira `XNotFound` (exceção de domínio), não `DoesNotExist` vazando.
- Já trazem `select_related`/`prefetch_related` necessários. Paginação e serialização **não** são do selector.
- Selector não grava nada.

---

## 8. Exceções de domínio

Hierarquia única em `common/exceptions.py` com **categorias** que a camada externa sabe mapear.
Nenhuma outra skill redefine essas classes — todas importam daqui.

```text
DomainError (code, message, fields, details)   → to_dict() = {"code","message","fields","details"}
├── NotFoundError          → recurso inexistente / invisível pro actor
├── PermissionDeniedError  → actor sem permissão
├── ValidationError        → dado inválido
├── ConflictError          → estado não permite (transição inválida, duplicado)
└── BusinessRuleError      → regra de negócio violada (limite, capacidade, saldo)
```

Cada app cria as suas herdando da categoria certa, com `code` estável em MAIÚSCULAS
(`ORDER_INVALID_TRANSITION`). O `code` é contrato público — não renomear.
A API devolve `{"error": exc.to_dict()}`; o Expo decide pelo `code`.

Falha **técnica** (rede, provider, IA) não é `DomainError`: é `common.errors.TransientError`
(pode repetir) ou `PermanentError` (não adianta repetir). Hierarquia única para as 5 skills.
Implementação completa: `references/padroes-de-dominio.md`.

---

## 9. Autenticação e autorização

- **Autenticação** (quem é): `accounts.User`. Mecanismo de login/token é da backend-api.
- **Autorização** (o que pode): permissões de domínio no formato do Django `app_label.codename`
  (`sales.approve_order`, `financial.cancel_invoice`), declaradas em `Meta.permissions`
  e agrupadas em `Group` (papéis) via data migration.
- Checagem **dentro do service** com `require_perm(actor, "...")`, e visibilidade **dentro do selector**.
  Assim API, fila, CLI e agente de IA respeitam as mesmas regras sem repetir código.
- Permissão por objeto (dono, mesmo tenant) = regra explícita no service/selector.
- Padrão é **negar**. Superusuário não é atalho em código de domínio.

---

## 10. Transações e concorrência

- Transações **curtas**. Nada de I/O externo dentro.
- Ler-para-escrever no mesmo registro concorrido → `select_for_update()` (dentro de `atomic`).
- Contadores/saldos → `F()` expressions (`update(stock=F("stock") - qty)`) + `CheckConstraint(stock__gte=0)` como rede de segurança.
- Unicidade sob concorrência → **constraint no banco** e tratar `IntegrityError` convertendo em `ConflictError`. `exists()` antes do insert sozinho não garante nada.
- Efeitos após commit → `transaction.on_commit(...)`.
- Nunca assumir que só uma requisição mexe no dado.

---

## 11. Performance do ORM

- Medir antes de otimizar (`django-debug-toolbar` local, `django_assert_num_queries` nos testes).
- N+1: `select_related` (FK/1-1), `prefetch_related` (reverso/M2M), `Prefetch(queryset=...)` para filtrar.
- `exists()` em vez de `count()`/`len()` para checar existência; `only()`/`values()` em leituras grandes; `iterator(chunk_size=...)` para varreduras; `bulk_create`/`bulk_update` em lote.
- No 6.1+: `fetch_mode(models.FETCH_PEERS)` resolve N+1 automático; `FETCH_RAISE` em testes de selectors críticos.

---

## 12. Migrations

- Versionadas, revisadas e commitadas junto com o model. **Nunca** apagar migrations/banco como rotina.
- CI roda `makemigrations --check --dry-run` (migration faltando = build quebra).
- Data migration usa `apps.get_model(...)`, nunca import direto do model; sempre com `reverse_code` (ou `RunPython.noop` justificado).
- Mudança em tabela grande/produção = passos: adicionar campo nulo → backfill → tornar obrigatório/constraint. Índice em tabela grande: `AddIndexConcurrently` (migration com `atomic = False`).
- `squashmigrations` só em marco planejado.

---

## 13. Auditoria e soft delete

- Todo model de negócio: `created_at`/`updated_at`. Entidade importante: `AuditedModel` (`created_by`/`updated_by`), preenchidos **pelo service** a partir do `actor` (explícito, sem middleware mágico).
- Operação crítica (financeiro, permissão, dado de saúde) → histórico imutável: tabela de eventos própria ou `django-pghistory` (triggers no Postgres).
- Soft delete **só** com motivo (restauração, obrigação legal, vínculo histórico). Quando usar: `deleted_at` + manager padrão filtrando + `UniqueConstraint(..., condition=Q(deleted_at__isnull=True))`.

---

## 14. Configuração, logging e qualidade (resumo)

- Settings: `config/settings/{base,local,test,production}.py`; segredo só por env (`django-environ`); `.env.example` versionado; `.env` no `.gitignore`.
- `production.py` passa limpo em `manage.py check --deploy`.
- Logging: `logging` (nunca `print`), JSON em produção, `correlation_id` via `contextvars` (a camada externa preenche; o core só lê). Nome único: `correlation_id`. Nunca logar senha, token, cookie, CPF completo, dado de saúde.
- Qualidade: Ruff (lint+format), pytest-django, factory-boy, pre-commit. CI mínimo: `ruff` → `makemigrations --check` → `pytest` (com Postgres real).

Arquivos prontos: `references/estrutura-e-config.md` e `references/testes-e-qualidade.md`.

---

## 15. Proibido

```text
❌ regra de negócio em view, serializer, form, admin ou signal
❌ lógica crítica em save() / managers "espertos"
❌ ORM direto na camada de API, task ou tool MCP para ESCREVER (sempre via service)
❌ chamada externa dentro de transaction.atomic
❌ raise Exception("erro") / retornar False como erro
❌ dinheiro em float · datetime.now() · print() como log
❌ SQLite como banco de desenvolvimento
❌ segredo no Git · migrations fora do versionamento
❌ acesso liberado por padrão
❌ core importando api/async/ai-mcp/integrations (inclusive tasks)
❌ selector recebendo tenant_id de fora · FK para "users.User" escrita à mão
❌ abstração prematura (repository genérico, base service mágico, microserviço)
❌ utils.py gigante em common/
```

---

## 16. Checklist BE-01 + Definition of Done

```text
[ ] módulos por domínio, sem arquivos vazios
[ ] AUTH_USER_MODEL customizado desde o início
[ ] models herdam BaseModel/AuditedModel; dinheiro Decimal; status TextChoices
[ ] constraints no banco para as regras garantíveis; índices justificados
[ ] toda alteração de estado passa por service (keyword-only, actor, atomic)
[ ] toda consulta relevante em selector, com visibilidade aplicada
[ ] exceções de domínio com code estável, herdando da categoria certa
[ ] permissões em Meta.permissions, checadas no service
[ ] concorrência tratada (select_for_update / F() / constraint)
[ ] nenhum I/O externo dentro de transação; efeitos via on_commit/ports
[ ] migrations geradas, revisadas e versionadas
[ ] auditoria avaliada; soft delete só com motivo
[ ] settings por ambiente; segredos fora do repo; .env.example atualizado
[ ] logs sem dado sensível
[ ] testes: regras, permissões, transações, constraints, consultas críticas
[ ] ruff + makemigrations --check + pytest passando com PostgreSQL
[ ] core não importa nenhuma das outras 4 skills; efeitos via dispatch()
[ ] tenant aplicado via TenantModel + scope_to_tenant (se multi-tenant)
```

Pronto = um dev novo abre o projeto e acha em minutos: **onde estão os dados, as regras,
as consultas, as permissões, as validações, as transações e os testes.**

---

## Referências (ler conforme a tarefa)

| Arquivo | Quando ler |
|---|---|
| `references/estrutura-e-config.md` | Projeto novo, settings, pyproject, docker-compose, logging |
| `references/padroes-de-dominio.md` | Escrever models/services/selectors/exceções/permissões/migrations |
| `references/testes-e-qualidade.md` | Escrever testes, factories, pre-commit, CI |
| `references/contratos-entre-skills.md` | **Fonte da verdade da família.** Qualquer ponto de contato com api, async, ai-mcp, integrations ou ops |
| `scripts/novo_modulo.py` | Criar um app/módulo novo com a estrutura padrão |
