# Dados, API e autenticação

## Sumário
1. API client com validação
2. Erros tipados
3. Schemas Zod, DTO e mapper
4. Service por domínio
5. TanStack Query (setup, queries, mutations, keys)
6. Autenticação e tokens
7. Variáveis de ambiente
8. Paginação
9. Cache e offline
10. Formulários (→ `formularios.md`)
11. Contrato gerado por OpenAPI

---

## 1. API client com validação

O client recebe um schema Zod e só devolve dado validado. Nunca retorna `any`.
Implementação completa em `assets/templates/api-client.ts`. Assinatura:

```ts
apiClient.get(path, schema, options?)
apiClient.post(path, body, schema, options?)
apiClient.put / patch / delete
```

Responsabilidades do client (e só dele):
- montar URL a partir de `config.apiUrl` (`src/config/env.ts`)
- injetar `Authorization: Bearer <token>` quando houver sessão
- `Content-Type: application/json`
- timeout via `AbortController`
- tratar `204 No Content`
- converter status HTTP em erro tipado
- validar a resposta com o schema (`safeParse`) e lançar `ContractError` se o backend
  quebrar o contrato
- repassar `x-request-id` para logs

## 2. Erros tipados

Em `assets/templates/errors.ts`:

| Classe | Quando | O que a UI faz |
|---|---|---|
| `NetworkError` | sem rede / timeout | `OfflineState` + tentar de novo |
| `UnauthorizedError` | 401 | limpa sessão → login |
| `ForbiddenError` | 403 | mensagem de sem permissão |
| `NotFoundError` | 404 | tela de recurso não encontrado |
| `ValidationError` | 422 (com `fieldErrors`) | `setError` nos campos do formulário |
| `ServerError` | 5xx | erro genérico + retry |
| `ContractError` | resposta não bate com schema | erro genérico + log técnico |

Formato de erro esperado do backend (definir no contrato):

```json
{ "code": "USER_NOT_FOUND", "message": "Usuário não encontrado", "fieldErrors": { "email": ["já cadastrado"] } }
```

Mensagem para o usuário vem de `getUserMessage(error)` — nunca `error.message` cru.

## 3. Schemas Zod, DTO e mapper

```ts
// src/features/users/schemas/user-schema.ts
import { z } from "zod";

// Formato que a API devolve (DTO)
export const userDtoSchema = z.object({
  id: z.string(),
  first_name: z.string(),
  last_name: z.string(),
  email: z.email(),
  created_at: z.iso.datetime(),
});
export const userListDtoSchema = z.array(userDtoSchema);

// Formato do formulário (entrada do usuário)
export const userFormSchema = z.object({
  firstName: z.string().trim().min(2, "Informe o nome"),
  lastName: z.string().trim().min(2, "Informe o sobrenome"),
  email: z.email("E-mail inválido"),
});
```

```ts
// src/features/users/types/user-types.ts
import type { z } from "zod";
import type { userDtoSchema, userFormSchema } from "../schemas/user-schema";

export type UserDto = z.infer<typeof userDtoSchema>;
export type UserFormValues = z.infer<typeof userFormSchema>;

// Modelo usado pela UI
export type User = {
  id: string;
  fullName: string;
  email: string;
  createdAt: Date;
};
```

```ts
// src/features/users/utils/user-mapper.ts
import type { User, UserDto, UserFormValues } from "../types/user-types";

export function toUser(dto: UserDto): User {
  return {
    id: dto.id,
    fullName: `${dto.first_name} ${dto.last_name}`,
    email: dto.email,
    createdAt: new Date(dto.created_at),
  };
}

export function toUserPayload(values: UserFormValues) {
  return { first_name: values.firstName, last_name: values.lastName, email: values.email };
}
```

Zod v4: use `z.email()`, `z.url()`, `z.uuid()`, `z.iso.datetime()` (as formas
`z.string().email()` estão deprecadas).

## 4. Service por domínio

```ts
// src/features/users/services/user-service.ts
import { apiClient } from "@/services/api/api-client";
import { userDtoSchema, userListDtoSchema } from "../schemas/user-schema";
import { toUser, toUserPayload } from "../utils/user-mapper";
import type { UserFormValues } from "../types/user-types";

export async function getUsers() {
  const dtos = await apiClient.get("/users", userListDtoSchema);
  return dtos.map(toUser);
}

export async function getUser(id: string) {
  return toUser(await apiClient.get(`/users/${id}`, userDtoSchema));
}

export async function createUser(values: UserFormValues) {
  return toUser(await apiClient.post("/users", toUserPayload(values), userDtoSchema));
}
```

O service devolve **modelo**, nunca DTO.

## 5. TanStack Query

### Setup (uma vez)
`assets/templates/query-client.ts` configura:
- `onlineManager` ligado ao `@react-native-community/netinfo` (pausa requests offline)
- `focusManager` ligado ao `AppState` (refetch ao voltar para o app)
- `retry` que **não** repete 4xx (só rede e 5xx)
- `staleTime` padrão razoável (ex.: 30s)

Provider no `src/app/_layout.tsx`:
```tsx
<QueryClientProvider client={queryClient}>
  <Stack />
</QueryClientProvider>
```

### Query keys centralizadas
```ts
// src/features/users/query-keys.ts
export const userKeys = {
  all: ["users"] as const,
  list: (filters?: object) => [...userKeys.all, "list", filters ?? {}] as const,
  detail: (id: string) => [...userKeys.all, "detail", id] as const,
};
```

### Query
```ts
export function useUsers() {
  return useQuery({ queryKey: userKeys.list(), queryFn: getUsers });
}
```

### Mutation com invalidação
```ts
export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createUser,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: userKeys.all }),
  });
}
```

### Mutation otimista
Para ação rápida e reversível (remover, marcar como feito, favoritar): atualiza o cache na
hora e desfaz se a API falhar. Para criação com dado gerado no servidor, invalidar basta.

```ts
export function useDeleteUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteUser,
    onMutate: async (id: string) => {
      await queryClient.cancelQueries({ queryKey: userKeys.list() });
      const previous = queryClient.getQueryData<User[]>(userKeys.list());
      queryClient.setQueryData<User[]>(userKeys.list(), (old) => old?.filter((u) => u.id !== id));
      return { previous };
    },
    onError: (_error, _id, context) => {
      if (context?.previous) queryClient.setQueryData(userKeys.list(), context.previous);
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey: userKeys.all }),
  });
}
```
Ação destrutiva otimista combina com "desfazer" em vez de confirmação (skill `ux-ui`, `estados-e-feedback.md`).

### Busca com filtro
Filtro dentro da key (`userKeys.list({ search })`), termo com debounce (~300 ms, `src/hooks/use-debounce.ts`)
e `placeholderData: keepPreviousData` para a lista não piscar vazia entre um termo e outro.
Cada termo tem cache próprio: voltar a um termo anterior é instantâneo.

```ts
export function useUsers(search: string) {
  return useQuery({
    queryKey: userKeys.list({ search }),
    queryFn: ({ signal }) => getUsers({ search, signal }),
    placeholderData: keepPreviousData,
  });
}
```

### Consumo na screen
```tsx
const users = useUsers();
if (users.isPending) return <LoadingView />;
if (users.isError) return <ErrorState error={users.error} onRetry={users.refetch} />;
if (users.data.length === 0) return <EmptyState title="Nenhum usuário" />;
return <UserList users={users.data} onRefresh={users.refetch} refreshing={users.isRefetching} />;
```

## 6. Autenticação e tokens

Detalhes, templates (sessão, auth-service, guarda de rota) e biometria: `seguranca.md`.

Fluxo: login → backend devolve `accessToken` (curto) + `refreshToken` (longo) → guarda
no `tokenStorage` → `apiClient` injeta o access → em 401 tenta refresh **uma vez**;
falhou, limpa sessão e manda para login.

- Mobile: `expo-secure-store` (Keychain/Keystore).
- Web: SecureStore não existe. Preferir cookie `httpOnly; Secure; SameSite` definido pelo
  backend (`credentials: "include"`). O adaptador em `assets/templates/token-storage.ts`
  isola essa diferença; na Web ele não persiste token em `localStorage`.
- Nunca AsyncStorage para token.
- Estado de sessão (usuário logado, status) é estado global legítimo →
  `src/stores/session-store.ts` (Zustand, template pronto). Sempre leia com seletor:
  `useSessionStore((s) => s.user)`.

## 7. Variáveis de ambiente

- `EXPO_PUBLIC_*` vai para o bundle → **pública**. Só URL de API, IDs públicos, flags.
- Acesse sempre de forma estática: `process.env.EXPO_PUBLIC_API_URL`
  (acesso dinâmico `process.env[nome]` não é substituído no build).
- Centralize e valide em `src/config/env.ts` (template em `assets/templates/env.ts`):
  o app falha cedo se faltar variável.
- Segredo (chave de LLM, SMTP, credencial de storage) → backend. O app chama o seu
  backend, que chama o serviço externo.
- Valores por ambiente ficam no `eas.json` (`env` de cada profile) ou em variáveis do EAS.

## 8. Paginação

Nunca `GET /users` sem limite. Contrato: `?limit=30&cursor=abc` (preferido) ou
`?page=1&limit=30`. No app, `useInfiniteQuery` + `FlatList` com `onEndReached`:

```ts
export function useUsersInfinite() {
  return useInfiniteQuery({
    queryKey: [...userKeys.all, "infinite"],
    queryFn: ({ pageParam }) => getUsersPage({ cursor: pageParam }),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (last) => last.nextCursor ?? undefined,
  });
}
```

```ts
// schema de página reutilizável (src/services/api/pagination.ts)
export const pageSchema = <T extends z.ZodType>(item: T) =>
  z.object({ items: z.array(item), nextCursor: z.string().nullable() });
```

Na lista: `onEndReached={() => hasNextPage && !isFetchingNextPage && fetchNextPage()}` — o
guard evita disparar várias páginas, porque `onEndReached` é chamado repetidamente na rolagem.
Dados: `data.pages.flatMap((p) => p.items)`. Prefira cursor a offset: com offset, item
inserido durante a rolagem gera duplicado ou pulo. Lista muito grande: `performance.md` §2.

## 9. Cache e offline

Decida explicitamente por dado quanto tempo pode ficar velho (`staleTime`):
perfil → minutos; catálogo → minutos/horas; saldo/pagamento → ~0.

Offline, por padrão: detectar rede, mostrar `OfflineState`, permitir tentar de novo.
Decida **no início** se o app precisa de mais que isso — muda a arquitetura — e registre
em `docs/stack.md`:

- **Só leitura em cache**: persistir o cache do TanStack Query
  (`@tanstack/query-async-storage-persister` + `PersistQueryClientProvider`).
- **Escrita offline**: `expo-sqlite` como fonte local, fila de sincronização, ids gerados
  no cliente (`expo-crypto` `randomUUID()`), `updatedAt` para conflito, campo de status de
  sync. Para sync pronto, avaliar PowerSync / ElectricSQL / WatermelonDB.
- Mutations do Query ficam pausadas offline e retomam sozinhas (`onlineManager`).

## 10. Formulários

Tudo em `formularios.md`: schema de formulário, `FormInput`, props de teclado, 422 nos
campos, máscaras e validadores brasileiros, etapas, edição.

## 11. Contrato gerado por OpenAPI

Quando o backend expõe `openapi.json`, os schemas DTO **não são escritos à mão**: são
gerados. Ver `contrato-openapi.md`. Mappers, services, hooks e schemas de formulário
continuam manuais.
