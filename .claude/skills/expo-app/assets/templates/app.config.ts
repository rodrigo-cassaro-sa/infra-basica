// DESTINO: app.config.ts (raiz) — substitui/complementa app.json
// APP_VARIANT (definido por profile no eas.json) permite instalar DEV, PREVIEW e produção
// lado a lado no mesmo aparelho. URLs de API ficam nas variáveis de ambiente do EAS
// (eas env:create), não aqui.
import type { ConfigContext, ExpoConfig } from "expo/config";

const APP_VARIANT = process.env.APP_VARIANT ?? "development";
const BASE_ID = "com.empresa.meuapp"; // TROCAR
const BASE_NAME = "MeuApp"; // TROCAR

const variants = {
  development: { id: `${BASE_ID}.dev`, name: `${BASE_NAME} DEV` },
  preview: { id: `${BASE_ID}.preview`, name: `${BASE_NAME} PREVIEW` },
  production: { id: BASE_ID, name: BASE_NAME },
} as const;

const variant = variants[APP_VARIANT as keyof typeof variants] ?? variants.development;

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: variant.name,
  slug: "meuapp", // TROCAR
  scheme: "meuapp", // deep links: meuapp://rota
  version: "1.0.0",
  orientation: "portrait",
  userInterfaceStyle: "automatic",
  icon: "./assets/images/icon.png",
  ios: { ...config.ios, bundleIdentifier: variant.id, supportsTablet: true },
  android: {
    ...config.android,
    package: variant.id,
    adaptiveIcon: { foregroundImage: "./assets/images/adaptive-icon.png", backgroundColor: "#0B0B0F" },
  },
  web: { output: "static" },
  runtimeVersion: { policy: "fingerprint" }, // EAS Update só entrega OTA compatível com o nativo
  plugins: [
    "expo-router",
    "expo-secure-store",
    ["expo-splash-screen", { image: "./assets/images/splash-icon.png", imageWidth: 200, backgroundColor: "#0B0B0F" }],
    // SDK 56+: plugins tipados podem ser importados de "expo-<pacote>/plugin"
  ],
  experiments: {
    typedRoutes: true,
    reactCompiler: true, // com isso ligado, não adicione useMemo/useCallback/memo sem medir
  },
  extra: {
    eas: { projectId: "PREENCHER_COM_eas_init" },
  },
});
