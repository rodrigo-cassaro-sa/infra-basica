// DESTINO: src/components/ui/button.tsx
// Botão único do app. Variantes da ux-ui: primary · secondary · ghost (=tertiary) · danger (=destructive).
// Nenhuma tela redesenha botão: precisa de outro visual → nova variante aqui.
import { ActivityIndicator, Pressable, Text } from "react-native";

import { MIN_TOUCH_TARGET, useTheme } from "@/theme";

export type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

type ButtonProps = {
  title: string;
  onPress: () => void;
  variant?: ButtonVariant;
  loading?: boolean;
  /** Texto durante o loading. Padrão: "Salvando…". */
  loadingTitle?: string;
  disabled?: boolean;
  /** Descreve o resultado quando o título não basta (ex.: "Salva e volta para a lista"). */
  accessibilityHint?: string;
};

export function Button({
  title,
  onPress,
  variant = "primary",
  loading = false,
  loadingTitle = "Salvando…",
  disabled = false,
  accessibilityHint,
}: ButtonProps) {
  const { colors, spacing, radius, typography } = useTheme();
  const isDisabled = disabled || loading;

  const palette = {
    primary: { bg: colors.primary, bgPressed: colors.primaryPressed, fg: colors.onPrimary, border: colors.primary },
    secondary: { bg: colors.surface, bgPressed: colors.surfaceVariant, fg: colors.text, border: colors.border },
    ghost: { bg: "transparent", bgPressed: colors.surfaceVariant, fg: colors.primary, border: "transparent" },
    danger: { bg: colors.danger, bgPressed: colors.danger, fg: colors.onPrimary, border: colors.danger },
  }[variant];

  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={loading ? loadingTitle : title}
      accessibilityHint={accessibilityHint}
      accessibilityState={{ disabled: isDisabled, busy: loading }}
      disabled={isDisabled}
      onPress={onPress}
      style={({ pressed }) => ({
        minHeight: MIN_TOUCH_TARGET,
        paddingHorizontal: spacing.lg,
        borderRadius: radius.md,
        borderWidth: 1,
        borderColor: palette.border,
        backgroundColor: pressed ? palette.bgPressed : palette.bg,
        opacity: isDisabled ? 0.6 : 1,
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "center",
        gap: spacing.sm,
      })}
    >
      {loading ? <ActivityIndicator color={palette.fg} /> : null}
      <Text style={[typography.label, { color: palette.fg }]}>{loading ? loadingTitle : title}</Text>
    </Pressable>
  );
}
