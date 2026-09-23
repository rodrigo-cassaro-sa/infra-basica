// src/config/env.ts — ÚNICO lugar do app que lê configuração de ambiente.
//  web (hom/prod): window.__APP_CONFIG__ escrito pelo container (mesma imagem nos dois ambientes)
//  nativo (EAS):   EXPO_PUBLIC_* do perfil de build (preview = hom, production = prod)
//  dev:            EXPO_PUBLIC_* do .env local
export type AppEnv = "dev" | "hom" | "prod";

type AppConfig = {
  apiUrl: string;
  appEnv: AppEnv;
  sentryDsn?: string;
  release: string;
};

declare global {
  interface Window {
    __APP_CONFIG__?: Partial<AppConfig>;
  }
}

const runtime: Partial<AppConfig> =
  (typeof window !== "undefined" && window.__APP_CONFIG__) || {};

export const config: AppConfig = {
  apiUrl: runtime.apiUrl ?? process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000",
  appEnv: (runtime.appEnv ?? process.env.EXPO_PUBLIC_APP_ENV ?? "dev") as AppEnv,
  sentryDsn: runtime.sentryDsn || process.env.EXPO_PUBLIC_SENTRY_DSN || undefined,
  release: runtime.release ?? process.env.EXPO_PUBLIC_RELEASE ?? "dev",
};

export const isProd = config.appEnv === "prod";

// Nunca renderizar config.apiUrl no HTML estático: no build (SSG) ela ainda é o fallback.
// Usar só em runtime (chamadas de API, Sentry.init).
