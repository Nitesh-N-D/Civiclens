import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { askQuestion, fetchChanges, fetchHealth, fetchSchemes, fetchSources, RateLimitedError } from "./api";
import type { SignInConfig } from "./api";
import { AdminPanel } from "./components/AdminPanel";
import { BrandMark } from "./components/BrandMark";
import { ChangeList } from "./components/ChangeNotices";
import { Conversation } from "./components/Conversation";
import { Discovery } from "./components/Discovery";
import { EligibilityChecker, SchemeComparison } from "./components/EligibilityChecker";
import { Hero, TrustStrip } from "./components/Hero";
import { SchemeExplorer } from "./components/SchemeExplorer";
import { TopBar } from "./components/TopBar";
import { copy } from "./copy";
import type { Language } from "./copy";
import { useTheme } from "./hooks/useTheme";
import type { Answer, Change, Citation, SchemeCard, Turn } from "./types";

function App() {
  const { theme, toggle: toggleTheme } = useTheme();
  const [language, setLanguage] = useState<Language>("ta");
  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [loading, setLoading] = useState(false);
  const [sources, setSources] = useState<Citation[]>([]);
  const [schemes, setSchemes] = useState<SchemeCard[]>([]);
  const [changes, setChanges] = useState<Change[]>([]);
  const [adminEnabled, setAdminEnabled] = useState(false);
  const [signIn, setSignIn] = useState<SignInConfig | null>(null);
  const [serviceError, setServiceError] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const t = copy[language];

  useEffect(() => {
    document.documentElement.lang = language;
    document.title = language === "ta"
      ? "CivicLens — அரசுச் சேவைகள், எளிய வழியில்"
      : "CivicLens — Public services, made clearer";
  }, [language]);

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setAdminEnabled(data.admin_enabled === true);
        setSignIn(data.admin_sign_in ?? null);
      })
      .catch(() => setAdminEnabled(false));
    fetchSources().then(setSources).catch(() => setServiceError(true));
  }, []);

  useEffect(() => {
    fetchSchemes(language).then(setSchemes).catch(() => setSchemes([]));
    fetchChanges(language).then(setChanges).catch(() => setChanges([]));
  }, [language]);

  function settleLastTurn(value: string, answer: Answer) {
    setTurns((items) => [...items.slice(0, -1), { question: value, answer }]);
  }

  async function submitQuestion(event?: FormEvent, preset?: string) {
    event?.preventDefault();
    const value = (preset ?? question).trim();
    if (!value || loading) return;
    setQuestion(value);
    setLoading(true);
    setServiceError(false);
    setTurns((items) => [...items, { question: value, answer: { text: "", citations: [], mode: "search" }, pending: true }]);
    try {
      settleLastTurn(value, await askQuestion(value, language));
      setQuestion("");
    } catch (error) {
      if (error instanceof RateLimitedError) {
        settleLastTurn(value, { text: t.rateLimited, citations: [], mode: "search", warning: t.disclaimer });
        return;
      }
      setServiceError(true);
      settleLastTurn(value, { text: t.noAnswer, citations: [], mode: "search", warning: t.disclaimer });
      setQuestion("");
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setTurns([]);
    setQuestion("");
    inputRef.current?.focus();
  }

  return (
    <div className="app-shell" lang={language}>
      <TopBar t={t} language={language} onLanguage={setLanguage} theme={theme} onToggleTheme={toggleTheme} />
      <main id="home">
        <Hero t={t} compact={turns.length > 0} question={question} loading={loading} inputRef={inputRef}
          onQuestion={setQuestion} onSubmit={(event) => void submitQuestion(event)} />
        <TrustStrip t={t} />
        <section className="workspace">
          {turns.length ? (
            <Conversation t={t} turns={turns} question={question} loading={loading} serviceError={serviceError}
              onQuestion={setQuestion} onSubmit={(event) => void submitQuestion(event)} onReset={reset} />
          ) : (
            <>
              <Discovery t={t} sources={sources} serviceError={serviceError} onAsk={(prompt) => void submitQuestion(undefined, prompt)} />
              <SchemeExplorer t={t} schemes={schemes} />
              <EligibilityChecker key={`eligibility-${language}`} t={t} language={language} schemes={schemes} />
              <SchemeComparison key={`compare-${language}`} t={t} language={language} schemes={schemes} />
              {!!changes.length && <ChangeList changes={changes} t={t} />}
            </>
          )}
        </section>
        <footer className="page-footer">
          <div className="footer-brand"><BrandMark /><span>CivicLens</span></div>
          <p>{t.disclaimer}</p>
          <a href="https://www.myscheme.gov.in/" target="_blank" rel="noreferrer">{t.visitMyScheme} ↗</a>
        </footer>
        {adminEnabled && <AdminPanel t={t} signIn={signIn} />}
      </main>
    </div>
  );
}

export default App;
