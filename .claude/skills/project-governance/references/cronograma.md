# Cronograma, capacidade e ordem de execução

## Índice

- [Cronograma oficial](#cronograma-oficial)
- [Unidade de produtividade](#unidade-de-produtividade)
- [Capacidade planejada e média real](#capacidade-planejada-e-média-real)
- [Quando recalcular](#quando-recalcular)
- [Cálculo básico](#cálculo-básico)
- [Dependências](#dependências)
- [Escolha da próxima história](#escolha-da-próxima-história)
- [História bloqueada](#história-bloqueada)

---

## Cronograma oficial

`docs/cronograma.md` é persistente — não é apenas saída dinâmica de uma conversa.
Deve representar a previsão atual do projeto e não pode contradizer o índice.

## Unidade de produtividade

Métrica oficial:

```text
histórias prontas para homologação / dia
```

Calendário em **dias corridos**. Capacidade configurada pode ser 10/dia, 5/dia,
3/dia ou outro valor explicitamente definido.

## Capacidade planejada e média real

A capacidade fica registrada no cronograma e **não é alterada automaticamente**.

Quando houver histórico suficiente, registrar a média separadamente:

```text
Capacidade configurada: 5/dia
Média real observada: 4,2/dia
```

A média real não substitui a capacidade planejada por conta própria. Se houver
diferença persistente:

```text
informar → sugerir revisão → aguardar decisão humana
```

## Quando recalcular

```text
nova história · cancelamento · história pronta para aprovação · aprovação
início de desenvolvimento · bloqueio · desbloqueio
teste crítico falhou · teste crítico passou · mudança de escopo
história pronta para homologação · homologação · publicação
decisão que altera dependência · mudança de capacidade
```

## Cálculo básico

```text
histórias que ainda não atingiram "pronta para homologação"
÷ capacidade configurada
```

Arredondar para cima. Depois considerar dependências, bloqueios, decisões
pendentes, ordem funcional e mudanças de escopo.

Não apresentar precisão falsa: uma previsão com ressalvas explícitas é mais útil
do que uma data exata que ninguém pode sustentar.

## Dependências

Identificar dependências reais:

```text
H-010 depende H-004
H-011 depende H-010
H-012 independente
```

Não criar dependência apenas por proximidade de número.

## Escolha da próxima história

Considerar status, dependências, bloqueios, sequência funcional e prioridade de
negócio. Não escolher simplesmente o menor código disponível.

A DAH-01 pode sugerir ordem técnica, mas não redefine prioridade de negócio sem
confirmação humana. Se não houver prioridade definida: usar dependências e lógica
funcional **e informar** que a prioridade de negócio está ausente.

## História bloqueada

Bloqueio não exige status novo. Registrar o motivo:

```text
H-017 bloqueada
Motivo: D-021 pendente
```

Causas possíveis: dependência, decisão, ambiguidade, contrato, modelo de dados,
integração, segurança, infraestrutura, requisito externo, teste crítico.
