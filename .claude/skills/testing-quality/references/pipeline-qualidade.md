# Pipeline e qualidade estática

Leia quando a conversa envolver lint, type check, CI, cobertura, quality gates ou teste instável.

## Qualidade estática

Padronizar lint, format e type check quando adotado.

| Ponta | Ferramentas típicas |
|---|---|
| Backend (Python) | Ruff; Pyright ou mypy quando aplicável |
| Frontend | ESLint; TypeScript; formatter adotado pelo projeto |

Lint garante padrão e detecta alguns erros. **Lint não é teste** — não substitui validação de comportamento. Projeto com lint impecável e zero teste de regra de negócio não tem qualidade comprovada.

## CI

Toda alteração relevante passa automaticamente por:

```text
lint → testes → build → checagens necessárias
```

antes da integração.

Pipeline mínimo:

```text
checkout → install → lint → tests → build
```

Adicionar conforme o projeto: security checks, integration tests, E2E.

## Fast feedback

Ordenar para falhar rápido e barato:

```text
lint rápido → unit tests → integration → E2E
```

Não rodar dezenas de minutos de E2E antes dos unitários. Quem espera 40 minutos para descobrir erro de import perde o hábito de rodar o pipeline.

## Execução local

Dev ou agente precisa conseguir rodar sem depender do CI:

```text
testes do domínio
teste específico
suíte completa
```

Comandos padronizados ajudam, expostos por script quando útil:

```text
test
test-unit
test-integration
test-e2e
lint
quality
```

## Cobertura

Cobertura é **indicador, não objetivo**.

```text
100% coverage ≠ qualidade garantida
```

Cobertura sem assert relevante não vale nada — código executado não é código verificado.

Definir meta só quando ajudar:

```text
código crítico → cobertura alta
infra simples  → cobertura pragmática
```

Nunca sacrificar qualidade de teste para perseguir número.

## Quality gates

O pipeline pode bloquear merge/deploy quando:

```text
lint falha
teste crítico falha
build falha
cobertura crítica cai
contract test crítico falha
```

Quality gate precisa representar **risco real**. Gate por métrica inútil treina o time a ignorar gate — e aí o gate que importa também é ignorado.

## Teste falhando

Nunca ignorar teste falhando para marcar história como concluída.

Se o teste é que está errado: corrigir o teste e registrar o motivo quando relevante. "O teste está errado" sem análise é a forma mais comum de apagar um defeito real.

## Skip

`skip` é excepcional. Todo teste pulado tem motivo claro e registrado.

## Flaky

Teste intermitente é **defeito**, não característica. Não normalizar "às vezes falha" — investigar e corrigir.

Causas mais comuns, em ordem:

```text
dependência de tempo real
ordem de execução entre testes
estado compartilhado não limpo
concorrência não controlada
rede ou serviço externo real
```

Quarentena é aceitável como medida temporária, desde que exista pendência clara de correção. Flaky crítico aceito silenciosamente bloqueia a aprovação de QA.
