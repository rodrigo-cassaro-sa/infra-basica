# Stack e decisões fixas — [NOME DO APP]

> Fonte da verdade para humanos e IA. Todo código gerado segue este arquivo.
> Mudou uma decisão? Atualize aqui no mesmo commit.

## Plataforma
- Expo SDK: [57]  ·  React Native: [0.86]  ·  Node: [LTS]
- Execução em dev: [Development Build | Expo Go]
- Plataformas: [Android, iOS, Web]
- Rotas: `src/app`  ·  Alias: `@/*` → `./src/*`

## Decisões
| Área | Escolha | Observação |
|---|---|---|
| Navegação | Expo Router | typed routes; `Stack.Protected` para auth |
| Dados remotos | TanStack Query v5 | keys em `features/<f>/query-keys.ts` |
| HTTP | `src/services/api/api-client.ts` | único ponto de fetch; valida com Zod |
| Contrato | [openapi.json gerado | docs/contratos-de-api.md manual] | ver `contrato-openapi.md` da skill |
| Validação | Zod 4 | tipos via `z.infer` |
| Formulários | React Hook Form | `zodResolver` |
| Estado global | Zustand (`src/stores`) | só estado de cliente: `session-store`, `preferences-store` |
| Tokens | expo-secure-store | web: cookie httpOnly |
| Offline | [nenhum | cache persistido | expo-sqlite + sync] | decidir no início |
| UI | componentes próprios em `components/ui` [+ @expo/ui] | design system em `docs/guia-visual.md` |
| Tema / identidade | `tokens/tokens.json` → `src/theme/tokens.ts` (build-tokens.py da skill ux-ui) | tema padrão: [escuro | claro]; fonte: [nome] |
| Idioma | [só pt-BR (Intl em utils/format.ts) | multi-idioma: i18next + expo-localization] | idiomas: [pt-BR, …] |
| Listas longas | [FlatList | FlashList — motivo medido: …] | |
| Ícones | [@react-native-vector-icons/...] | |
| Testes | jest-expo + RNTL; Maestro E2E | |
| Monitoramento | [Sentry | EAS Observe] | |

## Convenções
- Idioma do código: [português | inglês]
- Arquivos: `kebab-case` (`user-card.tsx`); componentes `PascalCase`; hooks `use-*`
- Organização por feature: `src/features/<f>/{components,hooks,services,schemas,types,utils,screens}`
- Commits: conventional commits

## Backend
- Stack: [Node + Fastify | Django | FastAPI] + PostgreSQL, self-hosted (Docker Compose + Caddy/Traefik)
- URL por ambiente: DEV [..] · HOM [..] · PROD [..]
- Autenticação: [JWT access + refresh | cookie httpOnly]
- Formato de erro: `{ "code": "STRING", "message": "texto", "fieldErrors": { "campo": ["msg"] } }`

## Proibido
- Segredos no app (inclui `EXPO_PUBLIC_*` com chave privada)
- `fetch` fora de `services/`
- `any` sem justificativa
- Instalar lib sem `npx expo install` e sem registrar aqui
