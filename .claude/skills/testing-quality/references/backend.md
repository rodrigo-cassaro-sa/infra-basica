# Trilha backend

Leia quando a mudança tocar models, services, selectors, API, permissões, tasks, integrações externas, IA, banco ou migrations.

## Índice

1. [Ordem de prioridade](#1-ordem-de-prioridade)
2. [Models](#2-models)
3. [Services](#3-services)
4. [Selectors](#4-selectors)
5. [API](#5-api)
6. [Permissões](#6-permissões)
7. [Tasks assíncronas](#7-tasks-assíncronas)
8. [Integrações externas](#8-integrações-externas)
9. [IA / LLM](#9-ia--llm)
10. [Banco de dados e migrations](#10-banco-de-dados-e-migrations)
11. [Listagem, busca e limites](#11-listagem-busca-e-limites)
12. [Concorrência e performance](#12-concorrência-e-performance)

---

## 1. Ordem de prioridade

Quando não dá para testar tudo de uma vez:

```text
services > permissões > API > selectors > tasks > integrações > models
```

Services carregam a regra de negócio. É onde o teste tem mais valor por linha.

---

## 2. Models

Testar quando houver customização:

```text
constraints
defaults
choices
propriedades calculadas
relações
validações de entidade
```

Não testar comportamento nativo do framework sem customização — isso testa o Django, não o produto.

---

## 3. Services

Prioridade máxima. Testar:

```text
casos de uso
regras de negócio
transações
mudança de estado
efeitos esperados (e-mail enfileirado, evento publicado, saldo debitado)
erros de domínio
```

```python
def test_approve_order_updates_status():
    order = OrderFactory(status=Order.Status.PENDING)

    approve_order(order=order, approved_by=UserFactory())

    order.refresh_from_db()
    assert order.status == Order.Status.APPROVED
```

Para cada regra: um teste do caminho que funciona e um do que deve falhar com erro de domínio específico.

---

## 4. Selectors

Testar quando a consulta representa regra relevante:

```text
filtros
escopo
tenant
ordenação
relações
caso vazio
```

Isolamento de tenant em selector é teste obrigatório quando o sistema é multi-tenant — é aí que vazamento de dados costuma nascer.

---

## 5. API

Testar por endpoint:

```text
rota
método
autenticação
permissão
entrada (validação de payload)
saída (schema do response)
status HTTP
erros
paginação
filtros
```

O contrato testado aqui deve corresponder a `docs/contratos-de-api.md`. Divergência entre documento e comportamento é defeito, não detalhe.

---

## 6. Permissões

Toda funcionalidade privada crítica precisa de quatro testes:

```text
[ ] usuário autorizado          → sucesso
[ ] autenticado sem permissão   → 403
[ ] não autenticado             → 401
[ ] objeto de outro dono/tenant → negado (404 ou 403, conforme a política)
```

Esse bloco é o que o frontend **não** consegue provar. Ele precisa existir aqui.

---

## 7. Tasks assíncronas

Testar o comportamento próprio da task:

```text
publicação
execução
retry
erro transitório vs. permanente
falha final
estado persistido
idempotência
```

A regra de negócio principal continua testada no service — a task testa o envelope, não o conteúdo.

Não esperar tempo real: controle clock, agendamento e retry com mocks.

---

## 8. Integrações externas

Testar:

```text
adapter
schema de request/response
timeout
erro externo
429 (rate limit)
5xx
payload inválido
idempotência
```

Não chamar provider real em teste unitário. Mas integração crítica também merece um **contract test** separado, rodando contra sandbox, que responda:

```text
o provider ainda aceita nossa autenticação?
o schema continua igual?
```

Esse teste roda fora da suíte rápida (agendado ou em job próprio), porque depende de rede.

---

## 9. IA / LLM

Testar:

```text
structured output válido
schema inválido → tratamento
provider indisponível → fallback
autorização antes da chamada
RAG filtrado por permissão/tenant
prompt injection relevante ao caso
tool permissions
```

Use fake provider na maioria dos testes. Testes que chamam modelo real são caros, lentos e não determinísticos — reserve para verificação pontual, nunca para a suíte principal.

O ponto crítico: **o filtro de permissão do RAG precisa ser testado com dados de dois tenants**. Recuperar documento de outro cliente é vazamento, não imprecisão.

---

## 10. Banco de dados e migrations

```text
[ ] banco de testes isolado — nunca a suíte contra produção
[ ] PostgreSQL nos testes cujo comportamento depende dele
[ ] CI verifica migration ausente, quebrada ou em conflito
[ ] migration que transforma dado crítico tem teste do caminho de migração
[ ] mudança de model considera dados já existentes, não só banco vazio
```

Não assuma que SQLite representa o comportamento de produção.

Seeds de desenvolvimento ficam separados de dados de produção. Fixtures nunca contêm dado real sensível — use dados sintéticos ou sanitizados.

---

## 11. Listagem, busca e limites

APIs de lista precisam de teste de:

```text
primeira página
próxima página
filtro
ordenação
lista vazia
```

Busca:

```text
termo existente
termo inexistente
acentos quando relevante
case
paginação do resultado
```

Limites definidos pela regra viram teste direto: `máximo 40 pessoas`, `máximo 12h`, `limite 10 MB`. Testar no limite e um passo além.

---

## 12. Concorrência e performance

Testar concorrência quando houver risco real de corrida:

```text
estoque
pagamento
reserva
permissão
```

Idempotência é obrigatória onde a operação pode repetir (webhook, pagamento, task, importação): execute duas vezes e valide o **estado final**, não só a ausência de exceção.

Performance básica: quando o fluxo tem requisito declarado (tempo máximo, volume mínimo, latência), valide. QA-01 também detecta N+1 e queries excessivas em fluxos críticos. Carga pesada e performance avançada pertencem à OPS-01.
