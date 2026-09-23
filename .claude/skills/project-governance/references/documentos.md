# Documentos oficiais da DAH

## Índice

- [Estrutura e fonte de verdade](#estrutura-e-fonte-de-verdade)
- [Índice como backlog oficial](#índice-como-backlog-oficial)
- [Numeração das histórias](#numeração-das-histórias)
- [Capítulos](#capítulos)
- [Regras de negócio](#regras-de-negócio)
- [Modelo de dados](#modelo-de-dados)
- [Contratos de API](#contratos-de-api)
- [Mapa de fluxos](#mapa-de-fluxos)
- [Mapa de telas](#mapa-de-telas)
- [Guia visual](#guia-visual)

---

## Estrutura e fonte de verdade

```text
docs/
├── historias/
│   ├── indice.md
│   └── H-xxx.md ...
├── regras-de-negocio.md
├── modelo-de-dados.md
├── contratos-de-api.md
├── mapa-de-fluxos.md
├── mapa-de-telas.md
├── guia-visual.md
├── mapa-de-testes.md
├── mapa-de-decisoes.md
├── diario-de-bordo.md
└── cronograma.md
```

Cada artefato tem função própria e não se sobrepõe aos outros:

```text
indice.md              → backlog e estado das histórias
histórias H-xxx        → comportamento aprovado
regras-de-negocio.md   → regras consolidadas
modelo-de-dados.md     → estrutura conceitual dos dados
contratos-de-api.md    → contratos de comunicação
mapa-de-fluxos.md      → fluxos funcionais
mapa-de-telas.md       → estrutura funcional das interfaces
guia-visual.md         → sistema visual
mapa-de-testes.md      → validações e evidências
mapa-de-decisoes.md    → decisões e motivos
diario-de-bordo.md     → evolução e retomada
cronograma.md          → previsão viva do projeto
```

Antes de criar qualquer arquivo documental novo:

```text
essa informação cabe em documento oficial existente?
```

Se sim, atualizar o existente. Documentos paralelos criam duas versões da verdade
e ninguém descobre qual é a válida até alguém implementar a errada.

## Índice como backlog oficial

`docs/historias/indice.md` é a fonte oficial do backlog.

```markdown
| Código | Título | Capítulo | Release | Status |
|---|---|---|---|---|
| H-001 | Criar novo usuário | Credenciamento e acesso | MVP | planejada |
```

Nunca deixar o índice divergente do arquivo da história. Qualquer mudança de
status, título ou capítulo acontece nos dois lugares na mesma operação.

A **Versão** não está no índice: ela vive só dentro do arquivo da história, para não
haver dois lugares a sincronizar. O índice guarda o `Release` (escopo da entrega).

## Numeração das histórias

Sequência global: `H-001`, `H-002`, `H-003`, ...

- nunca reutilizar código;
- nunca renumerar histórias existentes;
- história cancelada mantém o código;
- capítulo não interfere na numeração;
- nova história recebe o próximo número livre.

## Capítulos

Capítulo é classificação funcional — uma área compreensível do negócio.
Exemplos: Credenciamento e acesso, Perfil, Permissões, Comunicação, Agenda,
Financeiro, Relatórios, Administração.

Capítulo não exige pasta própria, não altera numeração e pode receber novas
histórias a qualquer momento.

## Regras de negócio

`docs/regras-de-negocio.md`, identificadas como `RN-001`, `RN-002`, ...

Não duplicar regra equivalente. Uma regra pode estar associada a várias
histórias — é o documento que consolida, não a história.

## Modelo de dados

Atualizar quando histórias criam entidade, alteram campos, criam relação,
alteram cardinalidade, adicionam constraint ou alteram status/enums.

A documentação representa o modelo **consolidado**, não o diff de cada história.

## Contratos de API

Atualizar, quando aplicável: método, rota, entrada, saída, erros, autenticação,
autorização, paginação, filtros, idempotência.

## Mapa de fluxos

Atualizar quando a história cria fluxo, muda sequência, cria decisão, adiciona
caminho alternativo ou altera a integração entre etapas.

O fluxo documentado é funcional, não fluxo de código.

## Mapa de telas

Atualizar quando a história cria tela, altera tela, adiciona ação, altera
navegação ou adiciona estado visual. Várias histórias podem compartilhar a mesma
tela.

## Guia visual

Atualizar quando houver novo padrão visual, nova categoria de tela, novo
componente estrutural, nova navegação, mudança de responsividade ou mudança de
identidade.

Não alterar o guia por mudança cosmética trivial.
