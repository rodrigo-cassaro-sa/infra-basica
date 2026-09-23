# Checklists de passagem de status

Cada lista é o portão de um status. Verificar os itens **aplicáveis** — e quando
um item não se aplica, dizer por quê, em vez de omiti-lo. Item ignorado em
silêncio é a forma mais comum de uma história chegar quebrada em HOM.

## Índice

- [DoR — pronta para aprovação](#dor--pronta-para-aprovação)
- [DoR — implementação (antes de P-05)](#dor--implementação-antes-de-p-05)
- [DoD — pronta para homologação](#dod--pronta-para-homologação)
- [DoD — homologada](#dod--homologada)
- [DoD — implementada](#dod--implementada)
- [DoD — governança saudável](#dod--governança-saudável)

---

## DoR — pronta para aprovação

```text
[ ] código e título
[ ] capítulo
[ ] contexto
[ ] objetivo
[ ] atores
[ ] pré-condições
[ ] fluxo principal
[ ] fluxos alternativos relevantes
[ ] exceções relevantes
[ ] regras conhecidas
[ ] validações
[ ] permissões
[ ] dados envolvidos
[ ] integrações
[ ] dependências
[ ] resultado esperado
[ ] critérios de aceite testáveis
[ ] nenhuma ambiguidade bloqueante
[ ] nenhuma decisão crítica pendente
```

## DoR — implementação (antes de P-05)

```text
[ ] história aprovada
[ ] P-03 concluído
[ ] regras consolidadas
[ ] fluxo claro
[ ] modelo de dados suficiente
[ ] contrato de API suficiente quando aplicável
[ ] mapa de telas suficiente quando aplicável
[ ] guia visual suficiente quando houver frontend
[ ] dependências resolvidas
[ ] nenhuma decisão crítica pendente
[ ] nenhuma ambiguidade bloqueante
```

## DoD — pronta para homologação

```text
[ ] história aprovada
[ ] documentação DAH coerente
[ ] backend implementado
[ ] frontend implementado
[ ] integrações implementadas
[ ] migrations criadas/testadas
[ ] mapa de testes atualizado
[ ] critérios de aceite validados
[ ] testes funcionais aprovados
[ ] integração aprovada
[ ] E2E aprovado quando aplicável
[ ] usabilidade aprovada quando aplicável
[ ] segurança aprovada quando aplicável
[ ] lint/type/build aprovados quando aplicáveis
[ ] nenhuma falha crítica
[ ] nenhuma decisão crítica pendente
[ ] nenhuma pendência bloqueante
[ ] mapa de decisões atualizado quando necessário
[ ] diário atualizado
[ ] cronograma atualizado
```

## DoD — homologada

```text
[ ] deploy em HOM concluído
[ ] migrations de HOM concluídas
[ ] health checks passaram
[ ] QA integrado passou
[ ] E2E aplicável passou
[ ] usabilidade aplicável passou
[ ] SEC aplicável passou
[ ] integrações de HOM passaram
[ ] mapa de testes atualizado
[ ] nenhuma falha bloqueante
```

## DoD — implementada

```text
[ ] estava homologada
[ ] aprovação humana para PROD foi obtida
[ ] mesmo artefato homologado foi promovido quando possível
[ ] deploy PROD concluído
[ ] migrations PROD concluídas
[ ] health checks passaram
[ ] smoke tests passaram
[ ] logs foram verificados
[ ] nenhuma falha crítica permanece
[ ] mapa de testes atualizado
[ ] diário atualizado
[ ] cronograma atualizado
```

## DoD — governança saudável

A governança está saudável quando:

1. índice e arquivos de histórias estão sincronizados;
2. status seguem o fluxo oficial;
3. histórias aprovadas possuem aprovação humana explícita;
4. documentos consolidados representam o sistema atual;
5. mapa de testes possui rastreabilidade suficiente;
6. histórias prontas para homologação atendem o DoD de DEV;
7. histórias homologadas foram validadas em HOM;
8. histórias implementadas foram entregues e validadas em PROD;
9. decisões relevantes estão registradas;
10. decisões pendentes estão explícitas;
11. diário permite retomada;
12. cronograma representa o estado real;
13. bloqueios possuem motivo;
14. dependências estão identificadas;
15. nenhuma documentação paralela desnecessária foi criada;
16. o próximo prompt pode ser determinado pelo estado do projeto;
17. outro agente consegue retomar o trabalho sem perder contexto.
