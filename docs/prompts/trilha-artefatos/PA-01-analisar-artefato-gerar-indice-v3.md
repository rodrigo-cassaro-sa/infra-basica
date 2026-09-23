# PA-01 — Analisar Artefato de IA e Gerar Índice Proposto

## Tipo

```text
PROMPT AVULSO
```

Fora da sequência obrigatória `P-01 → P-02 → P-03 → P-04 → P-05 → P-06`.

Usado quando existe um artefato produzido por IA (ChatGPT, Claude, Gemini, Copilot, Lovable, Bolt, v0 ou outra ferramenta).

---

# Posição no fluxo

```text
ARTEFATO IA
   ↓
PA-01  → inventário + índice proposto + comparação DAH + resumo
   ↓
REVISÃO HUMANA DO ÍNDICE
   ↓
PA-02 A-001, PA-02 A-002 ... → histórias provisórias (uma por vez)
   ↓
REVISÃO HUMANA DAS HISTÓRIAS
   ↓
P-01 → H-xxx oficiais
   ↓
P-02 oficial
   ↓
PA-03 → normalização técnica do código (somente do que foi aprovado)
```

---

# Regra principal

```text
ARTEFATO DE IA ≠ FONTE DE VERDADE DO PROJETO
```

O artefato é matéria-prima, protótipo, fonte de descoberta e implementação candidata.

Histórias aprovadas e documentos DAH continuam sendo a fonte oficial.

---

# Escopo

**O PA-01 FAZ:**

- inventário do artefato
- classificação do artefato
- identificação de capacidades de negócio
- capítulos propostos
- índice proposto com códigos A-xxx
- comparação com a DAH existente
- resumo da análise
- perguntas que afetam o índice

**O PA-01 NÃO FAZ:**

- escrever histórias provisórias (isso é o PA-02)
- gerar códigos H-xxx (isso é o P-01)
- alterar qualquer arquivo em `docs/`
- normalizar, copiar ou importar código (isso é o PA-03)
- instalar dependências ou executar o artefato em produção

---

# 0. Entrada do artefato

Identificar e registrar a forma de entrada:

```text
repositório / pasta
arquivo .zip
código colado na conversa
prints / screenshots
link de preview (Lovable, Bolt, v0...)
conversa exportada
```

Regras:

- **Somente prints ou preview:** todo comportamento é no máximo `VISUAL`. Nenhum comportamento de backend pode ser marcado como comprovado.
- **Artefato inacessível, corrompido ou claramente incompleto:** parar e pedir ao usuário antes de continuar.
- Registrar a origem (ferramenta de IA), se conhecida.

---

# 1. Ler o projeto DAH existente

Se existirem, ler:

```text
AGENTS.md
docs/historias/indice.md
docs/mapa-de-decisoes.md
docs/regras-de-negocio.md
docs/modelo-de-dados.md
docs/contratos-de-api.md
docs/mapa-de-fluxos.md
docs/mapa-de-telas.md
docs/guia-visual.md
```

Se não existir documentação DAH:

```text
MODO PROJETO NOVO
→ toda capacidade será classificada como NOVA
→ comparacao-dah.md registra "sem DAH existente"
```

---

# 2. Inventário

Gerar `analise-artefato/inventario.md`.

O inventário é o mapa que o PA-02 usa para localizar evidências.

Levantar:

```text
linguagens e frameworks
estrutura de pastas
telas / páginas
rotas
componentes principais
models / entidades
endpoints / chamadas de API
estado global / contexts / stores
mocks e dados hardcoded
integrações externas
assets
configurações e variáveis de ambiente
testes existentes
dependências (package.json, requirements.txt, pyproject.toml)
```

Formato mínimo:

```markdown
# Inventário do Artefato

## Entrada
- Forma: ...
- Origem: ...

## Stack
- ...

## Telas / Rotas
| Rota / Tela | Arquivo | Observação |
|---|---|---|

## Entidades / Dados
| Entidade | Onde aparece | Campos observados |
|---|---|---|

## Endpoints / Chamadas
| Método + caminho | Arquivo | Real / Mock |
|---|---|---|

## Mocks e simulações
| O quê | Arquivo:linhas | Tipo (hardcoded, setTimeout, Promise.resolve, JSON local, usuário fictício) |
|---|---|---|

## Integrações externas
- ...

## Secrets encontrados
| Tipo | Arquivo:linha |
|---|---|
(NUNCA copiar o valor. Apenas apontar o local.)

## Cobertura da leitura
- Lido: ...
- Não lido / ignorado: ... (motivo)
```

**Artefato grande:** percorrer por pastas. Ignorar `node_modules`, `dist`, `build`, `.next`, caches e lockfiles (lockfiles só para dependências). Registrar em "Cobertura da leitura" o que ficou de fora.

---

# 3. Classificar o artefato

Uma ou mais categorias:

```text
A — protótipo visual
B — frontend funcional
C — backend funcional
D — API
E — modelo de dados
F — projeto completo
G — documentação
H — prova de conceito
I — código parcial
J — referência visual
```

---

# 4. Identificar capacidades

Reconstruir o sistema **na linguagem do negócio**, não na linguagem do código.

```text
Certo:  Criar usuário / Realizar login / Cancelar pedido
Errado: UserForm / AuthContext / useFetch / CustomerService
```

## 4.1 Critério de capacidade (candidata a história)

Um item só entra no índice se tiver:

```text
um ator (ou "ator não determinado")
um objetivo de negócio
um resultado observável
título no formato: verbo + objeto
```

## 4.2 O que NÃO entra no índice

```text
componente, hook, context, config, layout, estilo, utilitário
```

Esses itens são registrados em `resumo.md`, na seção "Itens técnicos / visuais", e não recebem código A-xxx.

## 4.3 Capacidade grande demais

Itens como "Gerenciar usuários" devem ser divididos já no índice:

```text
Criar usuário
Visualizar usuário
Editar usuário
Bloquear usuário
```

Criar somente as partes que têm evidência no artefato.

## 4.4 Nível de evidência

Cada capacidade recebe um nível:

```text
COMPROVADA → há código que executa o comportamento (handler + chamada/persistência real)
VISUAL     → tela/botão existe, sem lógica
MOCK       → lógica existe, mas sobre dados fixos ou resposta simulada
INFERIDA   → sugerida por um elemento (ex.: link "Esqueci minha senha") sem tela ou lógica
```

Na dúvida, usar o nível mais baixo.

---

# 5. Capítulos propostos

Agrupar capacidades em capítulos funcionais, como Credenciamento e acesso, Perfil, Cadastros, Pedidos, Financeiro, Relatórios ou Administração.

Capítulos do PA-01 são **PROPOSTOS**. Não entram no backlog oficial.

Se o projeto DAH já tiver capítulos, reutilizar os nomes existentes quando houver equivalência.

---

# 6. Índice proposto

Gerar `analise-artefato/indice-proposto.md`:

```markdown
# Índice Proposto — Artefato de IA

**Artefato:** ...
**Data da análise:** ...

| Código | Título | Capítulo | Evidência | Nível | Relação DAH | Status | Observação |
|---|---|---|---|---|---|---|---|
| A-001 | Criar usuário | Credenciamento e acesso | `src/pages/Signup.tsx:12-80` | COMPROVADA | NOVA | pendente | — |
| A-002 | Recuperar senha | Credenciamento e acesso | link em `Login.tsx:44` | INFERIDA | NOVA | pendente | sem tela |

## Histórico de alterações do índice

| Data | Alteração | Motivo |
|---|---|---|
```

## 6.1 Evidência

Sempre apontar local verificável:

```text
caminho/arquivo.ext:linhas
ou
Tela X (print n)
```

Nunca usar evidência vaga, como "tela de cadastro".

## 6.2 Status

```text
pendente       → aguardando PA-02
escrita        → história provisória criada pelo PA-02
não funcional  → PA-02 concluiu que não é comportamento de negócio
dividir        → PA-02 concluiu que é grande demais
dividida       → substituída por novos códigos (indicar quais)
removida       → excluída do escopo por decisão humana
sem evidência  → PA-02 não encontrou evidência suficiente
```

## 6.3 Ordem

Ordenar por capítulo e, dentro dele, pelo fluxo natural de uso (acesso antes do uso, criar antes de editar).

---

# 7. Regras dos códigos A-xxx

- `A` significa **ANÁLISE**.
- Sequenciais, com 3 dígitos: `A-001`, `A-002`...
- **Nunca reutilizar nem renumerar.**
- **Removida:** o código permanece na tabela com status `removida`.
- **Dividida:** o original recebe status `dividida → A-019, A-020`, e os novos códigos vão para o fim da sequência.
- **Nunca gerar H-xxx.** Só o P-01 cria códigos oficiais.
- Pode indicar correspondência com uma história existente (`A-003 → provável H-014`), mas nunca alterar a numeração oficial.

## 7.1 Re-execução (modo atualização)

Se `indice-proposto.md` já existir:

```text
MODO ATUALIZAÇÃO
→ preservar todos os códigos existentes
→ aplicar divisões/remoções marcadas pelo PA-02 ou pelo usuário
→ adicionar novos itens ao final
→ registrar no Histórico de alterações
```

---

# 8. Comparação com a DAH

Gerar `analise-artefato/comparacao-dah.md`.

Relações possíveis:

```text
NOVA        → não existe no backlog
EQUIVALENTE → corresponde a H-xxx
PARCIAL     → cobre só parte de H-xxx
MAIS AMPLA  → inclui comportamento além de H-xxx
CONFLITANTE → contradiz H-xxx ou regra de negócio
```

Formato:

```markdown
| A-xxx | H-xxx | Relação | Diferença principal (1 linha) | Ação sugerida |
|---|---|---|---|---|
| A-001 | H-001 | EQUIVALENTE | — | revisar no P-02 |
| A-003 | H-014 | CONFLITANTE | artefato permite excluir; H-014 proíbe | decisão humana |
```

Em modo projeto novo, registrar apenas: `Sem DAH existente — todas as capacidades classificadas como NOVA.`

Conflitos **não são resolvidos** pelo PA-01. Não assumir que o artefato está certo.

---

# 9. Resumo da análise

Gerar `analise-artefato/resumo.md` com:

```text
origem e forma de entrada
tipo do artefato (A–J)
stack original vs stack oficial
quantidade de telas, rotas e entidades
quantidade de capacidades por nível (comprovada / visual / mock / inferida)
capítulos propostos
contagem por relação DAH
conflitos
lacunas (comportamentos esperados que o artefato não cobre — marcar como observação, não como capacidade)
itens técnicos / visuais (não entram no índice; itens visuais alimentam o P-04)
dependências externas
secrets encontrados (apenas local)
riscos
cobertura da leitura
```

---

# 10. Perguntas ao usuário

Perguntar **somente** o que afeta o índice: escopo, divisão ou conflito. Detalhes de uma história ficam para o PA-02.

Formato:

```text
A-006 mostra exclusão definitiva de cliente.
H-014 não prevê exclusão.

Você deseja:
A) exclusão lógica
B) exclusão definitiva
C) remover do escopo
```

---

# 11. Proibições

```text
não escrever histórias A-xxx completas
não gerar H-xxx
não alterar docs/ nem backlog oficial
não registrar decisões do artefato como oficiais
não importar ou copiar código
não copiar valores de secrets
não tratar inferência ou mock como requisito
não incluir itens técnicos no índice
não colocar A-xxx no cronograma
```

---

# 12. Arquivos de saída

```text
analise-artefato/
├── inventario.md
├── resumo.md
├── indice-proposto.md
├── comparacao-dah.md
└── historias/          ← vazia; preenchida pelo PA-02
```

Essa pasta é temporária, de análise. Não faz parte da documentação oficial DAH.

---

# 13. Resposta final no chat

```text
ANÁLISE DO ARTEFATO

Origem: ...
Entrada: ...
Tipo: ...
Stack: ... (oficial: ...)

Capacidades: N
- comprovadas: x | visuais: x | mock: x | inferidas: x

Capítulos propostos: N
Índice: A-001 até A-0NN

Comparação DAH:
- x novas | x equivalentes | x parciais | x mais amplas | x conflitantes

Itens técnicos/visuais fora do índice: N

Perguntas:
1. ...

Próxima ação:
Revisar indice-proposto.md.
Depois executar: PA-02 A-001
```

---

# Regra final

```text
PA-01 NÃO COMEÇA PELO CÓDIGO.
COMEÇA RECONSTRUINDO O SISTEMA REPRESENTADO PELO ARTEFATO.

ARTEFATO → INVENTÁRIO → CAPACIDADES → CAPÍTULOS → ÍNDICE PROPOSTO
         → COMPARAÇÃO DAH → REVISÃO HUMANA → PA-02

PA-01 ORGANIZA.
PA-02 ESCREVE.
P-01 OFICIALIZA.
PA-03 NORMALIZA O CÓDIGO.
```
