# Arquitetura

## Sumário
1. Estrutura de pastas
2. Padrão de feature
3. Fluxo de dados
4. Rotas (Expo Router)
5. Código por plataforma
6. Visão geral do sistema

---

## 1. Estrutura de pastas

`src/app` contém **apenas rotas**. Todo o resto fica fora dela.

Template do SDK 55+ já nasce com `src/app` e alias `@/*` → `./src/*`. Projeto antigo com
`app/` na raiz: migre para `src/app` antes de crescer — nunca mantenha as duas pastas.

```text
meu-app/
├── src/
│   ├── app/                      # rotas (Expo Router) — só arquivos finos
│   │   ├── _layout.tsx           # providers globais (QueryClient, tema, auth)
│   │   ├── index.tsx             # redireciona conforme sessão
│   │   ├── (auth)/               # grupo público
│   │   │   ├── _layout.tsx
│   │   │   ├── login.tsx
│   │   │   ├── cadastro.tsx
│   │   │   └── recuperar-senha.tsx
│   │   └── (app)/                # grupo autenticado
│   │       ├── _layout.tsx       # layout do grupo logado (tabs/stack); guarda fica no _layout raiz
│   │       ├── home.tsx
│   │       ├── perfil.tsx
│   │       └── usuarios/
│   │           ├── index.tsx
│   │           └── [id].tsx
│   │
│   ├── features/                 # regras de negócio por domínio
│   │   ├── auth/
│   │   └── users/
│   │
│   ├── components/               # componentes genéricos, sem regra de negócio
│   │   ├── ui/                   # Screen, Button, Input, Card, Text...
│   │   ├── forms/                # FormInput ligado ao React Hook Form
│   │   └── feedback/             # LoadingView, EmptyState, ErrorState, OfflineState
│   │
│   ├── services/
│   │   ├── api/                  # api-client.ts, errors.ts, query-client.ts
│   │   └── storage/              # token-storage.ts
│   │
│   ├── stores/                   # session-store.ts, preferences-store.ts (Zustand)
│   ├── hooks/                    # hooks genéricos (use-online, use-debounce)
│   ├── utils/                    # puros: format.ts (Intl), validators-br.ts
│   ├── constants/                # constantes nomeadas (MAX_LOGIN_ATTEMPTS...)
│   ├── config/                   # env.ts (leitura e validação das env vars)
│   ├── i18n/                     # só se multi-idioma (ux-ui/references/i18n.md)
│   ├── test-utils/               # render com providers (testes.md)
│   └── theme/                    # index.ts (useTheme) + tokens.ts (GERADO do tokens.json)
│
├── assets/                       # imagens, fontes
├── tokens/tokens.json            # fonte dos tokens visuais (identidade do app)
├── docs/                         # só se o repo for só do app; em monorepo os docs ficam em ../docs
│                                 # (histórias, contratos, telas, guia visual, stack.md, rotas.md)
├── .maestro/                     # fluxos E2E
├── app.config.ts                 # config dinâmica (variantes dev/preview/prod)
├── eas.json
├── tsconfig.json
└── package.json
```

Regra para decidir entre `components/` e `features/<f>/components/`: se o componente
conhece um conceito de negócio (aluno, campanha, pedido), ele pertence à feature. Se não
conhece nada de negócio (botão, card, input), vai para `components/ui`.

## 2. Padrão de feature

```text
features/users/
├── components/
│   ├── user-card.tsx
│   └── user-form.tsx
├── hooks/
│   ├── use-users.ts            # useQuery lista
│   ├── use-user.ts             # useQuery detalhe
│   └── use-save-user.ts        # useMutation + invalidação
├── services/
│   └── user-service.ts         # chama apiClient com schema
├── schemas/
│   └── user-schema.ts          # DTO schema (API) + form schema
├── types/
│   └── user-types.ts           # z.infer + tipos de modelo
├── utils/
│   ├── user-mapper.ts          # DTO → modelo
│   └── user-rules.ts           # regras puras (canEdit, isEligible...)
├── screens/
│   ├── user-list-screen.tsx
│   ├── user-detail-screen.tsx
│   └── user-edit-screen.tsx
├── query-keys.ts               # userKeys.all / list / detail
└── index.ts                    # API pública da feature (o que outras podem importar)
```

Outras features importam **só pelo `index.ts`**. Isso evita que `campaigns` dependa de
arquivos internos de `users`.

Não crie pasta vazia por obrigação: feature pequena pode ter só `services`, `schemas` e
`screens`. A estrutura acima é o teto, não o piso.

## 3. Fluxo de dados

Ida:
```text
Route (src/app) → Screen → Hook (TanStack Query) → Service → apiClient → HTTPS
```

Volta:
```text
JSON → Zod (DTO) → mapper → modelo → cache do Query → Hook → Screen → Componente
```

Camadas só conhecem a vizinha seguinte. A screen não sabe que existe URL; o service não
sabe que existe tela.

## 4. Rotas (Expo Router)

Rota fina:

```tsx
// src/app/(app)/usuarios/[id].tsx
import { useLocalSearchParams } from "expo-router";
import { UserDetailScreen } from "@/features/users";

export default function UserDetailRoute() {
  const { id } = useLocalSearchParams<{ id: string }>();
  return <UserDetailScreen userId={id} />;
}
```

- Grupos `(nome)` organizam sem entrar na URL.
- Proteção de área autenticada: `Stack.Protected` no `src/app/_layout.tsx` guiado pelo `session-store` (template `root-layout.tsx`; ver `navegacao.md`). SDK sem `Stack.Protected`: `<Redirect href="/login" />` no `_layout.tsx` do grupo.
- Rotas viram deep links automaticamente (`meuapp://usuarios/123`). Defina `scheme` no `app.config.ts`.
- Parâmetros de rota são strings não confiáveis: valide com Zod se forem usados em regra.

## 5. Código por plataforma

Quando a diferença justificar, use extensões: `component.tsx`, `component.ios.tsx`,
`component.android.tsx`, `component.web.tsx`. Para diferenças pequenas, `Platform.OS`
ou `Platform.select` bastam. Não duplique arquivo por causa de uma linha.

Diferenças que quase sempre exigem tratamento na Web:
- `expo-secure-store` não funciona → usar adaptador de `token-storage`.
- Permissões nativas (câmera, notificações) têm API diferente ou inexistente.
- `Alert.alert` com botões tem suporte limitado → prefira modal próprio.

## 6. Visão geral do sistema

```text
                 APP (Expo: Android / iOS / Web)
                            │
          Expo Router → Screens → Hooks → Services
                            │
                  TanStack Query + apiClient
                            │  HTTPS / JSON (contrato)
                            ▼
      Backend self-hosted (Fastify | Django | FastAPI)
                            │
                        PostgreSQL
                  ┌─────────┼─────────┐
                Redis     MinIO    IA / agentes
                            │
          Docker Compose + Caddy/Traefik em VPS
```

Cada camada conhece só o necessário da seguinte. É isso que permite trocar
Django → Fastify, ou Postgres → outro banco, sem reescrever o app.
