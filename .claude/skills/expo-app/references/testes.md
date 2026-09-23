# Testes

## Sumário
1. O que testar (e o que não)
2. Setup (jest-expo + RNTL)
3. Mocks padrão
4. Render com providers
5. Onde mockar a API
6. Como escrever teste de tela
7. Exemplos por tipo
8. E2E com Maestro
9. Regras de manutenção

---

## 1. O que testar (e o que não)

Teste **comportamento que o usuário vê** e **regra de negócio**, não detalhe de
implementação. Teste que quebra quando você renomeia uma variável ensina a ignorar teste vermelho.

| Camada | Ferramenta | Testar | Custo |
|---|---|---|---|
| Regras (`*-rules.ts`), mappers, schemas, validadores | Jest | sempre (DoD) | muito baixo |
| Hooks de dados com lógica (otimista, invalidação) | Jest + TanStack Query | quando houver lógica | baixo |
| Telas e componentes | RNTL | formulário principal, lista com estados, login | médio |
| Jornada no app real | Maestro | 3 a 8 fluxos críticos | alto |

**Não vale testar:** componente só visual, estilo, snapshot de tela inteira (quebra a cada
ajuste e ninguém lê o diff), lib de terceiros, o próprio TanStack Query ou Zod.

Mínimo por projeto de cliente: regras + mappers + validadores, formulário principal, login e
2–3 fluxos Maestro.

## 2. Setup (jest-expo + RNTL)

```bash
npx expo install -- --save-dev jest-expo jest @types/jest @testing-library/react-native
```

```json
// package.json
{
  "scripts": {
    "test": "jest --watchAll=false",
    "test:watch": "jest --watch",
    "test:ci": "jest --ci --coverage"
  },
  "jest": {
    "preset": "jest-expo",
    "setupFilesAfterEnv": ["<rootDir>/jest.setup.ts"],
    "moduleNameMapper": { "^@/(.*)$": "<rootDir>/src/$1" },
    "testPathIgnorePatterns": ["/node_modules/", "/.maestro/"]
  }
}
```

O RNTL v13+ já traz os matchers (`toBeVisible`, `toHaveTextContent`, `toBeDisabled`).
Não instale `@testing-library/jest-native` (descontinuado).

## 3. Mocks padrão

Módulos nativos são mockados **uma vez**, em `jest.setup.ts`. Nenhum teste repete esses mocks.

```ts
// jest.setup.ts
import mockAsyncStorage from "@react-native-async-storage/async-storage/jest/async-storage-mock";

jest.mock("@react-native-async-storage/async-storage", () => mockAsyncStorage);

jest.mock("expo-secure-store", () => {
  const store = new Map<string, string>();
  return {
    getItemAsync: jest.fn(async (k: string) => store.get(k) ?? null),
    setItemAsync: jest.fn(async (k: string, v: string) => void store.set(k, v)),
    deleteItemAsync: jest.fn(async (k: string) => void store.delete(k)),
  };
});

jest.mock("@react-native-community/netinfo", () => ({
  addEventListener: jest.fn(() => jest.fn()),
  fetch: jest.fn(async () => ({ isConnected: true })),
}));

// só se o projeto usa react-native-keyboard-controller:
// jest.mock("react-native-keyboard-controller", () => require("react-native-keyboard-controller/jest"));

process.env.EXPO_PUBLIC_API_URL = "https://api.teste.local";
process.env.EXPO_PUBLIC_APP_ENV = "development";
```

## 4. Render com providers

Cada teste recebe um `QueryClient` **novo** e **sem retry**: reaproveitar vaza cache entre
testes; retry ligado faz teste de erro demorar segundos.

```tsx
// src/test-utils/render.tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, type RenderOptions } from "@testing-library/react-native";
import type { ReactElement, ReactNode } from "react";

export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: Infinity }, mutations: { retry: false } },
  });
}

export function createWrapper(queryClient = createTestQueryClient()) {
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

export function renderWithProviders(ui: ReactElement, options?: RenderOptions) {
  const queryClient = createTestQueryClient();
  return { queryClient, ...render(ui, { wrapper: createWrapper(queryClient), ...options }) };
}

export * from "@testing-library/react-native";
```

Stores Zustand são singletons: resete no `beforeEach` (`useSessionStore.setState({ status: "unauthenticated", user: null })`).

## 5. Onde mockar a API

- Teste de **tela/hook**: mocke o **service da feature** (`jest.mock("../services/student-service")`).
  Simples, e o teste não fica acoplado a URL e header.
- Teste do **`api-client.ts`** (refresh, erros tipados, contrato): mocke `global.fetch`.

Nunca mocke o hook da feature para testar a tela que usa esse hook — aí você testa o mock.

## 6. Como escrever teste de tela

Busque como o usuário encontra, nesta ordem:
1. `getByRole("button", { name: "Cadastrar aluno" })`
2. `getByLabelText("WhatsApp")`
3. `getByText("Nenhum aluno ainda")`
4. `getByTestId(...)` só sem texto nem rótulo (ícone)

Se a busca por papel/rótulo não acha, geralmente é falha de acessibilidade: corrija a tela.
Use `userEvent` (digitação e toque reais), não `fireEvent`. Esperas com `findBy*`/`waitFor`,
nunca `setTimeout`.

## 7. Exemplos por tipo

### Regra pura e mapper
```ts
// src/features/students/utils/student-rules.test.ts
import { canEnroll } from "./student-rules";

describe("RN-03 canEnroll", () => {
  it("bloqueia aluno inativo", () => expect(canEnroll({ ...baseStudent, active: false })).toBe(false));
});
```

### Lista com estados
```tsx
import { ServerError } from "@/services/api/errors";
import { renderWithProviders, screen, userEvent } from "@/test-utils/render";

import { StudentListScreen } from "../screens/student-list-screen";
import * as service from "../services/student-service";

jest.mock("../services/student-service");
jest.mock("expo-router", () => ({ router: { push: jest.fn() } }));
const mocked = jest.mocked(service);
const student = { id: "1", name: "Ana Souza", phone: "14999998888", active: true };

it("mostra os alunos", async () => {
  mocked.getStudentList.mockResolvedValue([student]);
  renderWithProviders(<StudentListScreen />);
  expect(await screen.findByText("Ana Souza")).toBeVisible();
});

it("erro com tentar novamente", async () => {
  mocked.getStudentList.mockRejectedValueOnce(new ServerError("x", 500)).mockResolvedValue([student]);
  renderWithProviders(<StudentListScreen />);
  await userEvent.setup().press(await screen.findByRole("button", { name: "Tentar novamente" }));
  expect(await screen.findByText("Ana Souza")).toBeVisible();
});
```

### Formulário: sucesso e 422
```tsx
import { ValidationError } from "@/services/api/errors";

jest.mock("expo-router", () => ({ router: { back: jest.fn() } }));

it("mostra erro do servidor no campo", async () => {
  const user = userEvent.setup();
  mocked.createStudent.mockRejectedValue(new ValidationError("x", { phone: ["WhatsApp já cadastrado"] }));
  renderWithProviders(<StudentCreateScreen />);

  await user.type(screen.getByLabelText("Nome completo"), "Ana Souza");
  await user.type(screen.getByLabelText("WhatsApp"), "14999998888");
  await user.press(screen.getByRole("button", { name: "Cadastrar aluno" }));

  expect(await screen.findByText("WhatsApp já cadastrado")).toBeVisible();
});

it("envia sem máscara", async () => {
  // ... preencher e enviar
  await waitFor(() => expect(mocked.createStudent).toHaveBeenCalledWith(expect.objectContaining({ phone: "14999998888" })));
});
```

### Hook com atualização otimista
```tsx
import { act, renderHook, waitFor } from "@testing-library/react-native";

import { createTestQueryClient, createWrapper } from "@/test-utils/render";

it("restaura a lista se a remoção falhar", async () => {
  const queryClient = createTestQueryClient();
  queryClient.setQueryData(studentKeys.list(), [student]);
  mocked.deleteStudent.mockRejectedValue(new Error("falhou"));
  mocked.getStudentList.mockResolvedValue([student]);

  const { result } = renderHook(() => useDeleteStudent(), { wrapper: createWrapper(queryClient) });
  act(() => result.current.mutate("1"));

  await waitFor(() => expect(result.current.isError).toBe(true));
  expect(queryClient.getQueryData(studentKeys.list())).toEqual([student]);
});
```

### api-client: um único refresh para várias chamadas
```ts
import { z } from "zod";

import { apiClient } from "@/services/api/api-client";
import { tokenStorage } from "@/services/storage/token-storage";

const ok = (status: number, body: unknown) =>
  ({ ok: status < 400, status, headers: new Headers(), json: async () => body }) as unknown as Response;

it("faz refresh uma vez só", async () => {
  await tokenStorage.setTokens({ accessToken: "velho", refreshToken: "r1" });
  global.fetch = jest.fn(async (url: RequestInfo | URL, init?: RequestInit) => {
    if (String(url).endsWith("/auth/refresh")) return ok(200, { accessToken: "novo", refreshToken: "r2" });
    const auth = (init?.headers as Record<string, string>).Authorization;
    return auth === "Bearer novo" ? ok(200, { ok: true }) : ok(401, {});
  }) as typeof fetch;

  const schema = z.object({ ok: z.boolean() });
  await Promise.all([apiClient.get("/a", schema), apiClient.get("/b", schema), apiClient.get("/c", schema)]);

  const refreshes = jest.mocked(global.fetch).mock.calls.filter(([u]) => String(u).endsWith("/auth/refresh"));
  expect(refreshes).toHaveLength(1);
});
```

### Guarda de rota
```tsx
import { renderRouter, screen } from "expo-router/testing-library";

it("deslogado cai no login", async () => {
  useSessionStore.setState({ status: "unauthenticated", user: null });
  renderRouter("./src/app");
  expect(await screen.findByRole("button", { name: "Entrar" })).toBeVisible();
});
```

## 8. E2E com Maestro

Maestro controla o app instalado (emulador, simulador ou aparelho) com fluxos YAML.

```bash
curl -Ls "https://get.maestro.mobile.dev" | bash
maestro studio            # clica no app e mostra o seletor de cada elemento
maestro test .maestro/    # roda todos os fluxos
```

- Teste o build **preview** (id `com.empresa.meuapp.preview`), não o dev client nem o Expo Go.
- Aponte o preview para um **backend de homologação** com usuário de teste fixo.
- Encontre elementos pelo texto visível; `testID` só em campo sem rótulo visível e ícone.
- Senha nunca no YAML versionado: `maestro test -e PASSWORD=$SENHA_TESTE .maestro/`.

```yaml
# .maestro/subflows/login.yaml
appId: com.empresa.meuapp.preview
---
- tapOn: "E-mail"
- inputText: ${EMAIL}
- tapOn: "Senha"
- inputText: ${PASSWORD}
- hideKeyboard
- tapOn: "Entrar"
```

```yaml
# .maestro/login.yaml
appId: com.empresa.meuapp.preview
env:
  EMAIL: teste@empresa.com.br
---
- launchApp:
    clearState: true   # apaga dados e SecureStore: todo fluxo começa deslogado
- runFlow: subflows/login.yaml
- assertVisible: "Início"
```

Fluxos que valem: login (sucesso e erro), ação principal do produto, cadastro principal,
logout (volta ao login sem dados do usuário anterior). Na nuvem: EAS Workflows (job de
Maestro) ou Maestro Cloud — confira a sintaxe atual na documentação.

## 9. Regras de manutenção

- **Bug corrigido ganha teste** que falharia sem a correção.
- Nome do teste descreve comportamento (`"desabilita o botão enquanto salva"`); regra cita o ID (`RN-03`).
- Teste instável (flaky) é corrigido ou apagado na hora.
- Cobertura é termômetro, não meta.
- `npm run test:ci` no CI (`qualidade.md` §4); PR vermelho não gera update OTA.
