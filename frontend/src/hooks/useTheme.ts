import { useEffect, useState } from "react";

export type Theme = "light" | "dark";
const STORAGE_KEY = "civiclens-theme";

export function initialTheme(): Theme {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === "light" || saved === "dark") return saved;
  } catch {
    // Storage may be blocked; fall back to the system preference.
  }
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

/** Light/dark theme: follows the system until the visitor chooses, then remembers the choice. */
export function useTheme() {
  const [theme, setTheme] = useState<Theme>(initialTheme);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute("content", theme === "dark" ? "#141c17" : "#f8faf8");
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      // Preference simply is not remembered.
    }
  }, [theme]);
  const toggle = () => setTheme((current) => (current === "dark" ? "light" : "dark"));
  return { theme, toggle };
}
