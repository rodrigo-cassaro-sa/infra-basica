# Listagem, filtros e performance

## Paginação

Toda lista é paginada, com padrão global definido — não dependa de cada view lembrar.

```python
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
}
```

Formato de resposta:

```json
{"count": 1250, "next": "...", "previous": null, "results": []}
```

Permita `page_size` do cliente apenas com teto (`max_page_size`), senão `?page_size=100000` derruba o banco. Para tabelas muito grandes com scroll infinito, avalie cursor pagination (estável sob inserções concorrentes).

## Filtros

Query params, declarativos com `django-filter`:

```text
GET /api/v1/customers/?active=true
GET /api/v1/customers/?search=rodrigo
GET /api/v1/orders/?status=pending&customer=123
```

```python
class OrderFilter(django_filters.FilterSet):
    created_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")

    class Meta:
        model = Order
        fields = ["status", "customer"]
```

Filtro declarado no FilterSet aparece no OpenAPI; filtro lido manualmente de `request.query_params` costuma ficar fora da documentação e sem validação.

## Ordenação

```text
?ordering=created_at
?ordering=-created_at
```

Restrinja `ordering_fields` a uma lista explícita de campos indexados. Ordenação arbitrária sobre coluna sem índice vira lentidão silenciosa em produção.

## Busca

Defina quais campos são pesquisáveis (`search_fields`). Busca textual irrestrita em todas as colunas é cara e imprevisível. Para volume alto, avalie `SearchVector`/índice GIN do PostgreSQL — e só considere solução externa de busca quando houver necessidade comprovada.

## Performance

Problemas típicos, em ordem de frequência:

1. **N+1** — serializer acessando relação sem `select_related`/`prefetch_related` no selector.
2. **Serializer que consulta por item** — `SerializerMethodField` fazendo query dentro do loop. Resolva com anotação no queryset (`annotate`) ou prefetch.
3. **Payload gigante** — campos desnecessários, nested profundo. Use serializer de lista enxuto e deixe o detalhe para o retrieve.
4. **Count caro** — `count` de tabela enorme com filtro sem índice; avalie cursor pagination.

O selector é quem prepara o queryset pronto para serializar:

```python
# apps/sales/selectors.py (core)
def order_list_for(*, actor) -> QuerySet[Order]:
    return (
        scope_to_tenant(Order.objects.all(), actor)
        .select_related("customer")
        .prefetch_related("items")
        .annotate(items_count=Count("items"))
    )
```

Ao revisar um endpoint de lista, conte as queries no teste (`django_assert_num_queries`): o número não pode crescer com a quantidade de itens da página.
