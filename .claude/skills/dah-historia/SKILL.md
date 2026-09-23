---
name: dah-historia
description: >-
  Criar, revisar, versionar e indexar Histórias DAH (H-XXX), a unidade de especificação
  funcional de todo projeto da casa — independente de stack, frontend e backend desacoplados.
  Use ao escrever uma História nova, alterar uma existente, checar se uma História está bem
  formada, sincronizar docs/historias/indice.md, ou quando o usuário descrever uma
  funcionalidade que precise virar especificação. Gatilhos típicos: "criar história", "nova
  H-", "revisar a H-0XX", "atualizar o índice", "isso aqui vira história?", "especificar
  uma funcionalidade".
---

# DAH — Especificar Histórias

A História é a unidade de intenção funcional do projeto. Ela descreve **o que o sistema deve fazer**, nunca como implementar.

Todo projeto da casa é **desacoplado** (app Expo + backend separados, conversando por contrato). A História descreve o **produto inteiro**, sem dizer se algo acontece no app, no backend ou num serviço: `Sistema` é o produto. Quem decide onde cada parte roda são os documentos derivados e as skills de stack.

Tudo o mais é derivado dela: `regras-de-negocio.md`, `modelo-de-dados.md`, `mapa-de-fluxos.md`, `mapa-de-telas.md`, `contratos-de-api.md` (skill `dah-documentacao`), `guia-visual.md` (skill `ux-ui`) e depois o código (`expo-app` e backend). Escreva a intenção uma vez; derive o resto.

```text
dah-historia → dah-documentacao → ux-ui (guia visual) → expo-app (front) + backend
```

## Os 12 campos — exatamente estes, nesta ordem

| # | Campo | Regra curta |
|---|---|---|
| 1 | Nome | Comportamento ou resultado observável. `Criar novo usuário`, não `Criar tabela usuário` |
| 2 | Código | `H-000`, sequencial, imutável, jamais reutilizado |
| 3 | Status | Só: `rascunho`, `aprovada`, `implementada`, `cancelada` |
| 4 | Versão | Inteiro desde `1`; incrementa a cada mudança funcional |
| 5 | Capítulo | Área funcional; subdivisão com ` / ` é válida |
| 6 | Contexto | Estado inicial e intenção que iniciam o fluxo |
| 7 | Local | Onde a interação ocorre, em termos funcionais |
| 8 | Atores | `Ator 1`, `Ator 2`… consistentes em toda a História |
| 9 | O que acontece | Fluxo principal de sucesso, passos numerados, em ordem real |
| 10 | O que não pode acontecer | Restrições objetivas e verificáveis |
| 11 | Resultados possíveis | Um `Sucesso` + as `Falha N` relevantes, todos verificáveis |
| 12 | Histórias relacionadas | Códigos existentes; a primeira é a continuação natural |

**Nenhum campo a mais.** Estimativa, custo, prioridade, complexidade, tokens, endpoint, tabela, framework, arquivo e plano técnico são derivados depois e não pertencem à História.

O template literal e exemplos bons/ruins de cada campo estão em [references/template-e-exemplos.md](references/template-e-exemplos.md). Leia antes de escrever a primeira História de uma sessão.

## Convenções do projeto

Antes de escrever, leia **`docs/produto.md`** (template em `assets/templates/docs/produto.md`):
capítulos em uso, papéis de ator, vocabulário oficial e convenção do índice. Não existe?
Crie a partir do template com o que já se sabe e pergunte o resto.

Padrão da casa para projeto novo:

- Pasta: `docs/historias/`.
- Arquivo: `H-001-criar-novo-usuario.md` — código, hífen, título em minúsculas, sem acento
  nem espaço (funciona em qualquer terminal, CI e URL). O título completo com acento fica
  dentro do arquivo.
- Índice: `docs/historias/indice.md`, tabela única, colunas `Código | Título | Capítulo | Release | Status`.
  `Release` guarda o escopo (`MVP`, `V1`); o número da Versão fica só dentro do arquivo.
- O índice também é o backlog: linha sem Código = História planejada e ainda não escrita.
- `Status` sempre no feminino (`aprovada`), concordando com "História".

**Projeto existente com outra convenção** (ex.: `Historias/H-001 Criar novo Usuário.md`):
siga a que está em uso e não migre sem pedido.

```bash
ls docs/historias/H-*.md | sort | tail -1          # último Código usado
grep -n "<termo do título>" docs/historias/indice.md  # já existe linha no backlog?
```

## Ao criar uma História

1. Identifique o comportamento central, o Capítulo, o Contexto e o Local.
2. Liste todos os Atores diretamente envolvidos.
3. Escreva o fluxo em ordem real — **validações antes das mudanças de estado que dependem delas**.
4. Registre restrições objetivas e separe cada Falha com comportamento próprio.
5. Relacione com Histórias existentes; nunca invente código inexistente.
6. Pegue o próximo Código disponível.
7. Crie como `rascunho`, salvo instrução explícita em contrário.
8. **Preencha a linha já existente no índice** quando houver — só acrescente linha nova se não existir.

Entregue sempre: o arquivo, o índice atualizado, as lacunas detectadas e as Histórias necessárias ainda não criadas (marcadas como sugestão, nunca como aprovadas).

## Ao revisar uma História

Preserve o Código. Altere só o necessário. Incremente a Versão quando houver mudança funcional — correção ortográfica que não muda sentido não conta. Atualize `Histórias relacionadas` e o índice. Verifique se a alteração revelou novos caminhos de falha ou novas Histórias necessárias.

**História `aprovada` ou `implementada` já foi usada para derivar documentos e código.** Mudança funcional nela exige incremento de Versão *e* revisão dos derivados afetados (skill `dah-documentacao`, guia visual, contrato e código) — avise o usuário quando sua alteração disparar isso.

## Granularidade

Quebre a História quando ela tiver objetivos independentes, atores com metas distintas, fluxos implementáveis em separado, mais de um resultado de sucesso independente, ou quando você não conseguir explicar o objetivo central em uma frase.

Falha e caminho alternativo **não** obrigam a criar outra História. Crie outra quando o caminho alternativo tiver fluxo próprio e reutilizável — `Criar usuário` pode oferecer recuperação de senha quando o e-mail já existir, mas `Recuperar senha` continua sendo História à parte.

Não crie História para tarefa técnica: criar tabela, instalar biblioteca, configurar servidor ou pipeline, criar endpoint isolado, refatorar, mexer em CSS sem necessidade funcional.

## A regra que mais se viola

**Não invente regra de negócio para preencher lacuna.** Quando uma decisão funcional necessária ainda não foi tomada, escreva a História só com o que está definido e registre a lacuna separadamente, fora dela.

O mesmo vale para termo subjetivo sem definição no projeto — `senha forte`, `valor adequado`, `prazo razoável`, `quantidade excessiva`. Ou o projeto já definiu objetivamente, e você escreve a definição, ou vira lacuna.

## Validação antes de salvar

- 12 campos presentes, Código no formato, Status entre os quatro válidos, Versão coerente
- Contexto (estado inicial) separado de Local (onde ocorre)
- Identificadores de ator consistentes do começo ao fim
- Fluxo em ordem real; validações precedem as mudanças de estado
- Restrições objetivas e verificáveis; nenhum termo subjetivo indefinido
- Sucesso verificável; cada Falha relevante com resultado observável e separada quando o comportamento difere
- Comportamento, não tarefa técnica; sem detalhe de implementação
- Um só objetivo funcional; compreensível isoladamente
- Todos os códigos em `Histórias relacionadas` existem; a primeira é a continuação natural quando aplicável
- Índice atualizado na mesma entrega
- Nenhuma regra que o implementador precisaria inventar

## Nunca

Adicionar campo fora dos 12 · mudar o Código de uma História existente · reutilizar Código cancelado · tratar a ordem numérica como ordem do fluxo · alterar Status ou Versão sem refletir no índice · alterar comportamento aprovado sem incrementar Versão · criar relação com código inexistente · esconder falha relevante dentro do fluxo de sucesso · inventar comportamento para fechar lacuna.

## Documentos não derivados

`docs/produto.md` (visão, capítulos, papéis, vocabulário) e os documentos de stack
(`docs/stack.md` do app, e o equivalente do backend) não são Histórias nem derivados delas.
A DAH descreve o sistema; a stack o implementa. Coexistem sem se substituir.
