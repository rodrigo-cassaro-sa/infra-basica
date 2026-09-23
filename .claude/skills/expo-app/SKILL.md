---
name: expo-app
description: >-
  Padrão único da casa para apps Expo + React Native + TypeScript (Android, iOS e Web com uma
  base de código), backend desacoplado via contrato HTTP/OpenAPI. Cobre arquitetura por
  feature, Expo Router, TanStack Query, Zod, formulários (RHF, máscaras e validadores BR),
  login/sessão/biometria, segurança, tema a partir de tokens, performance (FlashList,
  expo-image), testes (jest-expo, RNTL, Maestro), EAS Build/Update/Submit, lojas e Web. Use
  SEMPRE que o usuário mencionar Expo, React Native, EAS, app Android/iOS, "aplicativo",
  "tela do app", cadastro, login, listagem, formulário, teste, OTA, Play Store/App Store,
  ou pedir para gerar, revisar ou continuar código de app — mesmo sem dizer "Expo". Também
  para código a partir de história, mapa de telas, contrato ou Spec Kit. Use junto com a
  skill ux-ui ao criar telas. É a ÚNICA stack de frontend da casa: painel web, sistema
  administrativo, site com SEO e componentes DOM ("use dom") também são feitos aqui.
---

# Expo App — padrão da casa

Todo projeto sai com a mesma arquitetura: qualquer pessoa (ou IA) abre o repositório e
sabe onde cada coisa está. Consistência vale mais que a "melhor lib do momento".

Prioridade, nesta ordem — nunca inverta:
**correto → claro → simples → testável → desacoplado → reutilizável → performático → sofisticado.**

## Passo 0 — Situar o projeto (sempre)

Antes de gerar código, descubra (lendo arquivos; pergunte só o que faltar):

1. **`docs/stack.md`, `AGENTS.md`, `CLAUDE.md`**: se existirem, valem **acima desta skill**.
2. **SDK**: `package.json` → `expo`. Sem projeto: SDK estável mais recente.
3. **Execução**: Expo Go ou Development Build (muda quais libs podem entrar).
4. **Rotas**: `src/app/` (SDK 55+). Projeto antigo com `app/` → migrar, nunca misturar.
5. **Backend e contrato**: qual API, se publica `openapi.json` ou se o contrato é manual.
6. **Docs de feature**: `docs/` (história, regras, mapa de telas) ou specs do Spec Kit.
7. **Identidade visual**: `docs/guia-visual.md` + `tokens/tokens.json` (skill `ux-ui`). Sem
   eles, proponha criar antes de gerar telas — é o que dá a cara de cada app sem quebrar o padrão.

Assunto de versão, lib nova, erro de build ou upgrade → leia
`references/estado-atual-2026.md` **e confirme na web** (docs.expo.dev / expo.dev/changelog).
O Expo lança SDK a cada poucos meses; o conhecimento envelhece rápido.

## Stack padrão (fixa)

| Camada | Escolha |
|---|---|
| Linguagem | TypeScript `strict` + `noUncheckedIndexedAccess` (sem `any`) |
| Framework | Expo (SDK atual) + React Native, New Architecture |
| Navegação | Expo Router (`src/app`, typed routes, `Stack.Protected`) |
| Dados do servidor | TanStack Query v5 |
| HTTP | `fetch` via `src/services/api/api-client.ts` (único ponto; valida com Zod; refresh único) |
| Contrato | OpenAPI → schemas Zod gerados (backend próprio) · manual em `docs/contratos-de-api.md` (low-code) |
| Validação | Zod 4 (`z.email()`, `z.iso.datetime()`, `z.infer`) |
| Formulários | React Hook Form + `@hookform/resolvers/zod` |
| Tokens | `expo-secure-store` no mobile · cookie `httpOnly` na Web |
| Estado global | Zustand em `src/stores` (`session-store`, `preferences-store`) |
| Tema | `tokens/tokens.json` → `src/theme/tokens.ts` (gerado) → `useTheme()` |
| Dados locais | `expo-sqlite` (offline real) · kv-store/AsyncStorage (preferências, nunca token) |
| Imagens / listas | `expo-image` · `FlatList` → `FlashList` só com problema medido |
| Ícones | `@react-native-vector-icons/*` (`@expo/vector-icons` deprecado no SDK 56) |
| Qualidade | `npx expo lint` + Prettier · `jest-expo` + RNTL · Maestro E2E |
| Idioma | pt-BR com `Intl` (`utils/format.ts`) · multi-idioma: i18next + expo-localization (`ux-ui`) |
| Entrega | EAS Build / Submit / Update · Web: `npx expo export --platform web` |
| Backend | Self-hosted (Node + Fastify ou Django/FastAPI) + PostgreSQL, Docker Compose, Caddy/Traefik. **Sem BaaS gerenciado** salvo pedido explícito |

Instale **sempre** com `npx expo install <pacote>` (escolhe versão compatível com o SDK).
Depois de mexer em dependências: `npx expo install --fix` e `npx expo-doctor@latest`.

## Fluxos

### A) Projeto novo
1. `npx create-expo-app@latest <nome>` (SDK mais recente) e entre na pasta.
2. `bash <skill>/scripts/scaffold-project.sh . --install` — cria a estrutura, copia
   templates (api client, erros, query client, token storage, env, tema, Screen, feedback,
   FormInput, app.config, eas.json, CI, docs) sem sobrescrever nada.
3. Ajuste `app.config.ts`, revise `tsconfig.json` e `_layout.tsx`, preencha `docs/stack.md`.
4. Dev build desde o início: `eas init` → `eas build --profile development --platform android`.
5. Checagem: `npx tsc --noEmit`, `npx expo lint`, `npx expo-doctor@latest`.

### B) Feature nova
1. Leia os docs da feature (Histórias, `contratos-de-api.md`, `mapa-de-telas.md`, regras;
   ou Spec Kit) — a feature nasce do contrato, não do código. Os docs são produzidos pelas
   skills `dah-historia` e `dah-documentacao`; em monorepo ficam em `../docs`
   (`references/documentacao-por-historia.md`).
2. Esqueleto: `bash <skill>/scripts/scaffold-feature.sh <feature-kebab> <Entidade>`.
3. Preencha na ordem: **contrato → schema Zod (gerado ou manual) → types → mapper →
   service → query keys + hooks → componentes → screen → rota fina**.
4. Estados de tela, teclado e safe area.
5. Teste (regras puras e mapper no mínimo) e feche com a Definition of Done.

### C) Revisar / refatorar
Passe o código por "O que não fazer" e pela DoD. Para cada problema: arquivo, regra
violada e trecho corrigido — não só a crítica.

### D) Build, publicação e upgrade
`references/builds-eas.md` (ambientes, EAS, lojas, Web) e `references/qualidade.md`
(upgrade de SDK, checklist de release).

## Regras inegociáveis

O "porquê" está entre parênteses — use-o para julgar casos que as regras não cobrem.

1. **Rota é fina.** `src/app` só importa e renderiza a screen da feature. (Trocar rota não quebra lógica.)
2. **Screen organiza, não calcula.** Sem `fetch`, sem regra no JSX. (Tela gigante não se testa nem a IA edita com segurança.)
3. **Nenhum `fetch` fora de `services/`.** Tudo passa pelo `apiClient`. (URL, token, erro e refresh num lugar só.)
4. **Dado externo é `unknown` até passar pelo Zod.** (TS não checa a rede em runtime.)
5. **DTO ≠ modelo.** `snake_case` da API vira modelo de UI no mapper. (Mudança no backend fica num arquivo.)
6. **Dado de servidor vive no TanStack Query**, nunca em `useState` ou store.
7. **Sem estado derivado nem `useEffect` para calcular.** `useEffect` só sincroniza com sistema externo.
8. **Sem `any`**, `as` para calar compilador ou `@ts-ignore` sem justificativa.
9. **Nenhum segredo no app.** Tudo `EXPO_PUBLIC_*` é público. App → seu backend → serviço. Nunca app → banco, nunca token admin de NocoDB/BaaS/webhook no app.
10. **Token em armazenamento seguro.** SecureStore no mobile; na Web, cookie `httpOnly` (adaptador em `token-storage.ts`). Nunca AsyncStorage/localStorage.
11. **Toda tela assíncrona trata 5 estados:** loading, vazio, sucesso, erro, sem rede (`components/feedback`).
12. **Listas longas com `FlatList`**, nunca `ScrollView` + `.map()`.
13. **Nada de cor/número mágico.** Visual só via `useTheme()` (tokens gerados do `tokens.json`); números em `src/constants`.
14. **Backend é a autoridade.** Validação e permissão no app são UX; esconder botão não é autorização.
15. **Mensagem técnica nunca chega ao usuário.** Erro tipado → `getUserMessage` → texto amigável; detalhe vai para log sem token/senha/CPF.
16. **Safe area e teclado** em toda tela: use o `Screen` padrão. Alvo de toque ≥ 48 (`MIN_TOUCH_TARGET`).
17. **Não abstraia cedo; não otimize sem medir.** Com React Compiler ativo, nada de `useMemo`/`useCallback`/`memo` manual sem motivo medido.

## Onde está cada coisa

| Pergunta | Resposta |
|---|---|
| Rota | `src/app/...` (só importa a screen) |
| Tela | `src/features/<f>/screens/` |
| Regra de negócio | `src/features/<f>/utils/<x>-rules.ts` (função pura com teste) |
| Tipo | `src/features/<f>/types/` (preferir `z.infer`) |
| Validação / DTO | `src/features/<f>/schemas/` (reexporta de `services/api/generated/` se OpenAPI) |
| Chamada da API | `src/features/<f>/services/` → `src/services/api/api-client.ts` |
| Estado | local `useState`/`useReducer` · servidor: hook + Query · global: `src/stores` |
| Visual (cor, fonte, espaço) | `tokens/tokens.json` → `src/theme` · decisões em `docs/guia-visual.md` |
| Componente | de negócio: `features/<f>/components/` · genérico: `src/components/ui/` |
| Teste | ao lado do arquivo (`*.test.ts(x)`) |
| Decisões do projeto | `docs/stack.md` |

Se alguma resposta for "espalhado", a arquitetura está degradando — corrija antes de seguir.

## Nomes e convenções

- Arquivos `kebab-case` (`user-card.tsx`, `use-users.ts`, `user-service.ts`); componentes
  `PascalCase`; hooks `use*`; booleanos como pergunta (`isLoading`, `canEdit`).
- Query keys por feature em `query-keys.ts` (`userKeys.all`, `userKeys.detail(id)`).
- Outras features importam só pelo `index.ts` da feature.
- Imports absolutos `@/` → `src/`.
- Commits `feat:`/`fix:`/`refactor:`/`test:`/`chore:`/`docs:`; branches `main`, `feature/*`, `fix/*`.

## Expo Go × Development Build

- **Expo Go**: aprender e prototipar UI. Só libs embutidas e um SDK por versão (as lojas
  podem estar atrás do SDK atual — ver `estado-atual-2026.md`).
- **Development Build**: todo projeto profissional, desde o início. Obrigatório para lib
  nativa, push, biometria, config plugins ou SDK mais novo que o Expo Go da loja.

Antes de sugerir uma lib, verifique se roda no Expo Go e na Web (reactnative.directory).
Se exigir dev build, **avise explicitamente**.

## Mapa de referências — leia só o necessário

| Quando | Leia |
|---|---|
| Versões, SDK, Expo Go, breaking changes | `references/estado-atual-2026.md` |
| Pastas, padrão de feature, fluxo de dados, código por plataforma | `references/arquitetura.md` |
| Rotas, layouts, auth guard, tabs, modais, params, deep links | `references/navegacao.md` |
| API client, erros, Zod, DTO/mapper, Query, mutation otimista, busca, paginação, offline | `references/dados-e-api.md` |
| Formulários, teclado, 422 nos campos, máscaras, etapas, edição | `references/formularios.md` |
| CPF, CNPJ, telefone, CEP, moeda (validadores e máscaras prontos) | `references/validadores-br.md` |
| Backend com OpenAPI, geração de schemas, divergência de contrato | `references/contrato-openapi.md` |
| Componentes, estado, hooks, regras de negócio, naming | `references/padroes-de-codigo.md` |
| Tema/tokens/identidade, componentes base, estados de tela, listas, a11y, Web | `references/ui-e-design-system.md` |
| Lentidão, FlatList × FlashList, memo, expo-image, re-render | `references/performance.md` |
| Sessão (login/logout/refresh), guarda de rota, OAuth, biometria, permissões, logs, LGPD | `references/seguranca.md` |
| Dev build, eas.json, variantes, env, EAS Update (OTA), CI, Windows/iOS | `references/builds-eas.md` |
| Web: SEO, `+html.tsx`, layout desktop, hover/teclado, painel denso, componentes DOM, deploy | `references/web.md` |
| Contas das lojas, credenciais, primeira publicação, release | `references/publicacao-lojas.md` |
| Testes: setup, mocks, render, exemplos, Maestro | `references/testes.md` |
| Setup, CI, Git, dependências, upgrade, release, observabilidade | `references/qualidade.md` |
| Como consumir Histórias e docs DAH (RN, ENT, T, API), `docs/rotas.md`, Spec Kit/SDD, monorepo | `references/documentacao-por-historia.md` |

Templates em `assets/templates/` — cada `.ts/.tsx` traz `// DESTINO:` no topo. Adapte,
não reescreva do zero: api-client, errors, query-client, token-storage, env, theme + tokens,
Screen, Button, feedback, FormInput, format, stores (sessão, preferências), auth (schema,
service, types), root-layout, app.config, eas.json, CI, docs. Scripts:
`scripts/scaffold-project.sh`, `scripts/scaffold-feature.sh`.

Interface (o que a tela mostra, estados, textos, acessibilidade, i18n): skill **`ux-ui`**.
Esta skill decide onde e como isso vira código.

## Desenvolvimento assistido por IA

- Sem `docs/stack.md`? **Proponha criá-lo** (template em `assets/templates/docs/`) antes
  de gerar muitas telas — é o que mantém a IA consistente entre sessões.
- Projetos SDK 56+ nascem com `AGENTS.md`/`CLAUDE.md`: respeite e complemente.
- Nunca invente API de lib. Em dúvida, consulte `https://docs.expo.dev/versions/latest/`.
- Para upgrade de SDK, a skill oficial `upgrading-expo` (`expo/skills`) complementa esta.

## O que não fazer

Componente com centenas de linhas · `any`/`as`/`@ts-ignore` para calar · `fetch` em tela ·
regra no JSX · store como banco improvisado · `useEffect` para derivar ou buscar dados ·
token em AsyncStorage · segredo no app · log de dado sensível · ignorar loading/vazio/erro/offline ·
`ScrollView` com lista grande · cor e número mágicos · `npm install` em pacote Expo ·
lib para 5 linhas · `memo` em tudo sem medir · pedir todas as permissões na abertura ·
app falando direto com banco · desenvolver sem contrato · editar `services/api/generated/`
à mão · função de 3 linhas espalhada em 5 arquivos ("separe responsabilidades, não linhas").

## Definition of Done

- [ ] Regra de negócio isolada em função pura, com teste (ID RN-xx no nome)
- [ ] `npx tsc --noEmit` e `npx expo lint` limpos
- [ ] Loading, vazio, erro e sem-rede tratados, com textos reais (microcopy da `ux-ui`)
- [ ] Validação no form (Zod) **e** no backend; autorização no backend
- [ ] UI com componentes base e tokens; `Screen` com safe area e teclado
- [ ] Acessibilidade: role/label nos interativos, toque ≥ 48 (checklist de QA da `ux-ui`)
- [ ] Testado em Android físico · iOS testado ou planejado · Web conferida quando aplicável
- [ ] Sem segredo no código, sem log sensível
- [ ] Schemas batem com o contrato (OpenAPI regenerado ou `contratos-de-api.md`)
- [ ] Docs atualizados (`stack.md` se entrou lib nova)
- [ ] Commit pequeno no padrão convencional

## Formato de entrega

- Arquivos completos com caminho no topo (`// src/features/...`), na ordem do fluxo B,
  prontos para colar. Nunca pseudo-código, nunca só a tela.
- Comandos exatos (`npx expo install ...`) quando houver dependência nova.
- No fim, o que falta para bater a DoD, se algo ficou de fora.
