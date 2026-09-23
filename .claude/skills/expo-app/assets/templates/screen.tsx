// DESTINO: src/components/ui/screen.tsx
// Container padrão de tela: safe area + teclado + espaçamento e cores do tema.
import type { ReactNode } from "react";
import { KeyboardAvoidingView, Platform, ScrollView, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { useTheme } from "@/theme";

type ScreenProps = {
  children: ReactNode;
  title?: string;
  /** false para telas com FlatList própria (nunca aninhe FlatList dentro de ScrollView) */
  scroll?: boolean;
};

const MAX_CONTENT_WIDTH = 720; // centraliza em tablet/web

export function Screen({ children, title, scroll = true }: ScreenProps) {
  const { colors, spacing, typography } = useTheme();

  const contentStyle = {
    padding: spacing.md,
    gap: spacing.md,
    flexGrow: 1,
    width: "100%" as const,
    maxWidth: MAX_CONTENT_WIDTH,
    alignSelf: "center" as const,
  };

  const content = (
    <>
      {title ? (
        <Text accessibilityRole="header" style={[typography.title, { color: colors.text }]}>
          {title}
        </Text>
      ) : null}
      {children}
    </>
  );

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={["top", "left", "right"]}>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
        {scroll ? (
          <ScrollView contentContainerStyle={contentStyle} keyboardShouldPersistTaps="handled">
            {content}
          </ScrollView>
        ) : (
          <View style={[{ flex: 1 }, contentStyle]}>{content}</View>
        )}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
