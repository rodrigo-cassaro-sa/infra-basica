---
name: dah-documentacao
description: >-
  Derivar e manter a documentação estrutural do projeto a partir das Histórias DAH — regras-
  de-negocio.md, modelo-de-dados.md, mapa-de-fluxos.md, mapa-de-telas.md e contratos-de-api.md
  (o contrato que desacopla app Expo e backend). Use quando pedirem para gerar, atualizar ou
  revisar a documentação/documentacao, derivar regras de negócio, modelar dados, mapear telas
  ou fluxos, especificar contratos de API, ou propagar o impacto de uma História nova ou
  alterada. Gatilhos: "gerar a documentação", "derivar as regras", "modelo de dados", "mapa de
  telas", "contratos de API", "o que a H-0XX impacta".
---

# DAH — Derivar documentação estrutural

As Histórias são a fonte de intenção. Estes documentos são a **memória consolidada do sistema** — eles representam o sistema que emerge do conjunto, não um bloco por História.

```
Histórias → análise → impacto → o que já existe → criar/alterar/reutilizar → documentação
```

## Artefatos

Gerar ou atualizar em `docs/` (projeto existente com outra pasta, ex. `documentacao/`: siga a em uso):

| Arquivo | Prefixo | Conteúdo |
|---|---|---|
| `regras-de-negocio.md` | `RN-` | Regras permanentes e reutilizáveis do domínio |
| `modelo-de-dados.md` | `ENT-` | Entidades, atributos, relações, restrições lógicas |
| `mapa-de-fluxos.md` | `FL-` | Sequências que atravessam ações, decisões, telas, serviços |
| `mapa-de-telas.md` | `T-` | Telas, campos, ações, estados, navegação |
| `contratos-de-api.md` | `API-` | Método, recurso, entrada, saída, erros |

`guia-visual.md` (`GV-*`) é derivado das Histórias pela skill `ux-ui` (`references/guia-a-partir-de-historias.md`), não por esta. Aqui, identifique necessidades visuais (formulário, tabela, modal, confirmação, estado vazio) mas **não** defina cor, tipografia, espaçamento, raio, sombra ou dimensão — `mapa-de-telas.md` apenas referencia os componentes `GV-CMP-*` quando eles existirem.

Os formatos completos de cada documento estão em [references/formatos-dos-documentos.md](references/formatos-dos-documentos.md). Leia antes de criar o primeiro elemento de cada tipo. O cabeçalho de convenções do contrato (erro, paginação, autenticação) está pronto em `assets/templates/docs/contratos-de-api.md`.

Antes de derivar, leia `docs/produto.md` (capítulos, papéis, vocabulário, arquitetura).

## Projetos desacoplados

Todo projeto da casa tem app (Expo) e backend separados. Estes documentos são a **fronteira
entre eles**:

| Documento | Frontend (`expo-app`) usa para | Backend usa para |
|---|---|---|
| `contratos-de-api.md` | schemas Zod, services, mocks enquanto o backend não existe | rotas, validação, respostas e códigos de erro |
| `regras-de-negocio.md` | UX (desabilitar, avisar antes) + teste citando o RN | autoridade: valida e recusa |
| `modelo-de-dados.md` | tipos do modelo e mappers | tabelas e migrações |
| `mapa-de-telas.md` | telas, estados, `docs/rotas.md` | — |
| `mapa-de-fluxos.md` | navegação entre telas | orquestração entre operações |

Regras:
- **Docs moram em um lugar só**, lido pelos dois lados: pasta `docs/` na raiz do monorepo
  (`app/`, `api/`, `docs/`) — padrão da casa — ou repositório próprio de especificação quando
  front e back ficam em repositórios separados. Nunca copie os docs para dois repositórios.
- **Contrato muda primeiro.** Mudou `contratos-de-api.md`? Front e back se ajustam a ele,
  nunca o contrário. Divergência entre implementação e contrato é `CONFLITO`.
- Regra de negócio vale no backend **sempre**; o app só antecipa para a UX.

## De onde vem cada coisa

As Histórias DAH têm **exatamente 12 campos**. Não procure `objetivo`, `pré-condições`, `gatilho`, `fluxos alternativos`, `exceções`, `dados utilizados`, `regras` ou `permissões` — esses campos não existem e são proibidos pelo método. Derive assim:

| Campo da História | Alimenta |
|---|---|
| Código, Versão | Rastreabilidade em todos os artefatos |
| Status | Governa se pode alterar documentação oficial (ver abaixo) |
| Capítulo | Agrupamento de telas e módulos |
| Contexto | Pré-condição do fluxo; estado inicial da tela |
| **Local** | **`mapa-de-telas.md`** — é o campo que identifica a tela (T-) |
| Atores | Atores da tela; autenticação e autorização do contrato |
| O que acontece | `mapa-de-fluxos.md` (passos), `contratos-de-api.md` (operações), `modelo-de-dados.md` (entidades e atributos citados) |
| O que não pode acontecer | `regras-de-negocio.md` (RN), restrições do modelo, códigos de erro do contrato |
| Resultados possíveis | Estados finais do fluxo, estados da tela, respostas de sucesso e erro da API |
| **Histórias relacionadas** | **`mapa-de-fluxos.md`** — o encadeamento entre Histórias é o que define o fluxo; a primeira relação é a continuação natural |

`Local` e `Histórias relacionadas` são os dois campos mais fáceis de esquecer e os que mais carregam informação estrutural.

## Processo

1. **Ler as Histórias.** Todos os `.md` de `docs/historias/`. Ignore `indice.md`, README, temporários, backups e Histórias com Status `cancelada`.
2. **Ler os documentos existentes por inteiro** antes de escrever qualquer coisa.
3. **Classificar cada necessidade**: `REUTILIZAR` · `ALTERAR` · `CRIAR` · `REMOVER` · `SEM IMPACTO`. Prefira sempre reutilizar.
4. **Aplicar** na ordem: regras → dados → fluxos → telas → API. Essa ordem evita decisão prematura de interface ou tecnologia.

Monte internamente uma matriz de impacto por História — não precisa persistir em arquivo:

| Artefato | Impacto | Elemento |
|---|---|---|
| Regra | criar | RN-021 |
| Tela | reutilizar | T-017 |
| Fluxo | alterar | FL-009 |
| Dados | alterar | ENT-008 |
| API | criar | API-014 |

## Regra principal

> Não documentar Histórias isoladamente. Documentar o sistema que emerge do conjunto.

Antes de criar qualquer elemento: **procurar → comparar → reutilizar se possível → alterar se necessário → criar só quando realmente novo.** A comparação é por significado, não por igualdade textual.

Duplicidade semântica é o erro mais caro:

```
RN-014 — Email deve ser único
RN-038 — Não permitir email duplicado      ← errado, é a mesma regra
RN-071 — Usuário não pode repetir email
```

Vale igualmente para telas: uma História **não** significa uma tela nova. `Visualizar usuário`, `Editar usuário` e `Bloquear usuário` podem ser a mesma tela. E para fluxos: não crie FL para operação simples sem sequência significativa.

## Rastreabilidade

Todo elemento lista as Histórias que o originaram ou o utilizam, e a relação é bidirecional. Uma História gera vários elementos; um elemento serve a várias Histórias.

```
H-041
├── RN-021
├── T-018
├── FL-012
├── ENT-009
└── API-014
```

Identificadores nunca são renumerados nem reutilizados. Elemento novo recebe o próximo número livre.

## Não inventar

**Informação ausente vira `PENDENTE_DE_DEFINICAO`**, nunca suposição:

```md
### Paginação

PENDENTE_DE_DEFINICAO
```

**Requisitos incompatíveis viram `CONFLITO`**, com as Histórias envolvidas nomeadas. Não escolha um lado silenciosamente:

```
CONFLITO

H-021: Usuário pode alterar CPF.
H-044: CPF não pode ser alterado após cadastro.
```

## Status das Histórias

| Status | Efeito na documentação |
|---|---|
| `aprovada` | Pode alterar documentação oficial |
| `implementada` | Deve estar refletida na documentação |
| `rascunho` | Pode ser analisada; o que dela vier é provisório e deve ser marcado como tal |
| `cancelada` | Não gera elemento novo; o que já originou deve ser checado quanto a uso por outras Histórias |

Não existe outro status.

## Incrementalidade

A skill roda repetidamente. Com documentação já consolidada, **não regenere do zero** — incorpore apenas os impactos necessários. Nunca sobrescreva documento existente às cegas.

Não remova elemento só porque nenhuma História nova o mencionou. Remova apenas com evidência explícita de que o comportamento deixou de existir.

## Independência tecnológica

Os documentos descrevem o sistema; a stack o implementa. Nada de Django, Flutter, React, Vue, PHP, PostgreSQL, MySQL, Supabase, Firebase, n8n ou NocoDB.

No modelo de dados, use tipos lógicos — `texto`, `inteiro`, `decimal`, `booleano`, `data`, `hora`, `data/hora`, `enum`, `identificador`, `arquivo`, `lista`, `objeto` — e não `VARCHAR(255)`, `BIGINT`, `JSONB`, `UUID` ou `TIMESTAMPTZ`.

## Vocabulário

Antes de nomear, verifique o que já existe e o vocabulário oficial em `docs/produto.md`. Se o sistema usa `Usuário`, não apareça depois com `Conta`, `Pessoa de acesso` ou `Login` para a mesma entidade. Termo novo do domínio entra primeiro no `docs/produto.md`.

Ordem de precedência na interpretação: História aprovada mais recente → regras consolidadas → documentos estruturais existentes → História em rascunho. Em conflito entre documentos, registre; não sobrescreva em silêncio.

## Validação final

- **Regras:** duplicadas? contraditórias? todas com Histórias relacionadas?
- **Dados:** entidades duplicadas? atributos com nomes divergentes? relacionamentos inconsistentes? restrições batem com as regras?
- **Fluxos:** fluxos equivalentes? decisões coerentes? telas referenciadas existem?
- **Telas:** duplicadas? alguma ação poderia reutilizar tela existente? navegação coerente?
- **APIs:** endpoints duplicados? nomes de recurso consistentes? entradas batem com o modelo? erros batem com as regras e usam o envelope padrão? toda operação de escrita prevê 422 com `fieldErrors`? listas definem paginação? autenticação e autorização coerentes?
