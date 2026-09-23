// DESTINO: src/stores/preferences-store.ts
// Preferências do usuário (não sensíveis) persistidas no aparelho. Nunca token ou dado pessoal aqui.
import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

type ColorSchemePreference = "system" | "light" | "dark";

type PreferencesState = {
  colorScheme: ColorSchemePreference;
  /** null = segue o idioma do aparelho (só usado se o projeto for multi-idioma; ver ux-ui/references/i18n.md). */
  language: string | null;
  setColorScheme: (value: ColorSchemePreference) => void;
  setLanguage: (value: string | null) => void;
};

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set) => ({
      colorScheme: "system",
      language: null,
      setColorScheme: (colorScheme) => set({ colorScheme }),
      setLanguage: (language) => set({ language }),
    }),
    { name: "preferences", storage: createJSONStorage(() => AsyncStorage) },
  ),
);
