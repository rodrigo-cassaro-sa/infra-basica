# Guia visual — [NOME DO PRODUTO]

> Design system DESTE projeto. Vale acima dos padrões da skill `ux-ui` (exceto as regras
> inegociáveis, que só mudam com registro na seção 7). A IA lê este arquivo antes de gerar
> qualquer tela. Mudou algo? Atualize aqui primeiro, depois `tokens/tokens.json`.
> Só o que é DESTE produto: regras gerais de UX ficam na skill, não se copiam aqui.
> Decisão de marca sem definição: `PENDENTE_DE_DEFINICAO (usando padrão da casa)`.
> Como derivar e manter a partir das Histórias: `ux-ui/references/guia-a-partir-de-historias.md`.

## 1. Contexto
- Plataformas: [Web | Android | iOS | tablet]
- Estratégia: [desktop-first (sistema) | mobile-first (campo)]
- Público e contexto de uso: [ex.: secretária no computador da recepção; professor no celular durante a aula]
- Tema padrão: [escuro | claro | sistema] · Troca manual (Sistema/Claro/Escuro): [sim/não]
- Densidade: [confortável | compacta | escolha do usuário]
- Idioma: [só pt-BR | multi-idioma: pt-BR, …] (ver `ux-ui/references/i18n.md`)

## 2. Identidade da marca
- Personalidade em 3 palavras: [ex.: acolhedora, enérgica, confiável]
- Cor de marca: [#…] · usada em: ação principal, estado selecionado, links (não em fundos inteiros)
- Fonte: [família] · arquivos/pesos carregados: [ex.: @expo-google-fonts/inter 400, 600, 700]
- Logo: [arquivo] · versões clara/escura: [ ]
- Ícone do app e splash: [arquivos] · cor de fundo da splash: [token `background` do tema padrão]
- Ilustrações/fotos: [estilo, fonte] · Ícones: [biblioteca, outline/filled]
- Detalhe memorável (opcional, `frontend-web`): [ex.: cantos bem arredondados, destaque em gradiente só no cabeçalho]

## 3. Tokens
Fonte: `tokens/tokens.json` (DTCG) → `src/theme/tokens.ts` / `src/styles/tokens.css`
(`python3 <ux-ui>/scripts/build-tokens.py tokens/tokens.json --ts src/theme/tokens.ts --check`).

| Papel | Claro | Escuro | Contraste verificado (--check) |
|---|---|---|---|
| primary | #… | #… | sobre background: _:1 |
| background | #… | #… | |
| surface | #… | #… | |
| text | #… | #… | _:1 / _:1 |
| textMuted | #… | #… | _:1 / _:1 |
| border | #… | #… | 3:1? |
| focus | #… | #… | 3:1? |
| success / warning / danger / info | … | … | |

Tipografia: família [ ], escala [padrão da ux-ui | ajustes]. Espaçamento: 4·8·12·16·24·32·48·64.
Raio: [padrão sm 4 · md 8 · lg 12 · xl 16 | ajustes]. Sombra: [ ]. Movimento: fast [ ]ms · base [ ]ms · slow [ ]ms.
Breakpoints: 480 · 768 · 1024 · 1440. Alvo de toque mínimo: 48.

## 4. Componentes base
| ID | Conceito | Nome no código | Variantes | Observação |
|---|---|---|---|---|
| GV-CMP-001 | Botão | `Button` | primary · secondary · ghost (=tertiary) · danger (=destructive) | 1 primary por área |
| GV-CMP-002 | Campo | `FormInput` | text · email · phone · password · textarea | label sempre |
| GV-CMP-003 | Estados de tela | `LoadingView` · `EmptyState` · `ErrorState` · `OfflineState` | | vazio ≠ vazio por filtro |
| … | | | | |

Ícones: [biblioteca e estilo]. Tamanhos 16 · 20 · 24.

## 5. Vocabulário
Fonte única: `docs/produto.md` (vocabulário oficial do domínio). Aqui só termos de
interface que não são do domínio:
| Use | Não use | Onde |
|---|---|---|
| Salvar | Gravar, Submeter | botão de formulário |
| … | | |

## 6. Decisões por plataforma
- Navegação Web: [sidebar com grupos …]
- Navegação App: [tabs: Início · Agenda · Alunos · Perfil]
- Ações destrutivas: [confirmação | desfazer] em [quais casos]
- Toast: [lib/componente], posição [ ]
- Formato de datas: dd/mm/aaaa · moeda R$ 1.250,00

## 7. Exceções aprovadas
| Regra da skill ux-ui | Exceção | Motivo | Data |
|---|---|---|---|

## 8. Padrões do projeto (derivados das Histórias)
<!-- Um bloco por padrão. IDs nunca são renumerados nem reaproveitados. -->

### GV-CMP-0XX — [Nome do padrão]
- **Código:** `[Componente]` (`[caminho]`)
- **Finalidade:** [ ]
- **Estrutura / variantes / estados:** [ ]
- **Não usar:** [ ]
- **Histórias:** [H-xxx, H-yyy] | Uso global

## 9. Pendências e conflitos
| Item | Tipo | Situação | Desde |
|---|---|---|---|
| Cor de marca | PENDENTE_DE_DEFINICAO | usando padrão da casa | [data] |
| [H-014 × H-066: confirmação ao excluir] | CONFLITO_VISUAL_OU_INTERACAO | aguardando decisão | [data] |
