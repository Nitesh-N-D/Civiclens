import type { FormEvent, RefObject } from "react";
import type { Copy } from "../copy";
import { BrandMark } from "./BrandMark";

type Props = {
  t: Copy;
  compact: boolean;
  question: string;
  loading: boolean;
  inputRef: RefObject<HTMLTextAreaElement | null>;
  onQuestion: (value: string) => void;
  onSubmit: (event?: FormEvent) => void;
};

export function Hero({ t, compact, question, loading, inputRef, onQuestion, onSubmit }: Props) {
  return (
    <section className={`hero ${compact ? "hero-compact" : ""}`}>
      <div className="hero-orb orb-one" />
      <div className="hero-orb orb-two" />
      <div className="hero-content">
        <div className="eyebrow"><span className="eyebrow-line" />{t.eyebrow}</div>
        <h1>{t.headline.split("\n").map((line) => <span key={line}>{line}</span>)}</h1>
        <p className="hero-intro">{t.intro}</p>
        <form className="ask-box" onSubmit={onSubmit}>
          <div className="ask-topline">
            <span className="ask-symbol"><BrandMark /></span>
            <textarea
              ref={inputRef}
              rows={2}
              maxLength={1200}
              value={question}
              onChange={(event) => onQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  onSubmit();
                }
              }}
              placeholder={t.placeholder}
              aria-label={t.placeholder}
            />
          </div>
          <div className="ask-bottomline">
            <span className="ask-hint"><span className="sparkle">✦</span>{t.askHint}</span>
            <button className="submit-button" type="submit" disabled={loading || !question.trim()}>
              {loading ? <span className="spinner" /> : <span>{t.ask}</span>}
              {!loading && <span className="arrow">↗</span>}
            </button>
          </div>
        </form>
        <p className="privacy-note"><span className="lock-icon">⌑</span><span>{t.privacy} <a href="https://ai.google.dev/gemini-api/terms" target="_blank" rel="noreferrer">{t.providerTerms} ↗</a></span></p>
      </div>
      <div className="hero-side" aria-hidden="true">
        <div className="orbit orbit-a" /><div className="orbit orbit-b" />
        <div className="lens-art"><span className="lens-glow" /><div className="lens-inner"><BrandMark /></div></div>
        <div className="float-card float-card-top"><span className="float-check">✓</span><span><b>{t.floatSources}</b><small>{t.floatSourcesSub}</small></span></div>
        <div className="float-card float-card-bottom"><span className="tamil-badge">அ</span><span><b>{t.floatLanguages}</b><small>{t.floatLanguagesSub}</small></span></div>
      </div>
    </section>
  );
}

export function TrustStrip({ t }: { t: Copy }) {
  return (
    <div className="trust-strip">
      <div className="trust-item"><span className="trust-icon trust-shield">✓</span><span><b>{t.trust}</b><small>{t.trustSub}</small></span></div>
      <span className="trust-divider" />
      <div className="trust-item"><span className="trust-icon trust-language">文</span><span><b>{t.tamilFirst}</b><small>{t.tamilFirstSub}</small></span></div>
      <span className="trust-divider" />
      <div className="not-government"><span className="info-icon">i</span>{t.notGov}</div>
    </div>
  );
}
