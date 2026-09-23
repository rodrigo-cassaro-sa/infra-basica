# Development Build, EAS e publicação

## Fases

```
Protótipo (Expo Go) → Development Build → Preview (testes internos) → Production (lojas)
```

Em projeto profissional, pule direto para Development Build assim que for instalar a primeira lib nativa ou definir o SDK acima do Expo Go da loja.

## Setup inicial

```bash
npm i -g eas-cli            # ou npx eas-cli@latest
eas login
eas init                    # vincula projeto (projectId no app config)
npx expo install expo-dev-client
eas build:configure         # cria eas.json
```

## eas.json de referência

Ver `assets/templates/eas.json`. Resumo:

- `development`: `developmentClient: true`, `distribution: "internal"`, `environment: "development"`. Android gera APK instalável direto.
- `development-simulator`: igual, com `ios.simulator: true` (para quem tem Mac).
- `preview`: `distribution: "internal"`, `environment: "preview"`, `channel: "preview"` — para homologação com testers.
- `production`: `environment: "production"`, `channel: "production"`, `autoIncrement: true`.
- `cli.appVersionSource: "remote"`: o EAS controla buildNumber/versionCode.

```bash
eas build --profile development --platform android
eas build --profile preview --platform all
eas build --profile production --platform all
```

Depois de instalar o dev build no aparelho: `npx expo start` (o app abre o servidor do seu computador).

Build local sem nuvem (precisa Android Studio / Xcode): `npx expo run:android`, `npx expo run:ios`, ou `eas build --local`.

## Várias variantes instaladas lado a lado

Três ambientes, três apps instaláveis lado a lado no mesmo aparelho:

| Variante | Nome | Bundle / package | API |
|---|---|---|---|
| development | MeuApp DEV | `com.empresa.meuapp.dev` | api-dev |
| preview | MeuApp PREVIEW | `com.empresa.meuapp.preview` | api-hom |
| production | MeuApp | `com.empresa.meuapp` | api |


Use `app.config.ts` com `APP_VARIANT` para mudar nome e bundle id por ambiente (ex.: `com.empresa.app.dev`, `.preview`). Template em `assets/templates/app.config.ts`. Defina `APP_VARIANT` como variável EAS em cada ambiente.

## Variáveis de ambiente no EAS

```bash
eas env:create --environment preview --name EXPO_PUBLIC_API_URL --value https://api-hom.exemplo.com --visibility plaintext
eas env:list --environment production
eas env:pull --environment development    # gera .env.local
```

- Cada profile do `eas.json` usa o conjunto de variáveis do seu `environment`. Coloque `.env*.local` no `.gitignore`.
- Visibilidade: `plaintext`, `sensitive`, `secret`. Mas lembre: se a variável é `EXPO_PUBLIC_*`, ela vai para o bundle — "secret" no EAS não a torna secreta no app. Segredos de verdade (ex.: token do Sentry para upload de sourcemap) ficam em variáveis sem `EXPO_PUBLIC_`, usadas só no build.
- Ambientes típicos: API DEV / HOM / PROD com URLs diferentes.

## CNG (Continuous Native Generation)

- Padrão recomendado: **não versionar `android/` e `ios/`**; eles são gerados por `npx expo prebuild` a partir do app config + config plugins.
- Customização nativa → config plugin (ou inline module no SDK 56+), nunca edição manual.
- SDK 57+: `prebuild` limpa as pastas por padrão.

## EAS Update (OTA)

```bash
npx expo install expo-updates
eas update:configure
eas update --channel preview --message "fix: corrige validação de CPF"
```

- Só atualiza JS/assets. Mudou código nativo, lib nativa ou SDK → precisa **novo build**.

| Vai por OTA | Exige build novo |
|---|---|
| texto, layout, regra em TS, correção de tela, troca de imagem/asset | instalar/atualizar lib nativa, permissões, ícone, splash, nome, bundle id, plugins do `app.config.ts`, SDK, **qualquer mudança em componente DOM (`"use dom"`)** |

Em dúvida se a mudança é nativa: `npx expo-doctor` e `eas fingerprint:compare`.

**Fluxo obrigatório**: todo update vai primeiro para `preview`, é testado em aparelho, e só
então para `production`. Update direto em produção sem teste é o jeito mais rápido de
quebrar o app de todos os usuários de uma vez. Deu problema: `eas update:rollback`.
- `runtimeVersion: { policy: "fingerprint" }` no app config: o EAS calcula compatibilidade nativa automaticamente e evita mandar update incompatível.
- Canais `preview` e `production` apontando para branches; faça rollout gradual (`--rollout-percentage`) em produção.
- Diffing de bytecode Hermes (SDK 56+) deixa updates bem menores.

## EAS Workflows (CI/CD)

Arquivos em `.eas/workflows/*.yml` automatizam: build em PR, update em merge na main, testes E2E com Maestro, submit. Alternativa: GitHub Actions chamando `eas-cli`.

Estratégia recomendada (automatize só depois que o fluxo manual estiver liso):
- **Pull request**: `typecheck → lint → test` (template `ci.yml`) + `eas update --channel preview` para testar a mudança no aparelho. Barato e rápido.
- **Tag `v*`**: `eas build --profile production --platform all --auto-submit --non-interactive`.
- Build completo em todo PR gasta cota de build à toa.

No GitHub Actions: `expo/expo-github-action` com o secret `EXPO_TOKEN` (expo.dev → Access tokens).

## Publicar nas lojas

```bash
eas submit --platform android --profile production
eas submit --platform ios --profile production
```

Contas, credenciais, o que as lojas pedem na primeira publicação e fluxo de release:
`publicacao-lojas.md`. Leia antes do primeiro envio de cada app.

## Web

`npx expo export -p web` gera `dist/` (padrão da casa: `web.output: "static"`). Deploy,
SEO, layout de desktop e componentes DOM: `web.md`.

## Windows e iOS

| No Windows | Pode? |
|---|---|
| Programar, rodar Metro, web | ✔ |
| Android emulador/aparelho | ✔ |
| Expo Go em iPhone | ✔ (se o SDK bater com o Expo Go instalado; senão `eas go`) |
| Build iOS na nuvem (EAS) e instalar dev build no iPhone | ✔ (registre o aparelho: `eas device:create`) |
| Xcode / iOS Simulator local | ✘ (precisa macOS) |

## Após qualquer upgrade de SDK ou lib nativa

Gere **novo development build**. Dev build antigo + JS novo = crash com erro de módulo nativo ausente.
