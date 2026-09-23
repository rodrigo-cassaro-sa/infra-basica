// DESTINO: src/services/api/query-client.ts
// QueryClient configurado para React Native: rede (NetInfo) e foco (AppState).
import NetInfo from "@react-native-community/netinfo";
import { focusManager, onlineManager, QueryClient } from "@tanstack/react-query";
import { AppState, Platform, type AppStateStatus } from "react-native";

import { AppError, NetworkError, ServerError } from "./errors";

const MAX_RETRIES = 2;

// Pausa/retoma queries conforme conectividade
onlineManager.setEventListener((setOnline) =>
  NetInfo.addEventListener((state) => setOnline(!!state.isConnected)),
);

// Refetch ao voltar para o app (no mobile; na Web o próprio TanStack usa visibilitychange)
function onAppStateChange(status: AppStateStatus) {
  if (Platform.OS !== "web") focusManager.setFocused(status === "active");
}
AppState.addEventListener("change", onAppStateChange);

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (failureCount, error) => {
        // Só repete falha transitória. 4xx não adianta repetir.
        const isTransient = error instanceof NetworkError || error instanceof ServerError || !(error instanceof AppError);
        return isTransient && failureCount < MAX_RETRIES;
      },
    },
    mutations: { retry: false },
  },
});
