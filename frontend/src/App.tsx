import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";

type Language = "en" | "ta";
type Citation = { id: string; title: string; url: string; owner: string; locator?: string; status: string };
type Answer = { text: string; citations: Citation[]; mode: "ai" | "search"; warning?: string };
type Turn = { question: string; answer: Answer };

const copy = {
  en: {
    eyebrow: "PUBLIC SERVICES, MADE CLEARER",
    headline: "A clearer path to\npublic services.",
    intro: "Understand schemes and services in plain language, with official sources close at hand.",
    placeholder: "Ask about a scheme, service, or next step…",
    ask: "Ask CivicLens",
    prompt: "Try asking",
    prompts: ["I’m starting college. What support can I explore?", "How do I apply for an income certificate?", "What should I know about old-age pension schemes?"],
    trust: "Answers are grounded in official sources",
    trustSub: "Check the source and date before you act.",
    pilot: "Tamil Nadu pilot",
    notGov: "Independent information service · Not a government website",
    sources: "Official sources",
    sourceIntro: "Start with verified government portals and scheme directories.",
    sourceCount: "SOURCE LIBRARY",
    sourceEmpty: "Source library is loading…",
    askAgain: "Ask another question",
    evidence: "Evidence & links",
    answerLabel: "CIVICLENS EXPLAINED",
    loading: "Looking through the available official information…",
    privacy: "Please don’t enter Aadhaar numbers, bank details, or private documents. This pilot is for general questions and does not determine official eligibility.",
    disclaimer: "Information aid only. Scheme rules can change; confirm details with the responsible department before applying.",
    sourceStatus: "Directory source",
    searchMode: "Source search",
    aiMode: "AI explanation",
    clear: "Start over",
    noAnswer: "I couldn’t find enough reviewed information to answer that safely. Try an official source below or ask a narrower question.",
  },
  ta: {
    eyebrow: "அரசுச் சேவைகள் — எளிய விளக்கம்",
    headline: "அரசுச் சேவைகளை\nஎளிதாகப் புரிந்துகொள்ளுங்கள்.",
    intro: "திட்டங்களையும் சேவைகளையும் எளிய மொழியில் அறிந்து, அதிகாரப்பூர்வ ஆதாரங்களுடன் அடுத்த படியைத் தெரிந்துகொள்ளுங்கள்.",
    placeholder: "திட்டம், சேவை அல்லது அடுத்த படி பற்றி கேளுங்கள்…",
    ask: "CivicLens-இடம் கேளுங்கள்",
    prompt: "இவற்றில் கேளுங்கள்",
    prompts: ["கல்லூரி சேரும் எனக்கு என்ன உதவிகள் உள்ளன?", "வருமானச் சான்றிதழுக்கு எப்படி விண்ணப்பிப்பது?", "முதியோர் ஓய்வூதியத் திட்டங்கள் பற்றி சொல்லுங்கள்"],
    trust: "அதிகாரப்பூர்வ ஆதாரங்களை அடிப்படையாகக் கொண்ட பதில்கள்",
    trustSub: "செயல்படுவதற்கு முன் ஆதாரத்தையும் தேதியையும் சரிபார்க்கவும்.",
    pilot: "தமிழ்நாடு முன்னோட்டம்",
    notGov: "சுயாதீன தகவல் சேவை · அரசு இணையதளம் அல்ல",
    sources: "அதிகாரப்பூர்வ ஆதாரங்கள்",
    sourceIntro: "அரசுத் தளங்கள் மற்றும் திட்டத் தகவல்களிலிருந்து தொடங்குங்கள்.",
    sourceCount: "ஆதாரத் தொகுப்பு",
    sourceEmpty: "ஆதாரத் தொகுப்பு ஏற்றப்படுகிறது…",
    askAgain: "மற்றொரு கேள்வி கேளுங்கள்",
    evidence: "ஆதாரங்கள் மற்றும் இணைப்புகள்",
    answerLabel: "CIVICLENS விளக்கம்",
    loading: "கிடைக்கும் அதிகாரப்பூர்வ தகவல்களைத் தேடுகிறோம்…",
    privacy: "ஆதார் எண், வங்கித் தகவல் அல்லது தனிப்பட்ட ஆவணங்களை உள்ளிட வேண்டாம். இது பொதுவான கேள்விகளுக்கான முன்னோட்டம்; அதிகாரப்பூர்வத் தகுதியைத் தீர்மானிக்காது.",
    disclaimer: "தகவல் உதவி மட்டுமே. திட்ட விதிகள் மாறலாம்; விண்ணப்பிக்கும் முன் சம்பந்தப்பட்ட துறையிடம் உறுதிப்படுத்தவும்.",
    sourceStatus: "திட்டத் தகவல் ஆதாரம்",
    searchMode: "ஆதாரத் தேடல்",
    aiMode: "AI விளக்கம்",
    clear: "புதிதாகத் தொடங்குங்கள்",
    noAnswer: "பாதுகாப்பாகப் பதிலளிக்கத் தேவையான சரிபார்க்கப்பட்ட தகவல் கிடைக்கவில்லை. கீழே உள்ள அதிகாரப்பூர்வ ஆதாரத்தைப் பார்க்கவும் அல்லது குறிப்பான கேள்வியைக் கேட்கவும்.",
  },
} satisfies Record<Language, Record<string, string | string[]>>;

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
  const [language, setLanguage] = useState<Language>("en");
  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [loading, setLoading] = useState(false);
  const [sources, setSources] = useState<Citation[]>([]);
  const [serviceError, setServiceError] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const t = copy[language];
  const currentTurn = turns.at(-1);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  useEffect(() => {
    fetch("/api/sources")
      .then((response) => (response.ok ? response.json() : Promise.reject()))
      .then((data: { sources: Citation[] }) => setSources(data.sources ?? []))
      .catch(() => setServiceError(true));
  }, []);

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
          answer: { text: t.noAnswer as string, citations: sources, mode: "search", warning: t.disclaimer as string },
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
            <p className="privacy-note"><span className="lock-icon">⌑</span>{t.privacy}</p>
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
                {!loading && !!currentTurn.answer.citations.length && <div className="citations-block">
                  <div className="citation-title">{t.evidence}</div>
                  <div className="citation-list">{currentTurn.answer.citations.map((citation) => <a className="citation-card" href={citation.url} key={citation.id} target="_blank" rel="noreferrer">
                    <span className="citation-number">↗</span><span className="citation-copy"><b>{citation.title}</b><small>{citation.owner}{citation.locator ? ` · ${citation.locator}` : ""}</small></span><span className="citation-status">{citation.status || t.sourceStatus}</span>
                  </a>)}</div>
                </div>}
              </article>}
              <form className="followup-box" onSubmit={(event) => submitQuestion(event)}>
                <textarea rows={1} value={question} onChange={(event) => setQuestion(event.target.value)} placeholder={t.askAgain as string} aria-label={t.askAgain as string} />
                <button type="submit" disabled={loading || !question.trim()} aria-label={t.ask as string}>↗</button>
              </form>
              {serviceError && <p className="api-note">{language === "en" ? "The API is unavailable. Answers are not being sent to an AI service." : "API கிடைக்கவில்லை. பதில்கள் AI சேவைக்கு அனுப்பப்படவில்லை."}</p>}
            </section>
          )}
        </section>

        <footer className="page-footer"><div className="footer-brand"><BrandMark /><span>CivicLens</span></div><p>{t.disclaimer}</p><a href="https://www.myscheme.gov.in/" target="_blank" rel="noreferrer">{language === "en" ? "Visit myScheme" : "myScheme-ஐப் பார்க்கவும்"} ↗</a></footer>
      </main>
    </div>
  );
}

export default App;
