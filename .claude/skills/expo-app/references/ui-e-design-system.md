# UI e design system

## Sumário
1. Tokens do tema e identidade do app
2. Componentes base
3. Estados de tela
4. Listas
5. Imagens
6. Responsividade e Web
7. Acessibilidade
8. Permissões e notificações
9. Guia visual antes das telas
10. Idioma e formatação

---

## 1. Tokens do tema e identidade do app

A **skill `ux-ui`** define o comportamento e o piso de qualidade da interface; esta seção diz
como isso vira código no Expo. Cada app tem identidade própria (cor, fonte, raio, tema
padrão), mas todos seguem o mesmo pipeline:

```text
docs/guia-visual.md        decisões humanas do projeto (marca, fonte, tema padrão, vocabulário)
        ↓
tokens/tokens.json         fonte única dos valores (DTCG) — template na skill ux-ui
        ↓  python3 <ux-ui>/scripts/build-tokens.py tokens/tokens.json --ts src/theme/tokens.ts --check
src/theme/tokens.ts        GERADO — nunca editar à mão (--check valida contraste AA)
        ↓
src/theme/index.ts         useTheme() — única porta de entrada das telas (template theme.ts)
```

Trocar a identidade de um app = editar `tokens.json` e regenerar. Nenhum componente muda.

```text
useTheme() → { scheme, colors, spacing, space, radius, typography, shadow, motion, breakpoints }
colors      primary · primaryHover · primaryPressed · onPrimary · background · surface · surfaceVariant
            text · textMuted · textDisabled · border · divider · focus · success · warning · danger · info
spacing     xs 4 · sm 8 · md 16 · lg 24 · xl 32 · xxl 48   (escala completa em space[1..16])
radius      sm 4 · md 8 · lg 12 · xl 16 · full/pill
typography  display · h1–h4 · title · subtitle · bodyLarge · body · bodySmall · label · caption
motion      fast 150 · base 250 · slow 350 (ms)
MIN_TOUCH_TARGET = 48
```

- **Claro/escuro**: dois conjuntos com as mesmas chaves; `useTheme()` resolve pela preferência
  do usuário (`preferences-store`: sistema/claro/escuro) e, em "sistema", pelo SO.
  `DEFAULT_SCHEME` (escuro, padrão da casa) vem do `guia-visual.md`.
- **Fonte da marca**: carregue com `expo-font` (ex.: `@expo-google-fonts/inter`) no
  `_layout.tsx` antes de esconder a splash, e registre o nome carregado por peso em
  `font.native` do `tokens.json`. `useTheme().typography` já aplica a família certa por peso.
- Componente nunca faz `isDark ? "#111" : "#fff"`: consome o papel (`colors.surface`).

## 2. Componentes base

Camada própria em `src/components/ui`, construída uma vez e usada em todas as telas
(importe de `@/components/ui`):

`Screen` (template `screen.tsx`) · `Button` (template `button.tsx`: primary · secondary ·
ghost · danger, `loading`, pressed, ≥ 48) · `Text` (variantes da tipografia) · `Card` ·
`Badge` · `Avatar` · `Divider` · `Modal` · `Tabs`

Forms em `src/components/forms`: `FormInput` (template `form-input.tsx`).

Feedback em `src/components/feedback`: `LoadingView`, `EmptyState`, `ErrorState`
(recebe o erro e usa `getUserMessage`), `OfflineState`, `RetryButton`.

Nenhuma tela redesenha botão. Se um botão novo for necessário, vira variante do `Button`.
Mapa de nomes da `ux-ui` → código (tertiary = ghost, destructive = danger) fica no `guia-visual.md`.

## 3. Estados de tela

Toda operação assíncrona considera: **idle, loading, success, empty, error** — e listas
também **refresh, paginação e sem internet**. Não pense só "tem dado / não tem dado".

Ordem padrão de render:
```tsx
if (query.isPending) return <LoadingView />;
if (query.isError) return <ErrorState error={query.error} onRetry={query.refetch} />;
if (isEmpty(query.data)) return <EmptyState ... />;
return <Conteudo />;
```

Mensagens ao usuário: curtas, em português, com ação. "Não foi possível carregar seus
dados. Tente novamente." — nunca stack trace.

## 4. Listas

`FlatList` para qualquer lista que possa crescer; `FlashList` quando houver problema medido
(`performance.md` §2).

```tsx
<FlatList
  data={users}
  keyExtractor={(item) => item.id}
  renderItem={({ item }) => <UserCard user={item} onPress={openUser} />}
  ItemSeparatorComponent={Divider}
  ListEmptyComponent={<EmptyState title="Nenhum usuário" />}
  onRefresh={refetch}
  refreshing={isRefetching}
  onEndReached={() => hasNextPage && !isFetchingNextPage && fetchNextPage()}
  onEndReachedThreshold={0.4}
/>
```

`renderItem` estável e item leve. `ScrollView + map` só para conteúdo curto e fixo.

## 5. Imagens

`expo-image` sempre para imagem remota, com dimensão definida e tamanho certo vindo do
backend. Placeholder, transição, `recyclingKey` e prefetch: `performance.md` §4.

## 6. Responsividade e Web

O app roda em celular, tablet e navegador. Uma base de código só.
- Prefira `flex`, porcentagens e `maxWidth` a larguras fixas (`width: 350`).
- Conteúdo centralizado com `maxWidth` (ex.: 720) em telas largas.
- `useWindowDimensions()` + `useTheme().breakpoints` (tablet 768 · desktop 1024).
- Teste a Web de verdade (`npx expo start --web`): hover, teclado, foco, scroll e
  tamanhos grandes se comportam diferente.
- APIs sem suporte na Web (SecureStore, algumas permissões) ficam atrás de adaptador
  ou arquivo `.web.tsx`.
- Layout de desktop (barra lateral, tabelas, hover, teclado), SEO e componentes DOM: `web.md`.

## 7. Acessibilidade

Não é opcional. Estilo de props do projeto: `accessibility*` (um estilo só por projeto).

```tsx
<Pressable
  accessibilityRole="button"
  accessibilityLabel="Salvar usuário"
  accessibilityState={{ disabled: isSaving, busy: isSaving }}
  hitSlop={8}
  onPress={save}
>
```

Mínimo: role e label em todo interativo · área de toque ≥ 48 (`MIN_TOUCH_TARGET`) ·
contraste AA (garantido pelo `build-tokens.py --check`) · fonte respeita a escala do sistema
(não travar `allowFontScaling`) · erro de formulário anunciado · ordem de foco lógica na Web.
Padrões completos (card como unidade, gesto com alternativa, modal que isola o fundo, foco
após ação, leitor de tela ligado): skill `ux-ui`, `acessibilidade.md`.

## 8. Permissões e notificações

Permissão só no momento de uso, com explicação antes:
usuário toca "Escanear QR Code" → tela explica → pede câmera. Nunca pedir câmera,
localização, microfone, fotos e notificações na primeira abertura.

Push em serviço dedicado (`src/services/notifications/`), separando: permissão → token
do dispositivo → registro no backend → preferências → recebimento → navegação por deep
link. Telas não conhecem essa lógica.

## 9. Guia visual antes das telas

Antes de construir telas, o projeto precisa de `docs/guia-visual.md` (template na skill
`ux-ui`: `assets/templates/docs/guia-visual.md`) e do `tokens/tokens.json` gerado a partir
dele. Sem isso a IA decide cor e espaçamento tela a tela e o app perde consistência entre
sessões.

## 10. Idioma e formatação

Datas, números e moeda sempre via `Intl` em `src/utils/format.ts`, nunca na mão. Projeto
multi-idioma (i18next + expo-localization): skill `ux-ui`, `i18n.md`.
