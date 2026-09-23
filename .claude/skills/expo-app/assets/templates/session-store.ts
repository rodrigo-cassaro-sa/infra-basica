// DESTINO: src/stores/session-store.ts
// Estado da sessão (estado de CLIENTE legítimo). Tokens ficam no tokenStorage, não aqui.
// status "loading" segura a splash até saber se há sessão — evita piscar a tela de login.
import { Platform } from "react-native";
import { create } from "zustand";

import { getMe, login as loginRequest, revokeSession } from "@/features/auth/services/auth-service";
import type { LoginFormValues, SessionUser } from "@/features/auth/types/auth-types";
import { setUnauthorizedHandler } from "@/services/api/api-client";
import { queryClient } from "@/services/api/query-client";
import { tokenStorage } from "@/services/storage/token-storage";

type SessionStatus = "loading" | "authenticated" | "unauthenticated";

type SessionState = {
  status: SessionStatus;
  user: SessionUser | null;
  bootstrap: () => Promise<void>;
  login: (values: LoginFormValues) => Promise<void>;
  logout: () => Promise<void>;
};

export const useSessionStore = create<SessionState>()((set) => ({
  status: "loading",
  user: null,

  async bootstrap() {
    const hasToken = (await tokenStorage.getAccessToken()) ?? (await tokenStorage.getRefreshToken());
    try {
      // Na Web a sessão pode estar só no cookie httpOnly: tenta /auth/me mesmo sem token local.
      if (!hasToken && Platform.OS !== "web") throw new Error("sem sessão");
      set({ status: "authenticated", user: await getMe() });
    } catch {
      await tokenStorage.clear();
      set({ status: "unauthenticated", user: null });
    }
  },

  async login(values) {
    const user = await loginRequest(values);
    set({ status: "authenticated", user });
    // Não navegue: o Stack.Protected troca de grupo quando o status muda.
  },

  async logout() {
    await revokeSession();
    await tokenStorage.clear();
    queryClient.clear(); // sem isso o próximo usuário do aparelho vê dados em cache do anterior
    set({ status: "unauthenticated", user: null });
  },
}));

// Refresh falhou no apiClient → sessão encerrada.
setUnauthorizedHandler(() => {
  queryClient.clear();
  useSessionStore.setState({ status: "unauthenticated", user: null });
});
