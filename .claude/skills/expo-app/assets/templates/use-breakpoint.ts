// DESTINO: src/hooks/use-breakpoint.ts
import { useWindowDimensions } from "react-native";

import { breakpoints } from "@/theme";

export function useBreakpoint() {
  const { width } = useWindowDimensions();
  return {
    width,
    isPhone: width < breakpoints.tablet,
    isTablet: width >= breakpoints.tablet && width < breakpoints.desktop,
    isDesktop: width >= breakpoints.desktop,
  };
}
