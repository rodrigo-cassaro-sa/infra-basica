#!/usr/bin/env bash
# Gera o esqueleto de uma feature no padrão do skill.
# Uso (na raiz do app):  bash scripts/scaffold-feature.sh <feature-kebab> <Entidade>
# Ex.:                   bash scripts/scaffold-feature.sh alunos Aluno
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Uso: $0 <feature-kebab-plural> <EntidadePascal>"; exit 1
fi

FEATURE="$1"                         # alunos
ENTITY="$2"                          # Aluno
entity="$(echo "${ENTITY:0:1}" | tr '[:upper:]' '[:lower:]')${ENTITY:1}"   # aluno
file="$(echo "$ENTITY" | sed -E 's/([a-z0-9])([A-Z])/\1-\2/g' | tr '[:upper:]' '[:lower:]')"  # aluno / plano-aula
BASE="src/features/$FEATURE"

if [ -d "$BASE" ]; then echo "Já existe: $BASE"; exit 1; fi
mkdir -p "$BASE"/{components,hooks,services,schemas,types,utils,screens}

cat > "$BASE/schemas/$file-schema.ts" <<TS
import { z } from "zod";

// Formato da API (DTO) — deve bater com docs/contratos-de-api.md
export const ${entity}DtoSchema = z.object({
  id: z.string(),
  // TODO: campos conforme contrato (snake_case se a API usar)
});
export const ${entity}ListDtoSchema = z.array(${entity}DtoSchema);

// Formato do formulário
export const ${entity}FormSchema = z.object({
  // TODO: campos do formulário com mensagens em português
});
TS

cat > "$BASE/types/$file-types.ts" <<TS
import type { z } from "zod";

import type { ${entity}DtoSchema, ${entity}FormSchema } from "../schemas/$file-schema";

export type ${ENTITY}Dto = z.infer<typeof ${entity}DtoSchema>;
export type ${ENTITY}FormValues = z.infer<typeof ${entity}FormSchema>;

/** Modelo usado pela UI */
export type ${ENTITY} = {
  id: string;
};
TS

cat > "$BASE/utils/$file-mapper.ts" <<TS
import type { ${ENTITY}, ${ENTITY}Dto, ${ENTITY}FormValues } from "../types/$file-types";

export function to${ENTITY}(dto: ${ENTITY}Dto): ${ENTITY} {
  return { id: dto.id };
}

export function to${ENTITY}Payload(values: ${ENTITY}FormValues) {
  return { ...values };
}
TS

cat > "$BASE/utils/$file-rules.ts" <<TS
// Regras de negócio puras da feature. Uma função por regra (cite o ID: RN-01...).
export {};
TS

cat > "$BASE/services/$file-service.ts" <<TS
import { apiClient } from "@/services/api/api-client";

import { ${entity}DtoSchema, ${entity}ListDtoSchema } from "../schemas/$file-schema";
import type { ${ENTITY}FormValues } from "../types/$file-types";
import { to${ENTITY}, to${ENTITY}Payload } from "../utils/$file-mapper";

const PATH = "/$FEATURE";

export async function get${ENTITY}List() {
  const dtos = await apiClient.get(PATH, ${entity}ListDtoSchema);
  return dtos.map(to${ENTITY});
}

export async function get${ENTITY}(id: string) {
  return to${ENTITY}(await apiClient.get(\`\${PATH}/\${id}\`, ${entity}DtoSchema));
}

export async function create${ENTITY}(values: ${ENTITY}FormValues) {
  return to${ENTITY}(await apiClient.post(PATH, to${ENTITY}Payload(values), ${entity}DtoSchema));
}
TS

cat > "$BASE/query-keys.ts" <<TS
export const ${entity}Keys = {
  all: ["$FEATURE"] as const,
  list: (filters: Record<string, unknown> = {}) => [...${entity}Keys.all, "list", filters] as const,
  detail: (id: string) => [...${entity}Keys.all, "detail", id] as const,
};
TS

cat > "$BASE/hooks/use-$FEATURE.ts" <<TS
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ${entity}Keys } from "../query-keys";
import { create${ENTITY}, get${ENTITY}, get${ENTITY}List } from "../services/$file-service";

export function use${ENTITY}List() {
  return useQuery({ queryKey: ${entity}Keys.list(), queryFn: get${ENTITY}List });
}

export function use${ENTITY}(id: string) {
  return useQuery({ queryKey: ${entity}Keys.detail(id), queryFn: () => get${ENTITY}(id), enabled: !!id });
}

export function useCreate${ENTITY}() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: create${ENTITY},
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ${entity}Keys.all }),
  });
}
TS

cat > "$BASE/components/$file-card.tsx" <<TS
import { Pressable, Text } from "react-native";

import { MIN_TOUCH_TARGET, useTheme } from "@/theme";

import type { ${ENTITY} } from "../types/$file-types";

type ${ENTITY}CardProps = {
  item: ${ENTITY};
  onPress: (id: string) => void;
};

export function ${ENTITY}Card({ item, onPress }: ${ENTITY}CardProps) {
  const { colors, spacing, radius, typography } = useTheme();
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={\`Abrir \${item.id}\`}
      onPress={() => onPress(item.id)}
      style={{ minHeight: MIN_TOUCH_TARGET, padding: spacing.md, borderRadius: radius.md, backgroundColor: colors.surface }}
    >
      <Text style={[typography.body, { color: colors.text }]}>{item.id}</Text>
    </Pressable>
  );
}
TS

cat > "$BASE/screens/$file-list-screen.tsx" <<TS
import { router } from "expo-router";
import { FlatList, View } from "react-native";

import { EmptyState, ErrorState, LoadingView } from "@/components/feedback";
import { useTheme } from "@/theme";

import { ${ENTITY}Card } from "../components/$file-card";
import { use${ENTITY}List } from "../hooks/use-$FEATURE";

export function ${ENTITY}ListScreen() {
  const { colors, spacing } = useTheme();
  const query = use${ENTITY}List();

  if (query.isPending) return <LoadingView />;
  if (query.isError) return <ErrorState error={query.error} onRetry={query.refetch} />;

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <FlatList
        data={query.data}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <${ENTITY}Card item={item} onPress={(id) => router.push(\`/$FEATURE/\${id}\`)} />}
        contentContainerStyle={{ padding: spacing.md, gap: spacing.sm, flexGrow: 1 }}
        ListEmptyComponent={<EmptyState title="Nada por aqui ainda" />}
        onRefresh={query.refetch}
        refreshing={query.isRefetching}
      />
    </View>
  );
}
TS

cat > "$BASE/index.ts" <<TS
// API pública da feature. Outras features importam SÓ daqui.
export { ${ENTITY}ListScreen } from "./screens/$file-list-screen";
export { use${ENTITY}, use${ENTITY}List, useCreate${ENTITY} } from "./hooks/use-$FEATURE";
export type { ${ENTITY} } from "./types/$file-types";
TS

cat > "$BASE/utils/$file-mapper.test.ts" <<TS
import { to${ENTITY} } from "./$file-mapper";

describe("to${ENTITY}", () => {
  it("converte DTO em modelo", () => {
    expect(to${ENTITY}({ id: "1" })).toEqual({ id: "1" });
  });
});
TS

echo "Feature criada em $BASE"
echo "Próximos passos:"
echo "  1. Preencher schemas conforme docs/contratos-de-api.md"
echo "  2. Ajustar modelo em types/ e mapper"
echo "  3. Criar rota fina: src/app/(app)/$FEATURE/index.tsx -> <${ENTITY}ListScreen />"
