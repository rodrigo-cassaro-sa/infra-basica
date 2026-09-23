# Cronograma

## Objetivo

Este documento é a previsão viva do projeto.

Ele deve permitir responder:

- qual é a capacidade acordada;
- quanto falta para concluir o backlog;
- qual é a próxima história;
- o que está bloqueado e por quê;
- quando a previsão foi recalculada pela última vez.

O cronograma é persistente e não pode contradizer `docs/historias/indice.md`.
Qualquer divergência entre os dois é resolvida a favor do índice.

Proprietária: `project-governance`.

---

## Capacidade

A unidade oficial de produtividade é:

```text
histórias prontas para homologação / dia
```

O calendário usa **dias corridos**.

```text
Capacidade configurada: PENDENTE
Média real observada:   sem histórico
```

A capacidade é uma definição humana. Não alterar automaticamente.

Quando houver histórico suficiente, registrar a média real **ao lado** da capacidade
configurada, sem substituí-la. Havendo diferença persistente: informar, sugerir revisão
e aguardar decisão.

---

## Previsão

```text
Backlog restante: A PREENCHER
Previsão:         A PREENCHER
Última revisão:   —
```

Cálculo básico:

```text
histórias que ainda não atingiram "pronta para homologação"
÷ capacidade configurada
```

Arredondar para cima e, depois, ajustar por dependências, bloqueios, decisões pendentes,
ordem funcional e mudanças de escopo.

Não apresentar precisão falsa. Uma previsão com ressalvas explícitas vale mais do que
uma data exata que ninguém sustenta.

---

## Dependências

| História | Depende de | Observação |
|---|---|---|
| — | — | — |

Registrar apenas dependência real. Proximidade de número não é dependência.

---

## Bloqueios

Bloqueio não cria status novo: a história mantém o seu e o motivo é registrado aqui.

| História | Motivo | Desde | Quem destrava |
|---|---|---|---|
| — | — | — | — |

Causas possíveis: dependência, decisão, ambiguidade, contrato, modelo de dados,
integração, segurança, infraestrutura, requisito externo, teste crítico.

---

## Próxima história

```text
Próxima:  A PREENCHER
Motivo:   A PREENCHER
```

A escolha considera status, dependências, bloqueios, sequência funcional e prioridade de
negócio — não o menor código livre. Na ausência de prioridade de negócio definida, usar
dependências e lógica funcional **e informar** que a prioridade está ausente.

---

## Histórico de recálculo

| Data | Evento | Efeito na previsão |
|---|---|---|
| — | — | — |

Recalcular a cada: nova história, cancelamento, história pronta para aprovação, aprovação,
início de desenvolvimento, bloqueio, desbloqueio, teste crítico que falhou ou passou,
mudança de escopo, história pronta para homologação, homologação, publicação, decisão que
altera dependência, mudança de capacidade.
