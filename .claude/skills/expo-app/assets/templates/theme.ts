// DESTINO: src/theme/index.ts
// Único ponto de acesso ao visual. Nenhuma cor, medida, fonte ou duração solta nas telas.
// Valores vêm de ./tokens.ts, GERADO a partir de tokens/tokens.json (decisões do docs/guia-visual.md).
// Para mudar a identidade do app: edite tokens.json → rode build-tokens.py (skill ux-ui). Não edite aqui.
import { useColorScheme, type TextStyle } from "react-native";

import { usePreferencesStore } from "@/stores/preferences-store";

import {
  breakpoints,
  darkColors,
  fontFamilies,
  lightColors,
  MIN_TOUCH_TARGET,
  motion,
  radius,
  shadow,
  space,
  spacing,
  typography as baseTypography,
  type ThemeColors,
} from "./tokens";

export { breakpoints, MIN_TOUCH_TARGET, motion, radius, shadow, space, spacing };
export type { ThemeColors };

/** Tema quando o usuário escolhe "Sistema" e o SO não informa. Definido no docs/guia-visual.md. */
const DEFAULT_SCHEME: "dark" | "light" = "dark";

type TextStyleToken = Pick<TextStyle, "fontSize" | "lineHeight" | "fontWeight" | "fontFamily">;
type ScaleEntry = { fontSize: number; lineHeight: number; fontWeight: string };

/** Aplica a fonte da marca por peso (fontes custom no RN são um arquivo por peso). */
function withBrandFont<K extends string>(scale: Record<K, ScaleEntry>): Record<K, TextStyleToken> {
  const out = {} as Record<K, TextStyleToken>;
  for (const [key, style] of Object.entries(scale) as [K, ScaleEntry][]) {
    const family = fontFamilies[style.fontWeight];
    // Com fonte custom o peso já está no arquivo; manter fontWeight pode gerar negrito falso no Android.
    out[key] = family
      ? { fontSize: style.fontSize, lineHeight: style.lineHeight, fontFamily: family, fontWeight: "normal" }
      : { fontSize: style.fontSize, lineHeight: style.lineHeight, fontWeight: style.fontWeight as TextStyle["fontWeight"] };
  }
  return out;
}

export const typography = withBrandFont(baseTypography);

export function useColorSchemeResolved(): "dark" | "light" {
  const system = useColorScheme();
  const preference = usePreferencesStore((s) => s.colorScheme);
  if (preference !== "system") return preference;
  return system === "light" || system === "dark" ? system : DEFAULT_SCHEME;
}

export function useTheme() {
  const scheme = useColorSchemeResolved();
  const colors: ThemeColors = scheme === "light" ? lightColors : darkColors;
  return { scheme, colors, spacing, space, radius, typography, shadow, motion, breakpoints };
}
