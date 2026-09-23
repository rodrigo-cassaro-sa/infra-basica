#!/usr/bin/env bash
# Aplica o padrão da skill num projeto Expo EXISTENTE (criado com create-expo-app).
# Não sobrescreve arquivos que já existem.
# Uso: bash scripts/scaffold-project.sh /caminho/do/projeto [--install]
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
T="$SKILL_DIR/assets/templates"
# Contrato de runtime do deploy (config.js, /health, perfis EAS) mora na
# skill devops. Estes quatro arquivos vêm de lá para que o projeto gerado
# funcione no ambiente real — ver D-004 e o README do stack frontend-expo.
D="$SKILL_DIR/../devops/stacks/frontend-expo"
PROJ="${1:?Informe a pasta do projeto}"
INSTALL="${2:-}"

[[ -f "$PROJ/package.json" ]] || { echo "Erro: sem package.json. Crie antes: npx create-expo-app@latest <nome>" >&2; exit 1; }
grep -q '"expo"' "$PROJ/package.json" || { echo "Erro: não parece projeto Expo." >&2; exit 1; }

cd "$PROJ"

if [[ -d app && ! -d src/app ]]; then
  echo "Aviso: rotas em ./app. Mova para ./src/app e ajuste tsconfig (@/* -> ./src/*) antes de continuar."
fi

mkdir -p src/{app,features/auth/{schemas,services,types},components/{ui,forms,feedback},services/{api,storage},stores,hooks,utils,constants,config,theme,test-utils} tokens .maestro .github/workflows

# Docs do produto: monorepo (../docs, compartilhado com o backend) ou ./docs
if [[ -d ../docs ]]; then DOCS=../docs; else DOCS=docs; fi
mkdir -p "$DOCS"
echo "Docs em: $DOCS"

copy() { # copy <template> <destino>
  if [[ -e "$2" ]]; then echo "  mantido  $2"; else cp "$T/$1" "$2"; echo "  criado   $2"; fi
}

copy_de() { # copy_de <diretorio> <template> <destino>
  if [[ -e "$3" ]]; then echo "  mantido  $3"; else cp "$1/$2" "$3"; echo "  criado   $3"; fi
}

echo "Copiando templates..."
copy api-client.ts     src/services/api/api-client.ts
copy errors.ts         src/services/api/errors.ts
copy query-client.ts   src/services/api/query-client.ts
copy token-storage.ts  src/services/storage/token-storage.ts
copy_de "$D" env.ts    src/config/env.ts
copy theme.ts          src/theme/index.ts
copy tokens.ts         src/theme/tokens.ts
copy screen.tsx        src/components/ui/screen.tsx
copy button.tsx        src/components/ui/button.tsx
copy ui-index.ts       src/components/ui/index.ts
copy preferences-store.ts src/stores/preferences-store.ts
copy use-breakpoint.ts src/hooks/use-breakpoint.ts
copy_de "$D" html.tsx  src/app/+html.tsx
copy session-store.ts  src/stores/session-store.ts
copy auth-schema.ts    src/features/auth/schemas/auth-schema.ts
copy auth-types.ts     src/features/auth/types/auth-types.ts
copy auth-service.ts   src/features/auth/services/auth-service.ts
copy format.ts         src/utils/format.ts
copy feedback.tsx      src/components/feedback/index.tsx
copy form-input.tsx    src/components/forms/form-input.tsx
copy app.config.ts     app.config.ts
copy_de "$D" eas.json  eas.json
copy_de "$SKILL_DIR/../devops/assets/workflows" ci.yml .github/workflows/ci.yml
copy env.example       .env.example
copy docs/stack.md            "$DOCS/stack.md"
copy docs/rotas.md            "$DOCS/rotas.md"
# Histórias, mapa de telas e contratos: skills dah-historia e dah-documentacao (não copiados aqui)

# _layout e tsconfig costumam existir no template do Expo: não sobrescreve, só avisa.
[[ -e src/app/_layout.tsx ]] && echo "  revisar  src/app/_layout.tsx (compare com assets/templates/root-layout.tsx)" || copy root-layout.tsx src/app/_layout.tsx
echo "  revisar  tsconfig.json (strict + noUncheckedIndexedAccess + paths @/* -> ./src/*; ver assets/templates/tsconfig.json)"

[[ -f .env ]] || { cp .env.example .env; echo "  criado   .env (ajuste o IP da sua máquina na rede)"; }
grep -qxF '.env' .gitignore 2>/dev/null || printf '\n.env\n.env.local\n' >> .gitignore

if [[ "$INSTALL" == "--install" ]]; then
  echo "Instalando dependências..."
  npx expo install @tanstack/react-query zod react-hook-form @hookform/resolvers \
    @react-native-community/netinfo expo-secure-store expo-image expo-dev-client \
    react-native-safe-area-context expo-splash-screen expo-status-bar \
    zustand @react-native-async-storage/async-storage
  npx expo install -- --save-dev jest-expo jest @types/jest @testing-library/react-native
fi

cat <<'MSG'

Pronto. Próximos passos:
  1. Ajuste app.config.ts (BASE_ID, nome, slug, scheme) e preencha docs/stack.md
     Histórias e docs (contratos, telas, regras): skills dah-historia e dah-documentacao
     Identidade visual (skill ux-ui): copie assets/templates/docs/guia-visual.md -> docs/guia-visual.md
     e assets/tokens/tokens.json -> tokens/tokens.json; ajuste e gere o tema:
       python3 <ux-ui>/scripts/build-tokens.py tokens/tokens.json --ts src/theme/tokens.ts --check
  2. Revise tsconfig.json e src/app/_layout.tsx
  3. npx expo lint && npx tsc --noEmit && npx expo-doctor@latest
  4. eas init && eas build --profile development --platform android
  5. Primeira feature: bash <skill>/scripts/scaffold-feature.sh <feature> <Entidade>
MSG
