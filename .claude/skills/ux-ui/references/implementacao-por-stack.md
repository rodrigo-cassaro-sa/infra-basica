# Implementação no código (ponte com a expo-app)

Esta skill não define arquitetura de código. Ela diz **o que** a interface precisa fazer;
a `expo-app` — única stack de frontend da casa (Android, iOS e Web) — diz **onde** e
**como** isso vira código. Este arquivo é a ponte.

## Sumário
1. Qual skill usar
2. Tokens: nomes em cada stack
3. Componentes: onde moram e como se chamam
4. Estados de tela em cada stack
5. Documentos do projeto
6. Decisões unificadas entre as skills
7. Pipeline de identidade por projeto

---

## 1. Qual skill usar

| Pedido | Skill |
|---|---|
| Qualquer tela de app, painel web, sistema administrativo, site | `expo-app` + esta |
| Landing / peça de marca | `expo-app` (`web.output: "static"`) + `frontend-web` para estética + esta como piso |
| Lib só-web (gráfico complexo, editor rico, tabela avançada) | componente DOM da `expo-app` (`references/web.md` §6) + esta |

## 2. Tokens: nomes em cada stack

Uma fonte só: `tokens/tokens.json` (DTCG) → `scripts/build-tokens.py` gera `tokens.ts` (Expo)
e, se o projeto tiver componentes DOM com CSS próprio, `tokens.css`. O `src/theme/index.ts` da `expo-app` consome o `tokens.ts` gerado e expõe
tudo por `useTheme()`. Os nomes abaixo são os que o gerador emite — use-os como estão.

| Papel (esta skill) | Expo (`useTheme()`) | Componente DOM (CSS custom properties) |
|---|---|---|
| primary · hover · pressed · onPrimary | `colors.primary` · `primaryHover` · `primaryPressed` · `onPrimary` | `--color-primary` · `--color-primary-hover` · `--color-primary-pressed` · `--color-on-primary` |
| background · surface · surfaceVariant | `colors.background` · `surface` · `surfaceVariant` | `--color-background` · `--color-surface` · `--color-surface-variant` |
| textPrimary · textSecondary · textDisabled | `colors.text` · `textMuted` · `textDisabled` | `--color-text` · `--color-text-muted` · `--color-text-disabled` |
| border · divider · focus | `colors.border` · `divider` · `focus` | `--color-border` · `--color-divider` · `--color-focus` |
| error (papel) · success · warning · info | `colors.danger` · `success` · `warning` · `info` | `--color-danger` · `--color-success` · `--color-warning` · `--color-info` |
| spacing 4·8·16·24·32·48 | `spacing.xs·sm·md·lg·xl·xxl` | `--space-1·2·4·6·8·12` |
| escala completa (12, 40, 64…) | `space[3]`, `space[10]`, `space[16]` | `--space-3`, `--space-10`, `--space-16` |
| radius | `radius.sm·md·lg·xl·full` (`pill` = `full`) | `--radius-sm·md·lg·xl·full` |
| typography | `typography.display·h1–h4·bodyLarge·body·bodySmall·label·caption` (+ `title`=h3, `subtitle`=h4) | `--font-size-*`, `--line-height-*`, `--font-weight-*`, `--font-family-base` |
| fonte da marca | `font.native` no tokens.json → aplicada por peso em `typography` | `font.family.base` |
| shadow | `shadow.sm·md·lg` (prop `boxShadow`) | `--shadow-sm·md·lg` |
| motion | `motion.fast·base·slow` | `--duration-fast·base·slow` |
| breakpoints | `breakpoints.sm·md·lg·xl` (+ `tablet`, `desktop`) | media/container queries 480·768·1024·1440 |
| alvo de toque | `MIN_TOUCH_TARGET` (48) | `--size-touch-target-min` (48px) · `--size-pointer-target-min` (44px) |

`--check` no gerador valida os pares de contraste AA nos dois temas: rode sempre que mudar cor.

## 3. Componentes

| Conceito | Onde fica na `expo-app` |
|---|---|
| Tela com safe area/teclado | `components/ui/Screen` |
| Botão (primary/secondary/tertiary/destructive) | `components/ui/button.tsx` variantes `primary/secondary/ghost/danger` |
| Input com label e erro | `components/forms/FormInput` (RHF + Zod) |
| Loading | `feedback/LoadingView` (+ skeleton da feature) |
| Vazio | `feedback/EmptyState` |
| Erro | `feedback/ErrorState` + `getUserMessage` |
| Offline | `feedback/OfflineState` |
| Toast | lib do projeto em `components/ui` (registrada em `docs/stack.md`) |
| Modal | rota modal do Expo Router; bottom sheet no celular, diálogo no desktop |
| Lista longa | `FlatList` (→ `FlashList` com problema medido) |
| Tabela (desktop) | linhas nativas; avançada via componente DOM (`web.md` §5) |
| Navegação principal | tabs no celular, barra lateral no desktop (`web.md` §3) |

Regra: termos da esquerda desta skill (tertiary, destructive) mapeiam para os nomes já
existentes no código (ghost, danger). **Não renomeie** o que existe; só documente o mapa
no `guia-visual.md`.

## 4. Estados de tela

`if (query.isPending) … isError … isEmpty … conteúdo` com `components/feedback`; offline via
`NetworkError`. Componente DOM não tem estados próprios: a tela nativa trata e só renderiza
o DOM com dado pronto.

Esta skill adiciona: textos reais em cada estado (ver `conteudo-e-microcopy.md`),
vazio-por-filtro diferente de vazio, refresh que não apaga o conteúdo, 403/404 amigáveis.

## 5. Documentos do projeto

Pasta `docs/` do produto (em monorepo, na raiz, compartilhada com o backend):

| Documento | Papel UX |
|---|---|
| `docs/guia-visual.md` | design system do projeto: tokens, componentes, mapa de nomes, vocabulário, decisões de plataforma. Template: `assets/templates/docs/guia-visual.md` |
| `docs/mapa-de-telas.md` | telas (T-), estados, navegação e `GV-*` usados — skill `dah-documentacao` |
| `docs/rotas.md` | T- → rota → arquivo → hook — skill `expo-app` |
| `docs/telas/<tela>.md` | especificação de UX por tela quando a tela é complexa. Template: `assets/templates/docs/spec-de-tela.md` |
| `docs/stack.md` | decisões de lib (ex.: lib de toast, de ícones, de gráficos) |

Quer separar mais (projeto grande)? `docs/design/{design-system,componentes,acessibilidade,responsividade,web,app}.md` —
mas comece com `guia-visual.md`; separar cedo demais espalha a verdade.

Com Spec Kit/SDD: a spec da feature cita a tela e seus estados; o `plan.md` referencia
`guia-visual.md`.

## 6. Decisões unificadas entre as skills

| Tema | Decisão (já aplicada nos templates) |
|---|---|
| Alvo de toque | 48 em código cross-platform (`MIN_TOUCH_TARGET`, gerado dos tokens). Web com ponteiro: 44 px mínimo, 24 px absoluto (WCAG 2.5.8). |
| Escalas (raio, espaço, tipografia) | As do `tokens.json` desta skill. O `theme.ts` da `expo-app` não tem valor próprio: consome o `tokens.ts` gerado. |
| Tema padrão | Escuro quando o `guia-visual.md` não definir outro; usuário escolhe Sistema/Claro/Escuro (`preferences-store`). |
| Estados de tela | Lista canônica em `estados-e-feedback.md` §1; implementação em `components/feedback`. |
| Formato de erro da API | `{ code, message, fieldErrors: { campo: ["msg"] } }` ; texto ao usuário sempre via `getUserMessage` — nunca `error.message` cru. |
| `frontend-web` × esta | Produto → esta manda; marketing → `frontend-web` lidera com esta como piso. Em produto, a personalidade vai para paleta, tipografia e um detalhe memorável — não para padrões de interação. |
| CAIXA ALTA em rótulos, "→" em botão | Evitar, em produto e marketing. |
| Ícones | Uma família. Expo SDK 56+: `@react-native-vector-icons/*` (não `@expo/vector-icons`). |
| Acessibilidade em RN | Props `accessibility*` (estilo único da casa). |
| Idioma | pt-BR com `Intl` por padrão; multi-idioma com i18next (`i18n.md`), decisão registrada no `guia-visual.md`. |

## 7. Pipeline de identidade por projeto

Cada software tem identidade própria sem sair do padrão de qualidade:

```text
1. docs/guia-visual.md   → decisões: marca, fonte, tema padrão, densidade, vocabulário, exceções
2. tokens/tokens.json    → valores (cópia de assets/tokens/tokens.json ajustada ao guia)
3. build-tokens.py --check → contraste AA garantido nos dois temas
4. tokens.ts (+ tokens.css se houver DOM) → consumidos pelo `theme`
5. componentes base      → mesmos para todos os apps; só os tokens mudam
```

O que **muda** por projeto: cores de marca, fonte, raio, densidade, tema padrão, ícones,
vocabulário. O que **não muda**: regras inegociáveis desta skill, papéis semânticos,
estados de tela, alvo de toque, contraste, componentes base e seus nomes.
