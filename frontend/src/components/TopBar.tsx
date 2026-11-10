import type { Copy, Language } from "../copy";
import type { Theme } from "../hooks/useTheme";
import { BrandMark } from "./BrandMark";

type Props = { t: Copy; language: Language; onLanguage: (language: Language) => void; theme: Theme; onToggleTheme: () => void };

export function TopBar({ t, language, onLanguage, theme, onToggleTheme }: Props) {
  const themeLabel = theme === "dark" ? t.themeToLight : t.themeToDark;
  return (
    <header className="topbar">
      <a className="brand" href="#home" aria-label={t.homeLabel}>
        <BrandMark />
        <span className="brand-name">Civic<span>Lens</span></span>
      </a>
      <div className="topbar-right">
        <span className="pilot-pill"><span className="pilot-dot" />{t.pilot}</span>
        <div className="language-switch" role="group" aria-label={t.chooseLanguage}>
          <button type="button" className={language === "en" ? "selected" : ""} onClick={() => onLanguage("en")} aria-pressed={language === "en"}>EN</button>
          <button type="button" className={language === "ta" ? "selected" : ""} onClick={() => onLanguage("ta")} aria-pressed={language === "ta"}>தமிழ்</button>
        </div>
        <button type="button" className="theme-toggle" onClick={onToggleTheme} aria-label={themeLabel} title={themeLabel}>
          <span aria-hidden="true">{theme === "dark" ? "☀" : "☾"}</span>
        </button>
      </div>
    </header>
  );
}
