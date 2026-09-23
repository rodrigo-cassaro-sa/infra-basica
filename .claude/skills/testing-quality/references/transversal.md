# Trilha transversal

Leia quando a mudança atravessar as duas pontas, ou envolver contratos, filas, E2E, smoke, regressão, dados de teste ou mocks.

## Índice

1. [Teste de integração](#1-teste-de-integração)
2. [Teste de contrato](#2-teste-de-contrato)
3. [Compatibilidade entre deploys](#3-compatibilidade-entre-deploys)
4. [E2E](#4-e2e)
5. [Smoke tests](#5-smoke-tests)
6. [Regressão](#6-regressão)
7. [Dados de teste, factories e fixtures](#7-dados-de-teste-factories-e-fixtures)
8. [Mocks sem overmocking](#8-mocks-sem-overmocking)
9. [Tempo, IDs e determinismo](#9-tempo-ids-e-determinismo)
10. [Feature flags e rollback](#10-feature-flags-e-rollback)
11. [Testes manuais](#11-testes-manuais)
12. [Técnicas opcionais](#12-técnicas-opcionais)

---

## 1. Teste de integração

Valida múltiplas camadas juntas:

```text
service + banco
API + service
frontend + API mockada
fila/worker + banco
adapter + mock server
```

É o nível que pega o que o unitário não pega: mapeamento errado, transação que não commita, serialização quebrada.

---

## 2. Teste de contrato

Valida que a fronteira entre sistemas continua compatível:

```text
frontend ↔ API
backend ↔ provider externo
backend ↔ MCP / serviço interno
```

Verificar em cada lado:

```text
campos
tipos
status
schema
formato dos erros
```

Contrato quebrado passa em todos os testes unitários dos dois lados e ainda assim derruba o produto. Por isso ele é teste próprio, não consequência dos outros.

---

## 3. Compatibilidade entre deploys

Quando frontend e backend deployam separadamente, e o requisito de janela de migração existir:

```text
API nova não quebra cliente antigo
```

Testar backward compatibility sempre que o contrato exigir compatibilidade. Campo removido, campo renomeado e mudança de tipo são os três casos que mais quebram.

---

## 4. E2E

Representa fluxo real importante, ponta a ponta:

```text
abrir app → criar usuário → confirmar conta → login
```

Cobrir fluxos **críticos**, não toda combinação possível. E2E é caro e lento; a maior parte da segurança vem de testes menores. Se um cenário pode ser provado em integração, prove lá.

Checklist de um E2E que vale a pena:

```text
[ ] fluxo crítico de verdade
[ ] autenticação real
[ ] permissões
[ ] backend
[ ] frontend
[ ] persistência
[ ] resultado final verificado (não só "não deu erro")
```

---

## 5. Smoke tests

Depois de deploy, validação rápida:

```text
app sobe
API responde
login funciona
banco acessível
rota crítica responde
```

Smoke de produção precisa ser seguro — nunca destrutivo. Coordenação com OPS-01 para quando e onde rodam.

---

## 6. Regressão

```text
BUG ENCONTRADO → TESTE QUE REPRODUZ → CORREÇÃO → TESTE PASSA
```

O teste é escrito **antes** da correção e precisa falhar antes dela. Teste escrito depois, que já passa, não prova que reproduz o bug.

Bug encontrado durante QA segue: registrar → relacionar com a história → corrigir → adicionar teste de regressão → revalidar.

---

## 7. Dados de teste, factories e fixtures

Criar o dado mínimo necessário para o caso. Fixture gigante sem relação com o teste torna a falha ilegível e o teste frágil.

Factories quando o volume de objetos crescer: `UserFactory`, `CustomerFactory`, `OrderFactory`.

Fixtures para dados estáveis e realmente compartilhados. Evitar fixture global gigante.

Nunca usar dado real sensível. Use dados sintéticos ou fixtures sanitizadas.

---

## 8. Mocks sem overmocking

Mocke a **fronteira externa**: provedor de e-mail, pagamento, LLM, CRM, WhatsApp.

Se um teste mocka ao mesmo tempo:

```text
service + repository + model + validator + permission
```

ele provavelmente testa a própria configuração dos mocks e nada do sistema. Quando perceber isso, suba o teste um nível: transforme em integração com banco de testes.

---

## 9. Tempo, IDs e determinismo

Congelar ou controlar o tempo quando o comportamento depender de expiração, prazo, agendamento, data ou timezone.

Não depender de IDs fixos (`id = 1`) que o teste não garante.

Testes assíncronos não esperam tempo real — testam lógica de retry, agendamento, publicação e estado com clocks controlados.

Evitar dependência sem controle de: hora atual, rede real, ordem aleatória, dados externos, serviços reais.

---

## 10. Feature flags e rollback

Funcionalidade atrás de flag precisa de teste nos dois estados:

```text
flag on
flag off
```

Mudança crítica: validar que rollback ou versão anterior continua viável quando o requisito existir (coordenação com OPS-01).

Ambiente de teste deve se aproximar de produção quando o comportamento depender de infraestrutura.

---

## 11. Testes manuais

Válidos quando a automação não compensa:

```text
experiência visual
integração física
dispositivo específico
```

Registrar evidência mínima (passos, resultado, data, quem executou) no mapa de testes.

Se o teste manual se repete com frequência e é automatizável: automatizar. Mas não automatizar teste frágil de baixo valor só para aumentar a contagem — custo de manutenção é real.

---

## 12. Técnicas opcionais

Adotar quando trouxerem valor, nunca como requisito padrão:

| Técnica | Quando faz sentido |
|---|---|
| Mutation testing | módulos críticos, projeto maduro |
| Property-based testing | parsers, validadores, regras matemáticas, transformações |
| Visual regression | interface estável e crítica |
| Teste de carga | alto volume, campanha, importação, muitos usuários, fila, API pública |

Carga pesada nunca em produção sem planejamento.
