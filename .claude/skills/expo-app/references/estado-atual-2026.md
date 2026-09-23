# Estado atual do ecossistema Expo (snapshot: setembro/2026)

> Isto é um retrato datado. Antes de afirmar versões ao usuário, confirme em
> https://expo.dev/changelog e https://docs.expo.dev/versions/latest/ .
> Se a data atual estiver muito à frente de set/2026, trate tudo aqui como provavelmente desatualizado.

## Versões

| SDK | Lançamento | React Native | React | Observação |
|---|---|---|---|---|
| 54 | set/2025 | 0.81 | 19.1 | Última com Legacy Architecture. Versão do Expo Go nas lojas (set/2026). Recebe correções críticas até o SDK 58 sair. |
| 55 | fev/2026 | 0.83 | 19.2 | Só New Architecture. Template novo com `src/app`. Hermes v1 opt-in. |
| 56 | mai/2026 | 0.85 | 19.2 | Hermes v1 padrão. Expo Router sem React Navigation. `expo/fetch` global. Expo UI estável. TS 6. |
| 57 | jun/2026 | 0.86 | 19.2 | Release pequena e sem breaking changes. Use `expo@57.0.17+` (corrige regressão de memória do Hermes v1 com reanimated/worklets). |
| 58 | beta set/2026 | 0.88 (RC) | — | Feito para iOS 27 (ciclo de vida por UIScene). Estável previsto para set–out/2026. |

**Padrão para projeto novo hoje:** SDK estável mais recente (57, ou 58 quando sair) + Development Build.

Ciclo de vida: cada SDK recebe suporte por ~1 ano. O Expo está testando um ritmo novo: releases "grandes" intercaladas com releases pequenas sem breaking changes (como o 57).

## Expo Go — o ponto que mais confunde

- O Expo Go roda **apenas um SDK por versão do app**.
- Desde o SDK 55 houve atraso na aprovação das lojas: em set/2026 o Expo Go da App Store/Play Store ainda estava no **SDK 54**.
- Por isso o `create-expo-app` pergunta o SDK: "Latest" (para dev build) ou "SDK 54 para aprender com Expo Go".
- Para usar Expo Go com SDK novo:
  - Android (aparelho/emulador): o Expo CLI instala a versão certa automaticamente.
  - iOS físico: `eas go` gera um Expo Go da versão certa e sobe no TestFlight da sua conta.
  - iOS Simulator: Expo CLI instala.
- Recomendação oficial: Expo Go é ferramenta de aprendizado; app que vai para produção usa Development Build.

Consequência prática: **se o usuário quer testar no iPhone pelo Expo Go da loja, o projeto precisa ser SDK 54.** Caso contrário, dev build (ou `eas go`).

## Criação de projeto

```bash
npx create-expo-app@latest meu-app                          # pergunta o SDK
npx create-expo-app@latest meu-app --template default@sdk-57  # fixa o SDK
```

Template `default` (SDK 55+): Expo Router, TypeScript, `src/app`, Native Tabs, e (SDK 56+) `AGENTS.md`, `CLAUDE.md`, `.claude/settings.json`, Expo UI.
Flag `--no-agents-md` pula os arquivos de agente.

## Mudanças que quebram código antigo (e código gerado por IA com conhecimento velho)

1. **Legacy Architecture removida (SDK 55+)** — `newArchEnabled` não existe mais no app.json. Lib que não suporta New Architecture não funciona.
2. **`src/app` em vez de `app` (template SDK 55+)** — alias `@/*` aponta para `./src/*`.
3. **Expo Router não depende mais de React Navigation (SDK 56+)** — imports de `@react-navigation/*` junto com expo-router quebram. Use as APIs do próprio `expo-router`. Codemod:
   `npx expo-codemod sdk-56-expo-router-react-navigation-replace src`
   O `expo-doctor` avisa se os dois estiverem instalados.
4. **`expo/fetch` é o `globalThis.fetch` (SDK 56+)** — não precisa importar. Opt-out: `EXPO_PUBLIC_USE_RN_FETCH=1`.
5. **`@expo/vector-icons` deprecado (SDK 56)** — migrar para `@react-native-vector-icons/<set>` com `npx @react-native-vector-icons/codemod`. O pacote `expo` não o inclui mais.
6. **`expo-file-system`**: API nova (classes `File`/`Directory`) é padrão desde SDK 54; no 56 `copy()`/`move()` viraram assíncronos.
7. **`expo-calendar`, `expo-contacts`, `expo-media-library`**: APIs antigas deprecadas; novas são orientadas a objeto.
8. **iOS mínimo 16.4 e Xcode 26.4 (SDK 56+)**.
9. **Node.js ≥ 20.19.4** (RN 0.85+). Use Node LTS atual.
10. **`expo prebuild` limpa e regenera `android/` e `ios/` por padrão (SDK 57)** — use `--no-clean` para manter. Nunca edite as pastas nativas à mão se usa CNG; use config plugins.
11. **Hermes v1 é padrão (SDK 56+)**.
12. **iOS 27 exige ciclo de vida UIScene** — padrão no SDK 58; no 57 é opt-in via `expo-build-properties` (`ios.enableSceneSupport`). Quem customiza `AppDelegate.swift` precisa migrar.

## Novidades úteis

- **Expo UI** (`@expo/ui`) estável no SDK 56: componentes nativos SwiftUI/Jetpack Compose e componentes universais (`Host`, `Row`, `Column`, `TextInput`, `BottomSheet`...). Tem substitutos "drop-in" para `@gorhom/bottom-sheet`, datetimepicker, picker, slider etc. (`@expo/ui/community/...`).
- **Inline modules** (SDK 56): escrever módulo nativo Swift/Kotlin dentro do projeto.
- **Config plugins tipados**: importar de `expo-<pacote>/plugin` no `app.config.ts`.
- **Hermes bytecode diffing** no EAS Update: atualizações OTA bem menores (padrão no 56).
- **Expo Router**: `SuspenseFallback` exportável no `_layout`, SSR streaming na web (experimental), `Stack.Toolbar`.
- **Integração Convex** via `eas integrations:convex:connect`.
- **EAS Observe**: monitoramento de performance em produção (novo).
- **Skills oficiais** para agentes: Claude Code → `/plugin marketplace add expo/skills` e `/plugin install expo`; outros agentes → `npx skills add expo/skills`.
- **Expo MCP**: servidor MCP com docs e ferramentas do Expo.

## Como fazer upgrade de SDK

Um SDK por vez:

```bash
npx expo install expo@^57.0.0 --fix
npx expo-doctor@latest
```

Depois: ler "Breaking changes" do changelog; se usa CNG, apagar `android/` e `ios/`; gerar **novo development build**; testar em branch antes de mergear. Detalhes em `qualidade.md`.
