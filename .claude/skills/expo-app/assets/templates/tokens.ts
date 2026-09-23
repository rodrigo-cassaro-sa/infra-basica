// GERADO por build-tokens.py — não edite à mão; edite tokens.json.
// DESTINO: src/theme/tokens.ts — ponto de partida. Regenere a partir do tokens.json do projeto:
//   python3 <skill ux-ui>/scripts/build-tokens.py tokens/tokens.json --ts src/theme/tokens.ts

export const lightColors = {
  primary: "#6D28D9",
  primaryHover: "#5B21B6",
  primaryPressed: "#4C1D95",
  onPrimary: "#FFFFFF",
  background: "#FFFFFF",
  surface: "#F4F4F6",
  surfaceVariant: "#E9E9EE",
  text: "#15151C",
  textMuted: "#5B5B69",
  textDisabled: "#A6A6B4",
  border: "#8A8A99",
  divider: "#E4E4E9",
  focus: "#6D28D9",
  success: "#15803D",
  warning: "#B45309",
  danger: "#B91C1C",
  info: "#1D4ED8",
} as const;

export const darkColors = {
  primary: "#A78BFA",
  primaryHover: "#C4B5FD",
  primaryPressed: "#8B5CF6",
  onPrimary: "#1A0B3D",
  background: "#0F0F14",
  surface: "#1A1A22",
  surfaceVariant: "#252530",
  text: "#ECECF1",
  textMuted: "#A6A6B4",
  textDisabled: "#6B6B7A",
  border: "#6B6B7A",
  divider: "#2C2C36",
  focus: "#C4B5FD",
  success: "#4ADE80",
  warning: "#FBBF24",
  danger: "#F87171",
  info: "#60A5FA",
} as const;

export type ThemeColors = { [K in keyof typeof lightColors]: string };

export const space = {
  "1": 4,
  "2": 8,
  "3": 12,
  "4": 16,
  "6": 24,
  "8": 32,
  "10": 40,
  "12": 48,
  "16": 64,
} as const;

/** Nomes compatíveis com o theme.ts da skill expo-app. */
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const radius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
  pill: 9999,
} as const;

export const typography = {
  display: {
    fontSize: 40,
    lineHeight: 48,
    fontWeight: "700",
  },
  h1: {
    fontSize: 32,
    lineHeight: 40,
    fontWeight: "700",
  },
  h2: {
    fontSize: 28,
    lineHeight: 36,
    fontWeight: "600",
  },
  h3: {
    fontSize: 24,
    lineHeight: 32,
    fontWeight: "600",
  },
  h4: {
    fontSize: 20,
    lineHeight: 28,
    fontWeight: "600",
  },
  bodyLarge: {
    fontSize: 18,
    lineHeight: 28,
    fontWeight: "400",
  },
  body: {
    fontSize: 16,
    lineHeight: 24,
    fontWeight: "400",
  },
  bodySmall: {
    fontSize: 14,
    lineHeight: 20,
    fontWeight: "400",
  },
  label: {
    fontSize: 14,
    lineHeight: 20,
    fontWeight: "600",
  },
  caption: {
    fontSize: 12,
    lineHeight: 16,
    fontWeight: "400",
  },
  title: {
    fontSize: 24,
    lineHeight: 32,
    fontWeight: "600",
  },
  subtitle: {
    fontSize: 20,
    lineHeight: 28,
    fontWeight: "600",
  },
} as const;

/** Strings para a prop boxShadow (RN 0.76+ / New Architecture) ou CSS. */
export const shadow = {
  sm: "0px 1px 2px 0px rgba(0, 0, 0, 0.08)",
  md: "0px 4px 12px 0px rgba(0, 0, 0, 0.12)",
  lg: "0px 12px 32px 0px rgba(0, 0, 0, 0.16)",
} as const;

export const motion = {
  fast: 150,
  base: 250,
  slow: 350,
} as const;

export const breakpoints = {
  sm: 480,
  md: 768,
  lg: 1024,
  xl: 1440,
  tablet: 768,
  desktop: 1024,
} as const;

/** Fonte carregada (expo-font) por peso; undefined = fonte do sistema. */
export const fontFamilies: Record<string, string | undefined> = {
  "400": undefined,
  "500": undefined,
  "600": undefined,
  "700": undefined,
};

/** Área mínima de toque: 48 atende Android (48dp) e iOS (44pt). */
export const MIN_TOUCH_TARGET = 48;
