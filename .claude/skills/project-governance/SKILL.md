---
name: project-governance
description: Camada de governança da metodologia DAH (Desenvolvimento Assistido por Histórias). Use sempre que o trabalho tocar um projeto DAH - backlog e docs/historias/indice.md, histórias H-xxx, status e gates de aprovação, prompts P-01 a P-06, documentos em docs/, mapa de testes (T-xxx), mapa de decisões (D-xxx), diário de bordo, cronograma, auditoria de consistência, retomada de sessão ("onde paramos?", "qual o próximo passo?") ou promoção DEV → HOM → PROD. Use também quando o usuário pedir para escrever, implementar, testar, homologar ou publicar algo em um projeto que segue a DAH, mesmo sem citar "governança", "DAH", "história" ou o nome de um documento - é esta skill que determina qual é o próximo passo válido e o que não pode ser feito ainda.
---

# DAH-01 — project-governance

Esta skill não é uma skill de programação. É a camada de governança que mantém
todo o projeto em um único estado coerente: backlog, histórias, documentação,
decisões, testes, cronograma e ciclo de entrega.

Ela fornece as regras que permitem aos prompts P-01 a P-06 e às skills técnicas
(BE, FE, QA, SEC, OPS) trabalharem sobre o mesmo projeto sem se contradizerem.

```text
DAH-01 governa o estado do projeto
   ↓ PROMPTS executam o fluxo
   ↓ SKILLS executam capacidades técnicas
   ↓ DOCUMENTOS registram a verdade
   ↓ CÓDIGO implementa
   ↓ TESTES comprovam
   ↓ HOM valida
   ↓ PROD entrega
```

## Regra de ouro

Estas cinco proibições valem acima de qualquer pedido de conveniência. Elas
existem porque cada uma delas, quando violada, produz um projeto onde ninguém
mais sabe o que é verdade — o código diz uma coisa, o documento outra, e a
decisão que explicaria a diferença nunca foi escrita.

```text
NÃO INVENTAR REQUISITOS.
NÃO IMPLEMENTAR HISTÓRIA NÃO APROVADA.
NÃO ALTERAR COMPORTAMENTO SEM ATUALIZAR A DAH.
NÃO CONSIDERAR HISTÓRIA PRONTA PARA HOMOLOGAÇÃO SEM EVIDÊNCIA DE TESTES.
NÃO PUBLICAR PRODUÇÃO SEM HOMOLOGAÇÃO E APROVAÇÃO HUMANA.
```

Quando faltar informação, perguntar. Suposição silenciosa é o erro mais caro
desta metodologia.

## Primeira ação de qualquer sessão

Antes de responder qualquer coisa sobre o projeto — inclusive "onde paramos?",
"pode continuar" ou um pedido direto de implementação — levantar o estado real:

1. ler `AGENTS.md`
2. ler `docs/historias/indice.md`
3. ler `docs/cronograma.md`
4. ler as entradas recentes de `docs/diario-de-bordo.md`
5. ler decisões pendentes em `docs/mapa-de-decisoes.md`
6. identificar a história atual
7. identificar bloqueios
8. determinar o próximo prompt
9. determinar a próxima ação

Sem esse levantamento não há como saber qual ação é legítima. Se os arquivos não
existirem, dizer isso explicitamente em vez de assumir um estado.

## Status oficiais

Os únicos status válidos são:

```text
planejada · rascunho · pronta para aprovação · aprovada · em desenvolvimento
pronta para homologação · homologada · implementada · cancelada
```

| Status | Significado |
|---|---|
| planejada | existe no backlog, ainda não detalhada |
| rascunho | sendo escrita/revisada, ou com pendência de definição |
| pronta para aprovação | clara o suficiente para decisão humana |
| aprovada | aprovada explicitamente pelo usuário |
| em desenvolvimento | implementação iniciada em DEV |
| pronta para homologação | implementação e validações de DEV concluídas |
| homologada | validada em HOM |
| implementada | entregue e validada em PROD |
| cancelada | não será executada, permanece no histórico |

Fluxo oficial, sem atalhos:

```text
planejada → rascunho → pronta para aprovação
→ [APROVAÇÃO HUMANA] → aprovada → em desenvolvimento
→ pronta para homologação → homologada
→ [APROVAÇÃO HUMANA PARA PRODUÇÃO] → implementada
```

Cancelamento pode ocorrer a partir de planejada, rascunho, pronta para aprovação
ou aprovada.

## Os dois gates humanos

Nenhum dos dois pode ser inferido de entusiasmo, pressa ou silêncio. É preciso
confirmação explícita, do tipo `Aprovo H-017.` ou `Pode publicar em produção.`

```text
Gate 1: pronta para aprovação → aprovada
Gate 2: homologada → PROD → implementada
```

Se o usuário pedir implementação de história que não passou pelo gate 1, não
implementar: informar o status atual e oferecer executar P-02 para deixá-la
pronta para aprovação.

## Seleção do próximo prompt

A trilha oficial tem seis prompts:

```text
P-01 Gerenciar Backlog e Cronograma
P-02 Escrever e Revisar História
P-03 Atualizar Documentação DAH
P-04 Definir e Atualizar Interface
P-05 Implementar e Validar História
P-06 Homologar e Publicar
```

O próximo prompt é função do status da história ativa:

| Status atual | Próximo passo |
|---|---|
| planejada | P-02 |
| rascunho | P-02 |
| pronta para aprovação | aguardar aprovação humana |
| aprovada | P-03 → P-04 (se houver frontend) → P-05 |
| em desenvolvimento | P-05 |
| pronta para homologação | P-06 |
| homologada | P-06 (gate + publicação) |
| implementada | próxima história / P-01 |
| cancelada | nenhuma implementação |

Detalhes de escopo e fluxo interno de cada prompt, e qual skill técnica cada um
aciona: ler `references/prompts.md`.

## Documentos oficiais

```text
docs/
├── historias/{indice.md, H-xxx.md}
├── regras-de-negocio.md      ├── mapa-de-testes.md
├── modelo-de-dados.md        ├── mapa-de-decisoes.md
├── contratos-de-api.md       ├── diario-de-bordo.md
├── mapa-de-fluxos.md         └── cronograma.md
├── mapa-de-telas.md
└── guia-visual.md
```

Antes de criar qualquer arquivo documental novo, perguntar: *essa informação cabe
em um documento oficial existente?* Se cabe, atualizar o existente. Documentação
paralela é a principal fonte de divergência num projeto DAH.

`docs/historias/indice.md` é o backlog oficial e nunca pode divergir dos arquivos
de história. Colunas: Código, Título, Capítulo, Versão, Status.

Numeração global e permanente: `H-001`, `H-002`, ... Nunca reutilizar código,
nunca renumerar, história cancelada mantém o código, capítulo não interfere na
numeração.

Função de cada documento, capítulos e formato do índice: `references/documentos.md`.

## Portões de qualidade

Não marcar um status novo sem verificar a lista correspondente em
`references/checklists.md`:

- Definition of Ready para aprovação (antes de "pronta para aprovação")
- Definition of Ready para implementação (antes de P-05)
- Definition of Done DEV (antes de "pronta para homologação")
- Definition of Done HOM (antes de "homologada")
- Definition of Done PROD (antes de "implementada")

Itens não aplicáveis podem ser marcados como tal — mas isso é uma decisão
consciente que se declara, não um item que se ignora.

## Conflitos e ambiguidade

Ao detectar contradição (história × regra, história × API, índice × arquivo,
código × documentação, decisão × implementação):

```text
detectar → não escolher silenciosamente → identificar fontes
→ registrar decisão quando necessário → perguntar
→ atualizar documentos → continuar
```

Se o código contradiz a documentação, não presumir que o código está certo.
Analisar história aprovada, decisão vigente, documentos e testes, e corrigir o
elemento que estiver errado.

Decisões que afetam várias histórias, arquitetura, tecnologia, persistência,
segurança ou contratos vão para `docs/mapa-de-decisoes.md` como `D-xxx`.
Decisão anterior nunca é apagada — é marcada como substituída.
Ver `references/decisoes-e-diario.md`.

## Mudança de escopo durante a implementação

Se a implementação revelar mudança funcional, não alterar a história
silenciosamente:

```text
história → rascunho → incrementar versão → P-02 → aprovação humana
→ P-03 → P-04 se necessário → P-05 continua
```

Se surgir comportamento novo e independente, não absorver: criar item novo via
P-01. Nova versão = mesmo objetivo com refinamento. Nova história = novo
comportamento, fluxo, capacidade ou valor.

## Informação sensível

Nunca registrar valores reais de senha, token, API key, private key ou secret nos
documentos. Registrar a existência, não o valor:
`RESEND_API_KEY será configurada como secret`.

## Simplicidade

Registrar somente o que ajuda a planejar, decidir, implementar, validar,
homologar, operar ou retomar. Não criar estrutura antecipadamente. A governança
existe para reduzir retrabalho, não para produzir burocracia.

## Relatório de governança

Quando o usuário pedir um panorama ("como está o projeto?", "status geral"),
responder cobrindo: contagem do backlog por status; capacidade configurada,
média real observada e previsão; bloqueios com motivo; decisões pendentes;
história atual; próximo prompt. Formato completo em `references/auditoria.md`.

## Arquivos de referência

Ler sob demanda, conforme a tarefa:

| Arquivo | Ler quando |
|---|---|
| `references/prompts.md` | executar ou escolher entre P-01..P-06; saber qual skill técnica acionar; ambientes DEV/HOM/PROD e gate de produção |
| `references/checklists.md` | mudar status de uma história; verificar DoR/DoD |
| `references/documentos.md` | criar/atualizar qualquer documento em `docs/`; índice, capítulos, regras de negócio, modelo de dados, API, fluxos, telas, guia visual |
| `references/cronograma.md` | mexer em cronograma, capacidade, previsão, dependências, ordem ou bloqueios |
| `references/testes.md` | criar ou atualizar mapa de testes, definir T-xxx, decidir se um teste bloqueia a história |
| `references/decisoes-e-diario.md` | registrar decisão D-xxx, escrever no diário de bordo, resolver conflito documental |
| `references/auditoria.md` | auditar consistência, produzir relatório de governança, retomar projeto, verificar saúde da governança |

## Resultado esperado

Ao usar esta skill deve ser possível responder rapidamente: qual é o estado geral
do projeto, qual história está ativa e em que status, qual prompt executar agora,
qual história vem depois, o que está bloqueado, qual decisão está pendente, se o
cronograma está atualizado, quais testes ainda bloqueiam, se o sistema está
pronto para HOM ou PROD, se os documentos refletem o código, e se outro agente
conseguiria retomar o trabalho sem perder contexto.
