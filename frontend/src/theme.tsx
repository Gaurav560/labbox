import { createContext, useContext, useEffect, type ReactNode } from "react";
import { usePersistentState } from "./persist";

export type Theme = "dark" | "light";

const ThemeContext = createContext<{ theme: Theme; toggle: () => void }>({ theme: "dark", toggle: () => {} });

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = usePersistentState<Theme>("theme", "light"); // Ukiyo opens on washi paper
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);
  return (
    <ThemeContext.Provider value={{ theme, toggle: () => setTheme((t) => (t === "dark" ? "light" : "dark")) }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);

// Terminal colours follow the theme (xterm cannot read CSS variables).
export const TERMINAL_THEMES = {
  dark: { background: "#0d100e", foreground: "#e6ebe7", cursor: "#e6ebe7", selectionBackground: "#3a423c" },
  // xterm's default ANSI colours are made for dark backgrounds; these keep AA contrast on light.
  light: {
    background: "#ffffff",
    foreground: "#1f2328",
    cursor: "#1f2328",
    selectionBackground: "#d1d9e0",
    black: "#1b1f2a",
    red: "#b3261e",
    green: "#0b7a4b",
    yellow: "#7f5300",
    blue: "#3550d4",
    magenta: "#8e3bb5",
    cyan: "#0e6a7e",
    white: "#555e70",
    brightBlack: "#555e70",
    brightRed: "#b3261e",
    brightGreen: "#0b7a4b",
    brightYellow: "#7f5300",
    brightBlue: "#3550d4",
    brightMagenta: "#8e3bb5",
    brightCyan: "#0e6a7e",
    brightWhite: "#1b1f2a",
  },
} as const;
