// DESTINO: src/features/auth/services/auth-service.ts
import { apiClient, noContent } from "@/services/api/api-client";
import { tokenStorage } from "@/services/storage/token-storage";

import { loginResponseDtoSchema, sessionUserDtoSchema } from "../schemas/auth-schema";
import type { LoginFormValues, SessionUser } from "../types/auth-types";

export async function login(values: LoginFormValues): Promise<SessionUser> {
  const res = await apiClient.post("/auth/login", values, loginResponseDtoSchema, { auth: false });
  await tokenStorage.setTokens(res);
  return res.user;
}

/** Usuário da sessão atual. Um 401 aqui já passa pelo refresh do apiClient. */
export async function getMe(): Promise<SessionUser> {
  return apiClient.get("/auth/me", sessionUserDtoSchema);
}

/** Revoga o refresh no backend. Falha de rede não impede o logout local. */
export async function revokeSession(): Promise<void> {
  const refreshToken = await tokenStorage.getRefreshToken();
  await apiClient
    .post("/auth/logout", refreshToken ? { refreshToken } : {}, noContent, { auth: false })
    .catch(() => undefined);
}
