# Navegação com Expo Router

> Desde o SDK 56 o Expo Router tem implementação própria (fork de partes do React Navigation).
> Não importe de `@react-navigation/*` em projeto com expo-router. Confirme APIs em
> https://docs.expo.dev/router/introduction/ quando estiver em dúvida.

## Convenções de arquivo

| Arquivo | Vira |
|---|---|
| `src/app/index.tsx` | `/` |
| `src/app/perfil.tsx` | `/perfil` |
| `src/app/usuarios/[id].tsx` | `/usuarios/123` |
| `src/app/[...rest].tsx` | catch-all |
| `src/app/(app)/home.tsx` | `/home` — grupo `( )` organiza sem aparecer na URL |
| `src/app/_layout.tsx` | layout (Stack, Tabs, Slot) do nível |
| `src/app/+not-found.tsx` | tela 404 |

## Root layout com providers e guarda de sessão

Template pronto: `assets/templates/root-layout.tsx` (destino `src/app/_layout.tsx`), ligado ao
`session-store` (`seguranca.md`, "Fluxo de sessão"). Resumo:

```tsx
function RootNavigator() {
  const status = useSessionStore((s) => s.status);
  useEffect(() => { useSessionStore.getState().bootstrap(); }, []);
  useEffect(() => { if (status !== "loading") SplashScreen.hideAsync(); }, [status]);
  if (status === "loading") return null; // splash continua visível

  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Protected guard={status === "authenticated"}>
        <Stack.Screen name="(app)" />
      </Stack.Protected>
      <Stack.Protected guard={status === "unauthenticated"}>
        <Stack.Screen name="(auth)" />
      </Stack.Protected>
    </Stack>
  );
}
```

- `Stack.Protected` (SDK 53+) separa área logada de forma declarativa. Quando o `guard` muda, o router redireciona sozinho — não use `router.replace` após login/logout.
- A splash fica visível enquanto `bootstrap()` lê o token e chama `/auth/me`: a tela de login não pisca para quem já está logado.
- Área por papel: `Stack.Protected guard={user?.role === "admin"}` aninhado no `(app)/_layout.tsx`.
- Guard de rota é UX. A API continua exigindo token e checando permissão.

## Navegar

```tsx
import { router, Link } from "expo-router";

router.push("/perfil");                 // empilha
router.replace("/home");                // substitui (não volta)
router.back();
router.push({ pathname: "/usuarios/[id]", params: { id: usuario.id } });

<Link href="/perfil">Perfil</Link>
<Link href={{ pathname: "/usuarios/[id]", params: { id: "15" } }}>Ver</Link>
```

Use **typed routes** (`experiments.typedRoutes: true` no app config — já vem no template): `href` errado vira erro de TypeScript.

## Parâmetros

```tsx
import { useLocalSearchParams } from "expo-router";

export default function UsuarioScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  // params chegam como string — converta/valide (Zod) antes de usar
}
```

Passe **ids** por parâmetro, não objetos inteiros. A tela de destino busca o dado (TanStack Query reaproveita o cache).

## Tabs

- `Tabs` de `expo-router` (tabs em JS, altamente customizáveis).
- **Native Tabs** (usado no template padrão SDK 55+): tab bar nativa do iOS/Android. O caminho de import mudou entre versões — confira na doc "Native tabs" da versão do projeto.

## Modais

```tsx
<Stack.Screen name="novo-item" options={{ presentation: "modal" }} />
```
Formsheet / sheets nativos: `presentation: "formSheet"` com `sheetAllowedDetents`.

## Loading e erro por rota

- Exporte `ErrorBoundary` numa rota para capturar erro de render daquela árvore.
- SDK 56+: exporte `SuspenseFallback` no `_layout` para customizar o carregamento com Suspense.

## Deep links

Defina `scheme` no app config (ex.: `"scheme": "meuapp"`). Toda rota já é deep link: `meuapp://usuarios/15`. Para links https (universal/app links) configure `associatedDomains` (iOS) e `intentFilters` (Android) — exige dev build.
