# Checklists

## Checklist de endpoint

```text
[ ] método definido
[ ] rota versionada (/api/v1/)
[ ] autenticação definida
[ ] permissão definida (incluindo por objeto, se aplicável)
[ ] serializer de entrada explícito (sem mass assignment)
[ ] serializer de saída revisado (sem dado sensível)
[ ] service (escrita) ou selector (leitura) utilizado
[ ] status HTTP correto em todos os caminhos
[ ] erros documentados com code estável (MAIÚSCULAS) e no catálogo
[ ] história DAH (H-xxx) referenciada no contrato
[ ] paginação quando lista
[ ] filtros/ordenação/busca restritos e declarativos
[ ] performance revisada (sem N+1)
[ ] idempotência avaliada se crítico
[ ] OpenAPI atualizado e fiel
[ ] testes de sucesso
[ ] testes de erro
[ ] testes de permissão
```

## Checklist de API (projeto)

```text
[ ] prefixo /api/v1/
[ ] autenticação global JWT (access curto, refresh rotativo + blacklist)
[ ] permissão padrão = negar (IsAuthenticated no mínimo)
[ ] formato de erro único
[ ] exception handler central importando common.exceptions/common.errors (sem classes duplicadas)
[ ] envelope {"error": {code, message, fields, details}}; 400 formato / 422 domínio
[ ] paginação global com teto de page_size
[ ] filtros padronizados (django-filter)
[ ] OpenAPI publicado (/api/schema/, /api/docs/)
[ ] CORS restrito por ambiente
[ ] CSRF coerente com a estratégia de autenticação
[ ] throttling nos endpoints sensíveis
[ ] health check sem dado sensível
[ ] logs com correlation_id (X-Request-ID), rota, status, duração
[ ] X-Request-ID propagado
[ ] client TS do Expo gerado do OpenAPI no CI (sem diff pendente)
[ ] catálogo de error codes atualizado
[ ] suíte de testes e lint no CI
```

## Checklist de code review de PR de API

Perguntas que pegam a maior parte dos problemas:

1. Tem regra de negócio dentro da view? Deveria estar em service.
2. O serializer de saída expõe algum campo que ninguém pediu?
3. A permissão cobre o objeto ou só o "estar logado"?
4. O queryset está escopado ao tenant/usuário no selector (`scope_to_tenant`)? Algum `tenant_id` veio do request?
5. A lista está paginada e sem N+1?
6. O erro novo tem `code` estável e está documentado?
7. A mudança quebra algum contrato existente? Foi classificada?
8. O OpenAPI reflete o que o código faz agora?
9. Existem testes de erro e de permissão, não só do caminho feliz?
10. Endpoint crítico: o que acontece se chamarem duas vezes ao mesmo tempo?
