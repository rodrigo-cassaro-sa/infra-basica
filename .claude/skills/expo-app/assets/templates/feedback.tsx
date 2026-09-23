// DESTINO: src/components/feedback/index.tsx
// Estados de tela reutilizáveis: loading, vazio, erro, offline.
import { onlineManager } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { ActivityIndicator, Pressable, Text, View } from "react-native";

import { getUserMessage, NetworkError } from "@/services/api/errors";
import { MIN_TOUCH_TARGET, useTheme } from "@/theme";

function Centered({ children }: { children: ReactNode }) {
  const { spacing } = useTheme();
  return <View style={{ flex: 1, alignItems: "center", justifyContent: "center", padding: spacing.lg, gap: spacing.md }}>{children}</View>;
}

export function LoadingView({ label = "Carregando" }: { label?: string }) {
  const { colors } = useTheme();
  return (
    <Centered>
      <ActivityIndicator accessibilityLabel={label} color={colors.primary} />
    </Centered>
  );
}

type EmptyStateProps = { title: string; description?: string; actionLabel?: string; onAction?: () => void };

export function EmptyState({ title, description, actionLabel, onAction }: EmptyStateProps) {
  const { colors, typography } = useTheme();
  return (
    <Centered>
      <Text style={[typography.subtitle, { color: colors.text, textAlign: "center" }]}>{title}</Text>
      {description ? <Text style={[typography.body, { color: colors.textMuted, textAlign: "center" }]}>{description}</Text> : null}
      {actionLabel && onAction ? <RetryButton label={actionLabel} onPress={onAction} /> : null}
    </Centered>
  );
}

/** O aparelho está sem rede, ou foi o servidor que não respondeu? */
function semConexao(): boolean {
  // O onlineManager é alimentado pelo NetInfo (ver services/api/query-client).
  // Dizer "sem internet" com a conexão ativa manda a pessoa procurar defeito
  // no lugar errado — no web, isso costuma ser CORS ou servidor fora.
  return !onlineManager.isOnline();
}

export function ServerUnreachableState({ onRetry }: { onRetry?: () => void }) {
  const { colors, typography } = useTheme();
  return (
    <Centered>
      <Text accessibilityRole="alert" style={[typography.subtitle, { color: colors.text }]}>
        Não foi possível falar com o servidor
      </Text>
      <Text style={[typography.body, { color: colors.textMuted, textAlign: "center" }]}>
        Sua conexão está ativa, mas o servidor não respondeu.
      </Text>
      {onRetry ? <RetryButton onPress={onRetry} /> : null}
    </Centered>
  );
}

export function ErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  const { colors, typography } = useTheme();
  if (error instanceof NetworkError) {
    return semConexao() ? <OfflineState onRetry={onRetry} /> : <ServerUnreachableState onRetry={onRetry} />;
  }
  return (
    <Centered>
      <Text accessibilityRole="alert" style={[typography.body, { color: colors.text, textAlign: "center" }]}>
        {getUserMessage(error)}
      </Text>
      {onRetry ? <RetryButton onPress={onRetry} /> : null}
    </Centered>
  );
}

export function OfflineState({ onRetry }: { onRetry?: () => void }) {
  const { colors, typography } = useTheme();
  return (
    <Centered>
      <Text style={[typography.subtitle, { color: colors.text }]}>Você está sem internet</Text>
      <Text style={[typography.body, { color: colors.textMuted, textAlign: "center" }]}>Verifique a conexão e tente de novo.</Text>
      {onRetry ? <RetryButton onPress={onRetry} /> : null}
    </Centered>
  );
}

export function RetryButton({ label = "Tentar novamente", onPress }: { label?: string; onPress: () => void }) {
  const { colors, spacing, radius, typography } = useTheme();
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      onPress={onPress}
      style={{
        minHeight: MIN_TOUCH_TARGET,
        paddingHorizontal: spacing.lg,
        justifyContent: "center",
        borderRadius: radius.md,
        backgroundColor: colors.primary,
      }}
    >
      <Text style={[typography.label, { color: colors.onPrimary }]}>{label}</Text>
    </Pressable>
  );
}
