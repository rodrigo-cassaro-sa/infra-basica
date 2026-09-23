# Checklists, DoR, DoD e relatório

Marcar apenas itens aplicáveis. Item não aplicável se registra como `n/a` com uma palavra de motivo — não se apaga em silêncio.

## Definition of Ready para QA

Antes de testar a história:

```text
[ ] história clara
[ ] critérios de aceite definidos e testáveis
[ ] implementação disponível
[ ] ambiente funcional
[ ] dependências disponíveis
```

Se faltar item, o bloqueio é da história, não do QA. Diga isso antes de começar.

## Checklist de nova história

```text
[ ] critérios de aceite testáveis
[ ] casos positivos identificados
[ ] casos negativos identificados
[ ] permissões identificadas
[ ] integrações identificadas
[ ] impacto frontend identificado
[ ] impacto backend identificado
[ ] regressão identificada
```

## Checklist backend

```text
[ ] models
[ ] services
[ ] selectors
[ ] permissions
[ ] API
[ ] tasks
[ ] integrations
[ ] migrations
[ ] error paths
```

## Checklist frontend

```text
[ ] componente
[ ] formulário
[ ] navegação
[ ] loading
[ ] error
[ ] empty
[ ] permissions visuais
[ ] responsividade
[ ] acessibilidade
```

## Checklist integração externa

```text
[ ] sucesso
[ ] timeout
[ ] 429
[ ] 5xx
[ ] payload inválido
[ ] retry
[ ] idempotência
```

## Checklist assíncrono

```text
[ ] publicação
[ ] execução
[ ] retry
[ ] falha final
[ ] idempotência
[ ] estado persistido
```

## Checklist E2E

```text
[ ] fluxo crítico
[ ] autenticação
[ ] permissões
[ ] backend
[ ] frontend
[ ] persistência
[ ] resultado final
```

## Checklist final de qualidade

```text
[ ] critérios de aceite atendidos
[ ] testes críticos passam
[ ] sem regressão conhecida crítica
[ ] permissões validadas
[ ] erros tratados
[ ] lint passa
[ ] build passa
[ ] contratos respeitados
[ ] comportamento documentado corresponde ao sistema
```

## Definition of Done — qualidade da história

```text
[ ] mapa de testes atualizado
[ ] critérios de aceite validados
[ ] testes unitários relevantes
[ ] testes de integração relevantes
[ ] API validada quando aplicável
[ ] frontend validado quando aplicável
[ ] permissões validadas
[ ] regressão coberta
[ ] sem teste crítico falhando
[ ] sem flaky crítico conhecido
[ ] evidência disponível
```

## Definition of Done — QA-01 completa

A qualidade está aprovada quando:

1. critérios de aceite possuem validação;
2. regras críticas possuem teste;
3. caminhos positivos e negativos relevantes foram cobertos;
4. permissões foram testadas;
5. integrações possuem tratamento de erro validado;
6. regressões relevantes possuem testes;
7. frontend e backend funcionam juntos quando aplicável;
8. nenhum teste crítico está falhando;
9. não existem flakies críticos aceitos silenciosamente;
10. o pipeline de qualidade passa;
11. documentação e comportamento estão consistentes;
12. a evidência permite à DAH-01 concluir a história.

## Classificação de bug

**Crítico — bloqueia a conclusão** quando afeta:

```text
critério de aceite
segurança
dados
fluxo principal
permissão
integridade
```

**Não crítico — pode não bloquear** quando é:

```text
cosmético
melhoria futura
caso secundário aceito
```

Bug não crítico ainda exige **decisão explícita e registrada** no momento em que a história é marcada como concluída. "A gente resolve depois" sem registro vira dívida invisível.

## Formato do relatório de QA

```text
H-023

Critérios:
- AC-01 OK
- AC-02 OK
- AC-03 FALHA

Testes:
- 18 passaram
- 1 falhou

Bloqueio:
- AC-03: permissão de leitura entre tenants não é negada (T-047)

Status QA: NÃO APROVADO
```

Resultado é binário: `APROVADO` ou `NÃO APROVADO`, com razões objetivas.

Não usar score arbitrário:

```text
evitar:   qualidade = 8/10
preferir: critério atendido / não atendido
```

## Fluxo de status

```text
em desenvolvimento
 ↓
implementação pronta
 ↓
QA-01
 ↓
mapa de testes atualizado com evidências
 ↓
aprovada pela qualidade
 ↓
DAH-01
 ↓
implementada
```

QA-01 não altera status sozinha. A DAH-01 governa o status final e usa a evidência produzida aqui para decidir.
