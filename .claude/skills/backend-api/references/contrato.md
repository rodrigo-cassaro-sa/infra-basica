# Contrato de endpoint

Preencha antes de escrever código. O contrato é o que o app Expo (iOS/Android/web) vai consumir; descobrir divergência depois de implementado custa retrabalho dos dois lados.

## Template

```markdown
### <Nome da operação>

- **História (DAH):** H-012 — mesmo código citado na docstring do service
- **Service/selector:** `order_approve` (BE-01)
- **Método:** POST
- **URL:** /api/v1/orders/{id}/approve/
- **Autenticação:** Bearer token (obrigatória)
- **Permissão:** `sales.approve_order` (checada no service) + pedido do mesmo tenant do usuário (selector)
- **Entrada:** { "note": "string, opcional, max 500" }
- **Saída 200:** OrderDetailSerializer
- **Status possíveis:** 200, 400, 401, 403, 404, 409, 422
- **Erros:**
  - 409 ORDER_ALREADY_APPROVED — pedido já aprovado
  - 409 ORDER_NOT_APPROVABLE — pedido não está em estado aprovável
- **Efeitos colaterais:** muda status para `approved`, registra auditoria, emite evento `order.approved` (BE-03 envia a notificação)
- **Idempotência:** repetir a chamada com pedido já aprovado retorna 409, não duplica efeito
- **Paginação:** n/a
- **Filtros:** n/a
```

## Perguntas que o contrato precisa responder

1. **Quem pode chamar?** Autenticado? Qual permissão de domínio (`app.codename`)? Precisa pertencer ao tenant do objeto?
2. **O que entra?** Campos, tipos, obrigatoriedade, limites. Campo que o cliente não deve controlar (status, owner, valores calculados) **não entra**.
3. **O que sai?** Qual serializer, quais campos. Confirme que nenhum campo sensível vai junto.
4. **Qual status em cada caminho?** Sucesso, validação, não autenticado, sem permissão, não encontrado, conflito de estado.
5. **Que efeito tem no domínio?** Escrita, transição de estado, evento, integração externa, e-mail.
6. **E se chamar duas vezes?** Duplica? Retorna conflito? É naturalmente idempotente?
7. **É lista?** Então paginação, filtros, ordenação e campos buscáveis fazem parte do contrato.

## Recurso ou ação?

- CRUD convencional sobre um recurso → verbos REST padrão.
- Transição de negócio com nome próprio (`approve`, `cancel`, `block`, `refund`, `publish`) → `POST /recurso/{id}/acao/`. Fica mais legível que PATCH em `status`, permite validação e permissão específicas, e documenta a intenção no OpenAPI.
- Operação que não é sobre um recurso existente (relatório, exportação, simulação) → considere um recurso próprio: `POST /api/v1/exports/` devolvendo o job.

## Exemplos de contrato para endpoints críticos

Para cada endpoint crítico, registre na documentação: exemplo de entrada, exemplo de saída de sucesso, exemplos dos erros possíveis, permissões necessárias e efeitos. Use `OpenApiExample` do drf-spectacular para que o exemplo viva junto do schema em vez de num documento paralelo que envelhece.

```python
@extend_schema(
    request=CustomerCreateSerializer,
    responses={201: CustomerDetailSerializer, 409: ErrorSerializer},
    examples=[
        OpenApiExample(
            "Criação simples",
            value={"name": "Acme", "email": "contato@acme.com"},
            request_only=True,
        )
    ],
)
```

## Códigos de erro

Todo `code` novo entra no **catálogo de erros** do projeto (`docs/api/error-codes.md`, gerado ou
mantido junto com o OpenAPI — ver `cliente-expo.md`). O Expo mapeia `code` → mensagem/ação.
Formato: MAIÚSCULAS, inglês, `<ENTIDADE>_<MOTIVO>` (`ORDER_ALREADY_APPROVED`).
