# Qualidade, testes e entrega

## Sumário
1. Setup inicial
2. Scripts do package.json
3. Testes
4. Lint, format e CI
5. Git e commits
6. Dependências
7. Ambientes, build e publicação
8. Upgrade de SDK
9. Checklist de release
10. Logging e observabilidade

---

## 1. Setup inicial

```bash
npx create-expo-app@latest meu-app
cd meu-app

# dados, validação, formulários
npx expo install @tanstack/react-query zod react-hook-form @hookform/resolvers
npx expo install @react-native-community/netinfo expo-secure-store expo-image expo-splash-screen
# estado global de cliente (sessão, preferências)
npx expo install zustand @react-native-async-storage/async-storage

# testes
npx expo install -- --save-dev jest-expo jest @types/jest @testing-library/react-native

# lint (gera configuração ESLint do Expo)
npx expo lint
```

Depois rode `scripts/scaffold-project.sh` (copia os templates) e crie `.env` a partir de `env.example`.
Rode `npx expo-doctor` para conferir compatibilidade de versões.

## 2. Scripts do package.json

```json
{
  "scripts": {
    "start": "expo start",
    "web": "expo start --web",
    "typecheck": "tsc --noEmit",
    "lint": "expo lint",
    "test": "jest --watchAll=false",
    "test:watch": "jest --watch",
    "doctor": "expo-doctor",
    "check": "npm run typecheck && npm run lint && npm run test"
  },
  "jest": { "preset": "jest-expo" }
}
```
Config completa do Jest (setup de mocks, alias `@/`): `testes.md` §2.

## 3. Testes

Pirâmide: muitos unitários (regras, mappers, schemas, validadores) → alguns de componente →
poucos de integração → E2E só nas jornadas críticas. Teste ao lado do arquivo
(`user-rules.test.ts`). Setup com mocks padrão, render com providers, onde mockar a API,
exemplos por tipo e Maestro: `testes.md`.

## 4. Lint, format e CI

O computador verifica o que puder ser verificado. Pipeline mínimo em todo PR:

```text
typecheck → lint → test → (build preview quando main)
```

Exemplo GitHub Actions: `assets/templates/ci.yml`. Prettier para formatação; ESLint do
Expo com regras de hooks ativas.

## 5. Git e commits

- Branches: `main`, `feature/*`, `fix/*`. Sem git-flow para equipe pequena.
- Commits pequenos, prefixo convencional + descrição em português no imperativo:
  `feat: adiciona cadastro de aluno`, `fix: corrige refresh com sessão expirada`,
  `refactor: extrai service de campanhas`, `test: cobre validação do login`.
- História, docs derivados e o código que a implementa no mesmo commit/PR.
- Fluxo completo de commit, push, PR e deploy: skill `git-deploy` (config em `docs/deploy.md`).
- Fluxo: `feature/*` → PR → CI verde → `main` → build preview → homologação → produção.
- Nunca versionar: `.env*` com valores reais, keystores, `credentials.json`,
  `android/` e `ios/` (se usa CNG).

## 6. Dependências

Antes de instalar, responda:
1. Existe solução oficial (`expo-*`) ou já no React Native?
2. É mantida? Tem tipos?
3. Suporta New Architecture? (obrigatório no SDK 55+)
4. Roda no Expo Go ou exige dev build? (https://reactnative.directory) — se exigir, avise.
5. Funciona na Web?
6. Dá para escrever em ~20 linhas? Então não instale.

Instale **sempre** com `npx expo install` e registre em `docs/stack.md`.

Atualização (incluindo SDK do Expo, um SDK por vez):
```text
branch → npx expo install --fix / upgrade → typecheck → lint → testes → build → teste Android/iOS/Web → merge
```

## 7. Ambientes, build e publicação

Tudo em `builds-eas.md` (variantes dev/preview/prod, dev build, EAS Build/Update/Submit,
lojas, Web estática).

## 8. Upgrade de SDK (em branch, um SDK por vez)

```bash
git checkout -b chore/upgrade-sdk-XX
npx expo install expo@^XX.0.0 --fix
npx expo-doctor@latest
# ler changelog do SDK: "Deprecations" e "Breaking changes"; rodar codemods indicados
rm -rf android ios        # se usa CNG
eas build --profile development --platform android
npm run check
# testar fluxos críticos em aparelho → preview → merge
```
Não atualize React, React Native ou Expo Router isoladamente — o `expo install --fix`
alinha tudo com o SDK. Para upgrade, a skill oficial `upgrading-expo` (`expo/skills`)
complementa esta. Contexto de versões: `estado-atual-2026.md`.

## 9. Checklist de release

```
[ ] versão/changelog atualizados
[ ] npm run check verde
[ ] preview testado por alguém além do dev
[ ] crash reporting ativo no build de produção
[ ] variáveis de produção conferidas (eas env:list --environment production)
[ ] política de privacidade e exclusão de conta ok
[ ] runtimeVersion/canal corretos para EAS Update
[ ] testado em aparelho físico Android e iPhone (teclado, permissões, safe area)
```

## 10. Logging e observabilidade

- `console.log` só em desenvolvimento. Produção: logger central (`src/services/logger.ts`)
  que envia para o serviço escolhido (Sentry é o padrão em apps Expo).
- Registrar: tipo do erro, data, versão do app, tela, ação, `x-request-id`, contexto não
  sensível. **Nunca**: senha, token, CPF, dado bancário, segredo.
- Precisa responder: o que quebrou, para quem, quando, em qual versão, qual tela, qual
  request. No backend self-hosted, correlacione pelo `x-request-id` (Prometheus/Grafana/Loki).
