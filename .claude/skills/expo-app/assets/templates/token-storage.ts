// DESTINO: src/services/storage/token-storage.ts
// Mobile: SecureStore (Keychain / Keystore).
// Web: SecureStore não existe. A sessão deve usar cookie httpOnly emitido pelo backend;
// aqui o token fica só em memória (não vai para localStorage, que é legível por XSS).
import * as SecureStore from "expo-secure-store";
import { Platform } from "react-native";

const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";

const isWeb = Platform.OS === "web";
const memory = new Map<string, string>();

async function getItem(key: string) {
  return isWeb ? (memory.get(key) ?? null) : SecureStore.getItemAsync(key);
}
async function setItem(key: string, value: string) {
  if (isWeb) memory.set(key, value);
  else await SecureStore.setItemAsync(key, value);
}
async function deleteItem(key: string) {
  if (isWeb) memory.delete(key);
  else await SecureStore.deleteItemAsync(key);
}

export const tokenStorage = {
  getAccessToken: () => getItem(ACCESS_KEY),
  getRefreshToken: () => getItem(REFRESH_KEY),
  async setTokens(tokens: { accessToken: string; refreshToken?: string }) {
    await setItem(ACCESS_KEY, tokens.accessToken);
    if (tokens.refreshToken) await setItem(REFRESH_KEY, tokens.refreshToken);
  },
  async clear() {
    await Promise.all([deleteItem(ACCESS_KEY), deleteItem(REFRESH_KEY)]);
  },
};
