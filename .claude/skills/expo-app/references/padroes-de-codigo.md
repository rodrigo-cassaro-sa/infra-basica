# Padrões de código

## Sumário
1. TypeScript
2. Componentes
3. Estado (qual usar)
4. Hooks e useEffect
5. Formulários
6. Regras de negócio
7. Naming, funções, constantes, comentários
8. Performance

---

## 1. TypeScript

- `strict: true` + `noUncheckedIndexedAccess: true` (template em `assets/templates/tsconfig.json`).
- Props sempre tipadas com `type XProps = {...}`.
- `any` proibido. Dado externo = `unknown` → Zod.
- Prefira `z.infer` a duplicar tipo à mão.
- União discriminada para estados com formas diferentes:
  ```ts
  type PaymentState =
    | { status: "idle" }
    | { status: "processing" }
    | { status: "paid"; receiptId: string }
    | { status: "failed"; reason: string };
  ```

## 2. Componentes

Pequenos, previsíveis, tipados, focados em apresentação.

```tsx
type UserCardProps = {
  user: User;
  onPress: (id: string) => void;
};

export function UserCard({ user, onPress }: UserCardProps) {
  return (
    <Card
      accessibilityRole="button"
      accessibilityLabel={`Abrir ${user.fullName}`}
      onPress={() => onPress(user.id)}
    >
      <Text variant="title">{user.fullName}</Text>
      <Text variant="caption">{user.email}</Text>
    </Card>
  );
}
```

Extraia componente quando houver **reutilização, complexidade, responsabilidade própria
ou necessidade de teste**. Não extraia para economizar 3 linhas de JSX.

Tela grande vira composição:
```text
CadastroScreen
├── CadastroHeader
├── PersonalDataForm
├── AddressForm
└── SubmitBar
```

Não copie e cole componente parecido — parametrize ou componha.

## 3. Estado (qual usar)

| Tipo | Ferramenta | Exemplo |
|---|---|---|
| Local simples | `useState` | modal aberto, aba, texto digitado |
| Local complexo | `useReducer` | wizard multi-etapa, carrinho da tela |
| Derivado | **cálculo no render** | `fullName`, total, filtro |
| Do servidor | TanStack Query | listas, detalhes, qualquer GET |
| Formulário | React Hook Form | qualquer form com 3+ campos |
| Global estável | Context | dependência injetada rara (tema já é `useTheme`, idioma é i18next) |
| Global mutável compartilhado | Zustand (`src/stores`) | sessão (`session-store`), preferências (`preferences-store`), carrinho global |
| URL | params do Expo Router | id, filtros compartilháveis |

Errado:
```tsx
const [fullName, setFullName] = useState("");
useEffect(() => setFullName(`${first} ${last}`), [first, last]);
```
Certo:
```tsx
const fullName = `${first} ${last}`;
```

## 4. Hooks e useEffect

- Hooks só no topo do componente/hook, nunca em `if`, loop ou após `return`.
- Hook de feature esconde a mecânica: a tela chama `useUser(id)` e não sabe de URL.
- `useEffect` **só** para sincronizar com sistema externo: listener, timer, AppState,
  subscription, API nativa. Sempre com cleanup.
- Não use `useEffect` para: derivar estado, buscar dado (é Query), reagir a evento de
  clique (faça no handler), resetar estado ao trocar prop (use `key`).

```tsx
useEffect(() => {
  const sub = AppState.addEventListener("change", onAppStateChange);
  return () => sub.remove();
}, []);
```

## 5. Formulários

React Hook Form + Zod. Um `useForm`, nunca dezenas de `useState`. Campos via `FormInput`,
422 do backend nos campos com `applyFieldErrors`, botão bloqueado com `mutation.isPending`.
Padrão completo, props de teclado, máscaras e validadores BR: `formularios.md`.

Validação no app = UX. Backend revalida sempre.

## 6. Regras de negócio

Regra fora do JSX, em função pura nomeada, com teste.

Ruim:
```tsx
<Button disabled={user.age < 18 || !user.active || user.balance <= 0} />
```
Bom:
```ts
// features/users/utils/user-rules.ts
export function canUserPurchase(user: User): boolean {
  return user.age >= MIN_PURCHASE_AGE && user.active && user.balance > 0;
}
```
```tsx
<Button disabled={!canUserPurchase(user)} />
```

Camadas: UI → regra/caso de uso → service → API. Nunca UI → banco.

## 7. Naming, funções, constantes, comentários

- Nomes dizem intenção: `currentUser`, `availableCampaigns`, `accessToken` — nunca `d`, `x`, `info`, `temp`.
- Funções com verbo e uma responsabilidade: `calculateCampaignPrice`, não `calc`.
  Função que busca + valida + calcula + salva + navega está fazendo coisa demais.
- Booleanos como pergunta: `isLoading`, `hasPermission`, `canEdit`, `shouldRefresh`.
- Sem número mágico: `const MAX_LOGIN_ATTEMPTS = 5;` em `src/constants`.
- Comentário explica **por quê** (restrição, regra incomum, decisão), não o quê.

## 8. Performance

Não otimize sem medir (em build de release). Com React Compiler ativo, nada de
`useMemo`/`useCallback`/`memo` manual sem medição. Listas (FlatList → FlashList), item de
lista, `expo-image`, re-render e busca: `performance.md`.
