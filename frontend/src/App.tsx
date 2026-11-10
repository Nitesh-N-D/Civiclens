import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { copy } from "./copy";
import type { Language } from "./copy";
import { ChangeList, ChangeNotices } from "./ChangeNotices";
import type { Answer, Change, Citation, Turn } from "./types";
import { PrintChecklist } from "./PrintChecklist";

type SchemeCard = { id: string; title: string; department: string; category: string; overview: string; url: string; source_id: string; status: string; eligibility_enabled: boolean };
type AdminOverview = { sources: Citation[]; source_count: number; human_verified_count: number; review_pending_count: number; provider: { configured: boolean; configured_keys: number; last_request_succeeded: boolean | null; last_failure_category: string | null; model: string | null }; monitoring: string; mutations_enabled: boolean };



const suggestions = [
  { icon: "✦", tone: "lavender", key: 0 },
  { icon: "⌂", tone: "mint", key: 1 },
  { icon: "◷", tone: "sand", key: 2 },
];

function BrandMark() {
  return (
    <span className="brand-mark" aria-hidden="true">
      <svg viewBox="0 0 38 38" fill="none">
        <path d="M19 3.5 32 8v10.5c0 8.3-5.2 13.5-13 16-7.8-2.5-13-7.7-13-16V8l13-4.5Z" fill="currentColor" opacity=".12" />
        <path d="M19 5.8 29.5 9.4v9c0 6.9-4 11.4-10.5 13.8C12.5 29.8 8.5 25.3 8.5 18.4v-9L19 5.8Z" stroke="currentColor" strokeWidth="1.7" />
        <circle cx="19" cy="17" r="5" stroke="currentColor" strokeWidth="1.7" />
        <path d="m22.6 20.6 4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    </span>
  );
}

function App() {
  const [language, setLanguage] = useState<Language>("ta");
  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [loading, setLoading] = useState(false);
  const [sources, setSources] = useState<Citation[]>([]);
  const [schemes, setSchemes] = useState<SchemeCard[]>([]);
  const [changes, setChanges] = useState<Change[]>([]);
  const [adminEnabled, setAdminEnabled] = useState(false);
  const [showAdmin, setShowAdmin] = useState(false);
  const [adminToken, setAdminToken] = useState("");
  const [adminOverview, setAdminOverview] = useState<AdminOverview | null>(null);
  const [adminError, setAdminError] = useState(false);
  const [serviceError, setServiceError] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const t = copy[language];
  const currentTurn = turns.at(-1);

  useEffect(() => {
    document.documentElement.lang = language;
    document.title = language === "ta"
      ? "CivicLens — அரசுச் சேவைகள், எளிய வழியில்"
      : "CivicLens — Public services, made clearer";
  }, [language]);

  useEffect(() => {
    fetch("/api/health")
      .then((response) => (response.ok ? response.json() : Promise.reject()))
      .then((data: { admin_enabled?: boolean }) => setAdminEnabled(data.admin_enabled === true))
      .catch(() => setAdminEnabled(false));
  }, []);

  async function loadAdminOverview(event: FormEvent) {
    event.preventDefault();
    setAdminError(false);
    try {
      const response = await fetch("/api/admin/overview", {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      if (!response.ok) throw new Error("not authorized");
      setAdminOverview(await response.json() as AdminOverview);
    } catch {
      setAdminOverview(null);
      setAdminError(true);
    }
  }

  function clearAdminSession() {
    setAdminToken("");
    setAdminOverview(null);
    setAdminError(false);
  }

  useEffect(() => {
    fetch("/api/sources")
      .then((response) => (response.ok ? response.json() : Promise.reject()))
      .then((data: { sources: Citation[] }) => setSources(data.sources ?? []))
      .catch(() => setServiceError(true));
  }, []);

  useEffect(() => {
    fetch(`/api/schemes?language=${language}`)
      .then((response) => (response.ok ? response.json() : Promise.reject()))
      .then((data: { schemes: SchemeCard[] }) => setSchemes(data.schemes ?? []))
      .catch(() => setSchemes([]));
    fetch(`/api/changes?language=${language}`)
      .then((response) => (response.ok ? response.json() : Promise.reject()))
      .then((data: { changes: Change[] }) => setChanges(data.changes ?? []))
      .catch(() => setChanges([]));
  }, [language]);

  async function submitQuestion(event?: FormEvent, preset?: string) {
    event?.preventDefault();
    const value = (preset ?? question).trim();
    if (!value || loading) return;
    setQuestion(value);
    setLoading(true);
    setServiceError(false);
    setTurns((items) => [...items, { question: value, answer: { text: "", citations: [], mode: "search" } }]);
    try {
      const response = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: value, language }),
      });
      if (response.status === 429) {
        setTurns((items) => {
          const next = [...items];
          next[next.length - 1] = { question: value, answer: { text: t.rateLimited as string, citations: [], mode: "search", warning: t.disclaimer as string } };
          return next;
        });
        return;
      }
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "Request failed");
      setTurns((items) => {
        const next = [...items];
        next[next.length - 1] = { question: value, answer: result as Answer };
        return next;
      });
      setQuestion("");
    } catch {
      setServiceError(true);
      setTurns((items) => {
        const next = [...items];
        next[next.length - 1] = {
          question: value,
          answer: { text: t.noAnswer as string, citations: [], mode: "search", warning: t.disclaimer as string },
        };
        return next;
      });
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
      <header className="topbar">
        <a className="brand" href="#home" aria-label="CivicLens home">
          <BrandMark />
          <span className="brand-name">Civic<span>Lens</span></span>
        </a>
        <div className="topbar-right">
          <span className="pilot-pill"><span className="pilot-dot" />{t.pilot}</span>
          <div className="language-switch" aria-label="Choose language">
            <button className={language === "en" ? "selected" : ""} onClick={() => setLanguage("en")} aria-pressed={language === "en"}>EN</button>
            <button className={language === "ta" ? "selected" : ""} onClick={() => setLanguage("ta")} aria-pressed={language === "ta"}>தமிழ்</button>
          </div>
        </div>
      </header>

      <main id="home">
        <section className={`hero ${turns.length ? "hero-compact" : ""}`}>
          <div className="hero-orb orb-one" />
          <div className="hero-orb orb-two" />
          <div className="hero-content">
            <div className="eyebrow"><span className="eyebrow-line" />{t.eyebrow}</div>
            <h1>{(t.headline as string).split("\n").map((line) => <span key={line}>{line}</span>)}</h1>
            <p className="hero-intro">{t.intro}</p>
            <form className="ask-box" onSubmit={(event) => submitQuestion(event)}>
              <div className="ask-topline">
                <span className="ask-symbol"><BrandMark /></span>
                <textarea
                  ref={inputRef}
                  rows={2}
                  maxLength={1200}
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey) {
                      event.preventDefault();
                      void submitQuestion();
                    }
                  }}
                  placeholder={t.placeholder as string}
                  aria-label={t.placeholder as string}
                />
              </div>
              <div className="ask-bottomline">
                <span className="ask-hint"><span className="sparkle">✦</span>{language === "en" ? "Clear, sourced guidance" : "தெளிவான ஆதாரத் தகவல்"}</span>
                <button className="submit-button" type="submit" disabled={loading || !question.trim()}>
                  {loading ? <span className="spinner" /> : <span>{t.ask}</span>}
                  {!loading && <span className="arrow">↗</span>}
                </button>
              </div>
            </form>
            <p className="privacy-note"><span className="lock-icon">⌑</span><span>{t.privacy as string} <a href="https://ai.google.dev/gemini-api/terms" target="_blank" rel="noreferrer">{t.providerTerms as string} ↗</a></span></p>
          </div>
          <div className="hero-side" aria-hidden="true">
            <div className="orbit orbit-a" /><div className="orbit orbit-b" />
            <div className="lens-art"><span className="lens-glow" /><div className="lens-inner"><BrandMark /></div></div>
            <div className="float-card float-card-top"><span className="float-check">✓</span><span><b>{language === "en" ? "Official sources" : "அதிகாரப்பூர்வ ஆதாரம்"}</b><small>{language === "en" ? "Evidence you can check" : "நீங்கள் சரிபார்க்கலாம்"}</small></span></div>
            <div className="float-card float-card-bottom"><span className="tamil-badge">அ</span><span><b>{language === "en" ? "Tamil + English" : "தமிழ் + ஆங்கிலம்"}</b><small>{language === "en" ? "Your language, your way" : "உங்கள் மொழியில்"}</small></span></div>
          </div>
        </section>

        <div className="trust-strip">
          <div className="trust-item"><span className="trust-icon trust-shield">✓</span><span><b>{t.trust}</b><small>{t.trustSub}</small></span></div>
          <span className="trust-divider" />
          <div className="trust-item"><span className="trust-icon trust-language">文</span><span><b>{language === "en" ? "Tamil-first by design" : "தமிழுக்கு முன்னுரிமை"}</b><small>{language === "en" ? "English is here when you need it" : "ஆங்கிலமும் கிடைக்கும்"}</small></span></div>
          <span className="trust-divider" />
          <div className="not-government"><span className="info-icon">i</span>{t.notGov}</div>
        </div>

        <section className="workspace">
          {!turns.length ? (
            <div className="discovery-grid">
              <div className="suggestions-panel">
                <div className="section-kicker">{language === "en" ? "A GOOD PLACE TO BEGIN" : "இங்கே தொடங்கலாம்"}</div>
                <h2>{t.prompt}</h2>
                <div className="suggestion-list">
                  {suggestions.map((item) => (
                    <button className="suggestion" key={item.key} onClick={() => void submitQuestion(undefined, (t.prompts as string[])[item.key])}>
                      <span className={`suggestion-icon ${item.tone}`}>{item.icon}</span>
                      <span>{(t.prompts as string[])[item.key]}</span>
                  <span className="suggestion-arrow">↗</span>
                    </button>
                  ))}
                </div>
              </div>
              <aside className="sources-panel">
                <div className="panel-heading">
                  <div><div className="section-kicker">{t.sourceCount}</div><h2>{t.sources}</h2></div>
                  <span className="source-stack"><i /><i /><i /></span>
                </div>
                <p className="panel-intro">{t.sourceIntro}</p>
                {sources.length ? <div className="source-list">
                  {sources.slice(0, 3).map((source) => <a className="source-row" href={source.url} key={source.id} target="_blank" rel="noreferrer">
                    <span className="source-favicon">↗</span><span className="source-row-copy"><b>{source.title}</b><small>{source.owner}</small></span><span className="external-arrow">↗</span>
                  </a>)}
                </div> : <div className="source-loading">{serviceError ? (language === "en" ? "Start the local API to load sources." : "ஆதாரங்களை ஏற்ற API-ஐத் தொடங்குங்கள்.") : t.sourceEmpty}</div>}
                <div className="source-footnote"><span className="footnote-dot" />{language === "en" ? "Each answer links back to where it came from" : "ஒவ்வொரு பதிலும் அதன் மூலத்துடன் இணைக்கப்படும்"}</div>
              </aside>
            </div>
          ) : (
            <section className="conversation" aria-live="polite">
              <div className="conversation-header"><div><div className="section-kicker">{language === "en" ? "YOUR QUESTION" : "உங்கள் கேள்வி"}</div><h2>{currentTurn?.question}</h2></div><button className="text-button" onClick={reset}>{t.clear} <span>↺</span></button></div>
              {currentTurn && <article className="answer-card">
                <div className="answer-heading"><span className="answer-avatar"><BrandMark /></span><span className="answer-label">{t.answerLabel}</span><span className="answer-mode">{currentTurn.answer.mode === "ai" ? t.aiMode : t.searchMode}</span></div>
                <p className="answer-text">{loading ? t.loading : currentTurn.answer.text}</p>
                {loading && <div className="loading-lines"><i /><i /><i /></div>}
                {!!currentTurn.answer.warning && !loading && <div className="answer-warning"><span>i</span>{currentTurn.answer.warning}</div>}
                {!loading && !!currentTurn.answer.notices?.length && <ChangeNotices notices={currentTurn.answer.notices} t={t} />}
                {!loading && !!currentTurn.answer.citations.length && <div className="citations-block">
                  <div className="citation-title">{t.evidence}</div>
                  <div className="citation-list">{currentTurn.answer.citations.map((citation) => <a className="citation-card" href={citation.url} key={citation.id} target="_blank" rel="noreferrer">
                    <span className="citation-number">↗</span><span className="citation-copy"><b>{citation.title}</b><small>{citation.owner}{citation.locator ? ` · ${citation.locator}` : ""}{citation.desk_checked_at ? ` · ${language === "ta" ? "மேசை ஆய்வு" : "Desk review"} ${citation.desk_checked_at}` : ""}</small></span><span className="citation-status">{citation.human_verified_at ? (language === "ta" ? `மனிதர் சரிபார்த்தது ${citation.human_verified_at}` : `Human checked ${citation.human_verified_at}`) : (language === "ta" ? "அதிகாரப்பூர்வ ஆதாரம் · விதிகள் சரிபார்க்கப்படவில்லை" : citation.status || t.sourceStatus)}</span>
                  </a>)}</div>
                </div>}
                {!loading && (!!currentTurn.answer.citations.length || !!currentTurn.answer.notices?.length) && <button className="text-button print-button" onClick={() => window.print()}>{t.print} <span>⎙</span></button>}
              </article>}
              {currentTurn && !loading && <PrintChecklist turn={currentTurn} t={t} />}
              <form className="followup-box" onSubmit={(event) => submitQuestion(event)}>
                <textarea rows={1} value={question} onChange={(event) => setQuestion(event.target.value)} placeholder={t.askAgain as string} aria-label={t.askAgain as string} />
                <button type="submit" disabled={loading || !question.trim()} aria-label={t.ask as string}>↗</button>
              </form>
              {serviceError && <p className="api-note">{language === "en" ? "The API is unavailable. Answers are not being sent to an AI service." : "API கிடைக்கவில்லை. பதில்கள் AI சேவைக்கு அனுப்பப்படவில்லை."}</p>}
            </section>
          )}
          {!turns.length && <section className="scheme-explorer">
            <div className="explorer-heading"><div><div className="section-kicker">{language === "en" ? "OFFICIAL DIRECTORY LEADS" : "அதிகாரப்பூர்வத் திட்டக் கோப்பகங்கள்"}</div><h2>{t.explore}</h2><p>{t.exploreIntro}</p></div><span className="explorer-count">{schemes.length.toString().padStart(2, "0")} <small>{language === "en" ? "PROGRAMS" : "திட்டங்கள்"}</small></span></div>
            <div className="scheme-cards">
              {schemes.map((scheme) => <article className="scheme-card" key={scheme.id}>
                <div className="scheme-card-top"><span className="scheme-icon">✳</span><span className="scheme-category">{scheme.category}</span></div>
                <h3>{scheme.title}</h3>
                <p className="scheme-department">{scheme.department}</p>
                <p className="scheme-overview">{scheme.overview}</p>
                <div className="scheme-card-footer"><span className="unverified-label"><i />{t.unverified}</span><a href={scheme.url} target="_blank" rel="noreferrer">{t.openDirectory} <span>↗</span></a></div>
              </article>)}
            </div>
          </section>}
          {!turns.length && !!changes.length && <ChangeList changes={changes} t={t} />}
        </section>

        <footer className="page-footer"><div className="footer-brand"><BrandMark /><span>CivicLens</span></div><p>{t.disclaimer}</p><a href="https://www.myscheme.gov.in/" target="_blank" rel="noreferrer">{language === "en" ? "Visit myScheme" : "myScheme-ஐப் பார்க்கவும்"} ↗</a></footer>
        {adminEnabled && <section className="admin-entry">
          <button className="admin-toggle" onClick={() => setShowAdmin((shown) => !shown)} aria-expanded={showAdmin}>{t.maintainer} <span>{showAdmin ? "−" : "+"}</span></button>
          {showAdmin && <div className="admin-panel">
            <div className="admin-panel-heading"><div><div className="section-kicker">CIVICLENS · INTERNAL</div><h2>{t.maintainer}</h2><p>{t.readOnly}</p></div><button className="text-button" onClick={() => { setShowAdmin(false); clearAdminSession(); }}>{t.closeOverview}</button></div>
            {!adminOverview && <form className="admin-auth" onSubmit={loadAdminOverview}>
              <label htmlFor="maintainer-token">{t.adminToken}</label>
              <div><input id="maintainer-token" type="password" autoComplete="off" value={adminToken} onChange={(event) => setAdminToken(event.target.value)} /><button type="submit" disabled={!adminToken.trim()}>{t.loadOverview}</button></div>
              {adminError && <p role="alert">{t.adminError}</p>}
            </form>}
            {adminOverview && <>
              <div className="admin-kpis"><div><b>{adminOverview.source_count}</b><small>{t.sources}</small></div><div><b>{adminOverview.human_verified_count}</b><small>{t.verified}</small></div><div><b>{adminOverview.review_pending_count}</b><small>{t.pendingReview}</small></div><div><b>{adminOverview.provider.configured ? `${adminOverview.provider.configured_keys} key(s)` : "Off"}</b><small>Gemini</small></div></div>
              <p className="admin-monitoring">{t.monitoringOff} {language === "en" ? "Provider status" : "சேவை நிலை"}: {adminOverview.provider.last_failure_category || (adminOverview.provider.last_request_succeeded === false ? "unavailable" : "no recent request")}</p>
              <div className="admin-source-list">{adminOverview.sources.map((source) => <div className="admin-source-row" key={source.id}><span><b>{source.title}</b><small>{source.owner} · {source.desk_checked_at ? `Desk review ${source.desk_checked_at}` : "No review date"}</small></span><em>{source.human_verified_at || t.pendingReview}</em></div>)}</div>
              <button className="text-button admin-clear" onClick={clearAdminSession}>{t.clearToken}</button>
            </>}
          </div>}
        </section>}
      </main>
    </div>
  );
}

export default App;
