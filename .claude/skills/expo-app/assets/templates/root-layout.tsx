// DESTINO: src/app/_layout.tsx
// Providers globais + guarda de sessão. Mantenha este arquivo fino.
// App sem login: remova os Stack.Protected e o bootstrap da sessão.
import { QueryClientProvider } from "@tanstack/react-query";
import { Stack } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { StatusBar } from "expo-status-bar";
import { useEffect } from "react";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { queryClient } from "@/services/api/query-client";
import { useSessionStore } from "@/stores/session-store";
import { useTheme } from "@/theme";

SplashScreen.preventAutoHideAsync();

function RootNavigator() {
  const status = useSessionStore((s) => s.status);
  const { colors, scheme } = useTheme();

  useEffect(() => {
    useSessionStore.getState().bootstrap();
  }, []);

  useEffect(() => {
    if (status !== "loading") SplashScreen.hideAsync();
  }, [status]);

  if (status === "loading") return null; // splash continua visível

  return (
    <>
      <StatusBar style={scheme === "dark" ? "light" : "dark"} />
      <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.background } }}>
        <Stack.Protected guard={status === "authenticated"}>
          <Stack.Screen name="(app)" />
        </Stack.Protected>
        <Stack.Protected guard={status === "unauthenticated"}>
          <Stack.Screen name="(auth)" />
        </Stack.Protected>
      </Stack>
    </>
  );
}

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <RootNavigator />
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}
