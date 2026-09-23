# Auditoria, retomada e relatório de governança

## Índice

- [Auditoria de consistência](#auditoria-de-consistência)
- [Histórias órfãs](#histórias-órfãs)
- [Testes órfãos](#testes-órfãos)
- [Decisões obsoletas](#decisões-obsoletas)
- [Auditoria de cronograma](#auditoria-de-cronograma)
- [Retomada de projeto](#retomada-de-projeto)
- [Relatório de governança](#relatório-de-governança)
- [Perguntas que a governança deve responder](#perguntas-que-a-governança-deve-responder)

---

## Auditoria de consistência

Verificar os pares:

```text
índice ↔ histórias
histórias ↔ regras
histórias ↔ dados
histórias ↔ API
histórias ↔ fluxos
histórias ↔ telas
histórias ↔ testes
documentos ↔ código
código ↔ testes
decisões ↔ implementação
cronograma ↔ status reais
```

## Histórias órfãs

Detectar os dois sentidos da divergência:

```text
arquivo H-023 existe, mas não está no índice
índice contém H-024, mas o arquivo não existe
```

## Testes órfãos

Detectar `T-xxx` sem história válida, ou história `pronta para homologação` sem
os testes aplicáveis registrados.

## Decisões obsoletas

Detectar decisão `ativa` que contradiz o estado atual do projeto e solicitar
revisão — sem apagar a decisão.

## Auditoria de cronograma

Verificar contagens por status, histórias bloqueadas, capacidade configurada,
dias corridos, data estimada e dependências. O cronograma não pode contradizer o
índice.

## Retomada de projeto

Ao iniciar nova sessão ou quando outro agente assume:

```text
1. ler AGENTS.md
2. ler indice.md
3. ler cronograma.md
4. ler entradas recentes do diário
5. ler decisões pendentes
6. identificar história atual
7. identificar bloqueios
8. determinar próximo prompt
9. determinar próxima ação
```

## Relatório de governança

```text
PROJETO

Backlog:
- total
- planejadas
- rascunho
- prontas para aprovação
- aprovadas
- em desenvolvimento
- prontas para homologação
- homologadas
- implementadas
- canceladas

Cronograma:
- capacidade configurada
- média real observada
- restantes até pronta para homologação
- previsão

Bloqueios:
- ...

Decisões pendentes:
- ...

História atual:
- ...

Próximo prompt:
- ...
```

## Perguntas que a governança deve responder

```text
qual é o estado geral do projeto?
qual história está ativa?
qual é o status dela?
qual prompt deve ser executado agora?
qual história vem depois?
o que está bloqueado?
qual decisão está pendente?
o cronograma está atualizado?
qual é a capacidade configurada?
quais testes ainda bloqueiam?
o sistema está pronto para HOM?
a release está pronta para PROD?
os documentos refletem o código?
o diário permite retomada?
```
