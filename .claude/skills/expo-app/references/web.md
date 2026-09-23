# Web com Expo

A casa usa **só Expo** no frontend: app Android, app iOS, painel web e site saem da mesma
base de código. Este arquivo cobre o que muda quando a Web é importante (painel, sistema
administrativo, site com SEO) e quando usar componentes DOM.

## Sumário
1. Decisões por tipo de projeto
2. Saída web, SEO e `+html.tsx`
3. Layout responsivo (celular → desktop)
4. Interação de desktop: hover, teclado, foco
5. Painel denso: tabelas, filtros, gráficos
6. Componentes DOM (`"use dom"`)
7. Sessão, deploy e checklist

---

## 1. Decisões por tipo de projeto

| Projeto | Como fazer |
|---|---|
| App + versão web do mesmo produto | Padrão da skill. Web ganha layout de desktop (§3) |
| Painel/sistema só web (admin, CRM, dashboard) | Mesmo projeto Expo, pensado desktop-first; tabelas e gráficos pesados via componente DOM (§5, §6) |
| Site institucional / landing com SEO | Expo com `web.output: "static"`, `Head` por página e `+html.tsx` (§2); estética com `frontend-web` dentro dos tokens |
| App + painel admin do mesmo cliente | Um repositório; grupo de rotas `(admin)` protegido por papel, ou projeto separado se o público e o deploy forem diferentes (decisão em `docs/stack.md`) |

Não existe mais "stack web à parte" na casa. Caso realmente fora do Expo (ex.: CMS de
terceiros) é exceção registrada em `docs/stack.md` com o motivo.

## 2. Saída web, SEO e `+html.tsx`

`app.config.ts` da casa já sai com `web: { output: "static" }`: uma página HTML por rota,
indexável e mais rápida no primeiro carregamento que SPA.

| `web.output` | Quando |
|---|---|
| `static` (padrão da casa) | Tudo que tem página pública ou precisa de SEO/preview de link |
| `single` | Painel 100% atrás de login, sem SEO |
| `server` | Só se precisar de API routes do Expo Router (a casa prefere backend separado) |

**HTML raiz** — `src/app/+html.tsx` (só roda na Web, no build):

```tsx
import { ScrollViewStyleReset } from "expo-router/html";
import type { PropsWithChildren } from "react";

export default function Root({ children }: PropsWithChildren) {
  return (
    <html lang="pt-BR">
      <head>
        <meta charSet="utf-8" />
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <ScrollViewStyleReset />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

**Título e descrição por página** (SEO e preview no WhatsApp):

```tsx
import Head from "expo-router/head";

export default function PlanosScreen() {
  return (
    <>
      <Head>
        <title>Planos e preços | Nome do App</title>
        <meta name="description" content="Resumo da página em uma frase (até ~155 caracteres)." />
        <meta property="og:title" content="Planos e preços | Nome do App" />
      </Head>
      {/* tela */}
    </>
  );
}
```

Rota dinâmica pública com `static` (ex.: `/blog/[slug]`): exporte `generateStaticParams()`
na rota para listar as páginas geradas no build. Rota atrás de login não precisa.

Limite honesto: conteúdo que muda a toda hora e precisa estar indexado (catálogo grande,
marketplace) não combina com página estática gerada no build. Registre a decisão em
`docs/stack.md` antes de começar.

## 3. Layout responsivo (celular → desktop)

Hook único da casa — `src/hooks/use-breakpoint.ts`:

```ts
import { useWindowDimensions } from "react-native";

import { breakpoints } from "@/theme";

export function useBreakpoint() {
  const { width } = useWindowDimensions();
  return {
    width,
    isPhone: width < breakpoints.tablet,
    isTablet: width >= breakpoints.tablet && width < breakpoints.desktop,
    isDesktop: width >= breakpoints.desktop,
  };
}
```

Regras:
- **Navegação**: tabs embaixo no celular; no desktop, barra lateral fixa (mesmas rotas).
  Troque no `_layout` do grupo com `isDesktop`, não duplique telas.
- **Conteúdo**: `maxWidth` (720 para leitura/formulário, 1200 para painel) centralizado.
- **Listas**: cards no celular; tabela no desktop quando o usuário compara colunas (§5).
- **Formulário no desktop**: duas colunas só para campos curtos relacionados (cidade/UF);
  ações alinhadas à direita no fim do formulário.
- **Modais**: bottom sheet no celular; diálogo centralizado no desktop.
- Nada de largura fixa em px para bloco inteiro; `flex`, `%`, `maxWidth`.

## 4. Interação de desktop: hover, teclado, foco

- **Hover**: `Pressable` com `onHoverIn`/`onHoverOut` (só dispara com mouse). Hover nunca é o
  único jeito de revelar ação — no toque ele não existe.

```tsx
const [hovered, setHovered] = useState(false);
<Pressable
  onHoverIn={() => setHovered(true)}
  onHoverOut={() => setHovered(false)}
  style={({ pressed }) => [
    styles.row,
    hovered && { backgroundColor: colors.surfaceVariant },
    pressed && { backgroundColor: colors.border },
  ]}
/>
```

- **Teclado**: todo elemento clicável é alcançável por Tab na ordem visual; Enter envia
  formulário (`onSubmitEditing` + `returnKeyType`); Esc fecha modal.
- **Foco visível**: não remova o contorno de foco; se estilizar, use `colors.focus`.
- **Atalhos** (painel): só se o pedido exigir; `useEffect` com listener de `keydown` sob
  `Platform.OS === "web"`, com cleanup, e nunca sobrescreva atalhos do navegador.
- **Cursor e seleção**: texto de dado (e-mail, código, valor) com `selectable`.
- **Links externos**: `Link` do Expo Router com `href` externo ou `expo-web-browser`;
  na Web abre em nova aba.

## 5. Painel denso: tabelas, filtros, gráficos

| Necessidade | Solução |
|---|---|
| Tabela simples (até ~8 colunas, paginada) | Nativa: linhas com `View` em `flexDirection: "row"`, cabeçalho fixo, `FlashList` se a lista for longa |
| Tabela com ordenação/redimensionar coluna/seleção múltipla, milhares de linhas | Componente DOM com lib web de tabela (§6) |
| Gráfico simples (barra, linha, pizza) | Lib nativa de gráfico já registrada em `docs/stack.md` |
| Gráfico interativo complexo, editor de texto rico, markdown longo, mapa web | Componente DOM |
| Filtros | Na URL (search params do Expo Router) para o usuário poder compartilhar e voltar |

Filtros e paginação sempre no servidor para lista grande (`dados-e-api.md`, paginação por cursor).

## 6. Componentes DOM (`"use dom"`)

Arquivo marcado com `"use dom"` roda como React DOM: no Android/iOS dentro de uma WebView
embutida; na Web, direto na página. Serve para usar lib web sem reescrever. A partir do
SDK 56 usa `@expo/dom-webview` sem instalação extra (SDK 55 ou anterior: `react-native-webview`).

**Use para**: gráfico interativo complexo, tabela avançada, editor de texto rico, markdown,
canvas/WebGL, embed que precisa de navegador.
**Não use para**: telas principais, listas do dia a dia, formulários, navegação — nativo é
mais rápido e mais acessível.

Regras da casa:
1. Arquivo próprio em `features/<f>/components/dom/`, um `export default` por arquivo, `"use dom"` na primeira linha.
2. **Props só serializáveis** (texto, número, booleano, array, objeto). Não passe `children`.
3. **Não busca dado nem acessa sessão lá dentro.** Query, Zustand e cookies não são compartilhados com a WebView: a tela nativa busca com o hook da feature e passa por props.
4. Ação de volta para o app = **função assíncrona como prop de primeiro nível** (native action).
5. **Tema por props**: passe `colors` do `useTheme()` (ou `scheme`) e aplique no DOM. Não duplique valores.
6. Acessibilidade continua valendo: HTML semântico, `label`, `aria-*`, contraste.
7. **Mudança em componente DOM exige build novo** — hoje eles vão embutidos e não recebem EAS Update (ver tabela de OTA em `builds-eas.md`).
8. Tamanho: `dom={{ matchContents: true }}` quando precisa se ajustar ao conteúdo, ou altura explícita via `dom={{ style: { height } }}`.

```tsx
// src/features/reports/components/dom/revenue-chart.tsx
"use dom";

import type { DOMProps } from "expo/dom";

type Point = { label: string; value: number };

type Props = {
  data: Point[];
  colors: { text: string; primary: string; border: string };
  onSelect: (label: string) => Promise<void>; // native action
  dom?: DOMProps;
};

export default function RevenueChart({ data, colors, onSelect }: Props) {
  const max = Math.max(1, ...data.map((p) => p.value));
  return (
    <figure style={{ margin: 0, color: colors.text, fontFamily: "system-ui, sans-serif" }}>
      <figcaption>Receita por mês</figcaption>
      <ul role="list" style={{ listStyle: "none", padding: 0 }}>
        {data.map((p) => (
          <li key={p.label}>
            <button
              type="button"
              aria-label={`${p.label}: ${p.value}`}
              onClick={() => onSelect(p.label)}
              style={{ all: "unset", display: "block", cursor: "pointer", minHeight: 44 }}
            >
              <span>{p.label}</span>
              <span style={{ display: "block", height: 8, width: `${(p.value / max) * 100}%`, background: colors.primary }} />
            </button>
          </li>
        ))}
      </ul>
    </figure>
  );
}
```

```tsx
// tela nativa
const { colors } = useTheme();
const report = useRevenueReport();
// ...estados de loading/erro/vazio como sempre...
<RevenueChart
  data={report.data}
  colors={{ text: colors.text, primary: colors.primary, border: colors.border }}
  onSelect={async (label) => router.push({ pathname: "/relatorios/[mes]", params: { mes: label } })}
  dom={{ matchContents: true }}
/>
```

(O exemplo usa HTML puro para ficar curto; na prática é aqui que entra a lib web de gráfico.)

Detecção: `import { IS_DOM } from "expo/dom"` diz se o código está rodando dentro de um
componente DOM. Links internos: `Link` do `expo-router/link`; nunca `<a>` para navegar.

## 7. Sessão, deploy e checklist

**Sessão na Web**: cookie `httpOnly` do backend (`seguranca.md`); o `api-client.ts` já envia
`credentials: "include"`. Backend em outro domínio: CORS com credentials e cookie
`SameSite=None; Secure`. Mesmo domínio via proxy: `SameSite=Lax`.

**Deploy**: `npx expo export -p web` gera `dist/`. Na casa: servir o `dist/` em container
estático (Caddy) no Easypanel — `Dockerfile` e `Caddyfile` prontos na skill `git-deploy`, no mesmo domínio do backend via proxy reverso
(evita CORS). Alternativa gerenciada: EAS Hosting. Com `output: "single"`, configure o
servidor para cair no `index.html`. Teste antes com `npx expo serve`.

Checklist Web:
- [ ] Rodei no navegador de verdade (`npx expo start --web`) em 375, 768 e 1280 px de largura
- [ ] Navegação vira barra lateral no desktop; conteúdo com `maxWidth`
- [ ] Tab percorre tudo em ordem; foco visível; Enter envia; Esc fecha modal
- [ ] Hover nunca é o único caminho para uma ação
- [ ] Página pública tem `Head` com título e descrição; `+html.tsx` com `lang="pt-BR"`
- [ ] Nenhuma API só-nativa sem adaptador `.web.tsx` (SecureStore, biometria, câmera)
- [ ] Componentes DOM só onde a tabela do §5 manda, com props serializáveis e tema por props
