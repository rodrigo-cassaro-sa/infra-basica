# PA-02 — Escrever História Provisória a partir do Artefato de IA

## Tipo

```text
PROMPT AVULSO
```

Trabalha depois do **PA-01 — Analisar Artefato de IA e Gerar Índice Proposto**.

```text
PA-01: ARTEFATO → ÍNDICE
PA-02: ÍNDICE + ARTEFATO → HISTÓRIA A-xxx
```

---

# Comando

```text
PA-02 A-001
```

Escreve **uma** história por execução.

Lote só com pedido explícito:

```text
PA-02 A-001..A-005
```

Mesmo em lote, cada história é independente e passa por todas as checagens abaixo.

---

# 1. Entradas

Obrigatórias:

```text
analise-artefato/indice-proposto.md
analise-artefato/inventario.md
ARTEFATO ORIGINAL
```

Se existirem:

```text
analise-artefato/comparacao-dah.md
AGENTS.md
docs/historias/indice.md
docs/regras-de-negocio.md
docs/mapa-de-decisoes.md
docs/modelo-de-dados.md
docs/contratos-de-api.md
docs/mapa-de-fluxos.md
docs/mapa-de-telas.md
```

---

# 2. Pré-checagem (parar se falhar)

| Situação | Ação |
|---|---|
| A-xxx não existe no índice | Não inventar código. Responder: "A-xxx não existe. Executar PA-01 em modo atualização." Parar. |
| Status `removida` | Informar e parar. |
| Status `dividida` | Informar os códigos substitutos e parar. |
| Status `escrita` | Só reescrever se o usuário pedir explicitamente. |
| Artefato inacessível | Pedir o artefato e parar. |

---

# 3. Localizar evidências

O título do índice é apenas um guia. **A evidência vem do artefato.**

Ordem de busca:

1. Caminhos da coluna "Evidência" do índice.
2. Entradas relacionadas no `inventario.md`.
3. Busca no artefato por: telas, componentes, rotas, handlers, funções, models, endpoints, botões, formulários, estados, textos, navegação, dados, integrações.

Toda evidência deve ser registrada como `caminho/arquivo.ext:linhas` ou `Tela X (print n)`.

---

# 4. Checagem de escopo (antes de escrever)

## 4.1 Não é história funcional

Exemplos: configurar Axios, criar Context, criar componente Card.

```text
→ NÃO escrever a história
→ atualizar status no índice: não funcional
→ Observação: motivo em 1 linha
→ recomendar remoção na resposta
```

## 4.2 Grande demais

Quando cobre mais de um objetivo ou resultado observável (ex.: "Gerenciar usuários").

```text
→ NÃO escrever a história
→ atualizar status no índice: dividir
→ Observação: divisão sugerida (ex.: Criar / Visualizar / Editar / Bloquear)
→ instruir: executar PA-01 em modo atualização
```

O PA-02 **não cria novos códigos A-xxx**. Isso é responsabilidade do PA-01.

## 4.3 Sem evidência

Quando não há nada no artefato que sustente o item:

```text
→ NÃO escrever a história
→ atualizar status no índice: sem evidência
→ recomendar remoção ou revisão no PA-01
```

---

# 5. Regras de escrita

- **Descrever o comportamento observado**, sem defender o código. Código de IA pode estar incompleto, ser só visual, ter mock, bug ou comportamento inventado.
- **Não adicionar etapas** que não existem, mesmo que sejam boas práticas.
- **Não inventar motivo de negócio.** O contexto é só o que o artefato permite concluir.
- **Ator** só com evidência. Sem evidência, usar: `Ator não determinado pelo artefato.`
- **Dados:** registrar nomes e campos observados. Não definir tipo de banco sem evidência.
- **Regras e validações:** sempre "aparentes" enquanto não houver documentação oficial.

## 5.1 Marcadores obrigatórios

Todo item das seções de conteúdo recebe um marcador:

```text
[E] Evidência   → existe no artefato (com local)
[I] Inferência  → dedução do agente
[M] Mock        → existe, mas simulado / hardcoded / sem implementação real
```

Exemplo:

```text
- [E] Rota /admin/users (`src/router.tsx:22`)
- [I] Provavelmente exclusiva de administradores
```

Nunca transformar `[I]` em regra definitiva.

---

# 6. Arquivo de saída

```text
analise-artefato/historias/A-001-criar-usuario.md
```

Nome: código + slug do título em minúsculas, sem acento, com hífens.

---

# 7. Modelo da história provisória

Remover seções sem informação relevante, exceto **Identificação**, **Evidências**, **Fluxo observado**, **Dúvidas** e **Observação para futura história DAH**, que são sempre obrigatórias.

```markdown
# A-xxx — Título

## Identificação

**Código de análise:** A-xxx
**Capítulo proposto:** ...
**Origem:** artefato de IA (ferramenta, se conhecida)
**Nível de evidência:** COMPROVADA / VISUAL / MOCK / INFERIDA
**Relação DAH:** NOVA / EQUIVALENTE / PARCIAL / MAIS AMPLA / CONFLITANTE
**Status:** provisória — não é história DAH oficial

## Evidências no artefato

- `caminho/arquivo:linhas` — o que foi encontrado
- ...

## Contexto aparente

...

## Objetivo aparente

Permitir que [ator] [ação] para [resultado observável].

## Atores aparentes

- [E]/[I] ...

## Pré-condições aparentes

- ...

## Gatilho

...

## Fluxo observado

1. [E] ...
2. [E] ...
3. [M] ...

## Fluxos alternativos observados

- ...

## Exceções observadas

- ...

## Regras aparentes

- ...

## Validações aparentes

- ...

## Permissões

- Comprovadas: ...
- Inferidas: ...

## Dados envolvidos

| Campo | Onde aparece | Observação |
|---|---|---|

## Integrações aparentes

- ...

## Estados da interface

| Estado | Existe? | Evidência |
|---|---|---|
| carregando | sim/não | ... |
| vazio | sim/não | ... |
| sucesso | sim/não | ... |
| erro | sim/não | ... |

## Resultado observado

...

## Critérios observáveis

- [ ] ...
- [ ] ...

(Baseados só no artefato. Não são critérios oficiais da DAH.)

## Mocks e simulações

- API mockada / dados estáticos / resposta simulada / gráfico fictício / botão sem implementação

## Inferências

- ...

## Dúvidas

- ...

## Comparação com DAH existente

**História relacionada:** nenhuma / H-xxx

| Aspecto | Detalhe |
|---|---|
| Coincide | ... |
| Falta no artefato | ... |
| Sobra no artefato | ... |
| Contradiz | ... |

## Pontos de conflito

- CONFLITO: H-xxx diz ...; artefato faz ... → decisão humana necessária

## Observação para futura história DAH

O que o P-02 oficial deve aproveitar, descartar ou confirmar.
```

---

# 8. Comparação e conflito

- Se houver H-xxx relacionada, comparar o que coincide, o que falta, o que sobra e o que contradiz.
- **Nunca alterar H-xxx** nem qualquer arquivo em `docs/`.
- Em contradição, registrar `CONFLITO` e **não assumir que o artefato está certo**.
- Se a classificação de relação mudar em relação ao `comparacao-dah.md`, registrar na resposta e na Observação do índice. Não editar `comparacao-dah.md`.

---

# 9. Dúvidas

Informação importante ausente vai para **Dúvidas**, e a história continua sendo escrita.

Interromper **somente** quando a ambiguidade impedir saber qual comportamento está sendo analisado. Nesse caso, fazer uma pergunta objetiva com opções.

---

# 10. Atualizar o índice

Depois de escrever, ou depois de uma decisão da checagem de escopo, atualizar em `indice-proposto.md` **somente**:

```text
coluna Status
coluna Observação (link para o arquivo ou motivo)
```

Não alterar códigos, títulos, capítulos nem a ordem. Sugestões de mudança de título vão na Observação.

---

# 11. Proibições

```text
não gerar H-xxx
não criar novos códigos A-xxx
não alterar docs/ ou backlog oficial
não copiar valores de secrets
não tratar [I] ou [M] como requisito
não escrever história artificial para item técnico
não colocar A-xxx no cronograma
```

---

# 12. Resposta no chat

```text
PA-02 A-xxx — Título

Resultado: escrita / não funcional / dividir / sem evidência
Arquivo: analise-artefato/historias/A-xxx-slug.md
Nível de evidência: ...
Relação DAH: ...
Mocks: x itens
Conflitos: x
Dúvidas principais:
1. ...

Próxima ação: PA-02 A-yyy
(ou: PA-01 modo atualização, se houver itens para dividir ou remover)
```

---

# 13. Depois de todas as histórias

Estrutura esperada:

```text
analise-artefato/
├── inventario.md
├── resumo.md
├── indice-proposto.md
├── comparacao-dah.md
└── historias/
    ├── A-001-....md
    ├── A-002-....md
    └── ...
```

Revisão humana decide o que entra, o que sai, o que é duplicado, o que está errado e o que deve mudar.

Promoção:

```text
A-xxx aceitas → P-01 → H-xxx no indice.md → P-02 oficial → aprovação humana
```

Quando `A-006 → H-031`, o P-02 oficial usa como fontes: H-031 no índice + A-006 + artefato original + documentação DAH.

```text
A-xxx ≠ H-xxx automaticamente
```

A história provisória contém inferências, dúvidas, mocks e comportamentos que podem ser rejeitados. O P-02 oficial deve normalizar, nunca copiar.

---

# Regra final

```text
PA-02 PEGA UM ITEM DO ÍNDICE,
VOLTA AO ARTEFATO
E ESCREVE A HISTÓRIA COM EVIDÊNCIAS RASTREÁVEIS.

EVIDÊNCIA [E] ≠ INFERÊNCIA [I] ≠ MOCK [M]

SE NÃO É FUNCIONAL, É GRANDE DEMAIS OU NÃO TEM EVIDÊNCIA:
NÃO ESCREVE — MARCA NO ÍNDICE E DEVOLVE AO PA-01.

SÓ DEPOIS DA REVISÃO HUMANA:
P-01 / P-02 OFICIAIS.
```
