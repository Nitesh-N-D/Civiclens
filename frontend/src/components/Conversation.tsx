import type { FormEvent } from "react";
import type { Copy } from "../copy";
import type { Citation, Turn } from "../types";
import { BrandMark } from "./BrandMark";
import { ChangeNotices } from "./ChangeNotices";
import { PrintChecklist } from "./PrintChecklist";

function citationStatus(citation: Citation, t: Copy) {
  if (citation.human_verified_at) return `${t.humanChecked} ${citation.human_verified_at}`;
  return t.rulesUnchecked || citation.status || t.sourceStatus;
}

export function AnswerCard({ turn, t, showPrint }: { turn: Turn; t: Copy; showPrint: boolean }) {
  const { answer } = turn;
  const loading = !!turn.pending;
  return (
    <article className="answer-card">
      <div className="answer-heading">
        <span className="answer-avatar"><BrandMark /></span>
        <span className="answer-label">{t.answerLabel}</span>
        <span className="answer-mode">{answer.mode === "ai" ? t.aiMode : t.searchMode}</span>
      </div>
      <p className="answer-text">{loading ? t.loading : answer.text}</p>
      {loading && <div className="loading-lines"><i /><i /><i /></div>}
      {!!answer.warning && !loading && <div className="answer-warning"><span>i</span>{answer.warning}</div>}
      {!loading && !!answer.notices?.length && <ChangeNotices notices={answer.notices} t={t} />}
      {!loading && !!answer.citations.length && (
        <div className="citations-block">
          <div className="citation-title">{t.evidence}</div>
          <div className="citation-list">
            {answer.citations.map((citation) => (
              <a className="citation-card" href={citation.url} key={citation.id} target="_blank" rel="noreferrer">
                <span className="citation-number">↗</span>
                <span className="citation-copy">
                  <b>{citation.title}</b>
                  <small>{citation.owner}{citation.locator ? ` · ${citation.locator}` : ""}{citation.desk_checked_at ? ` · ${t.deskReview} ${citation.desk_checked_at}` : ""}</small>
                </span>
                <span className="citation-status">{citationStatus(citation, t)}</span>
              </a>
            ))}
          </div>
        </div>
      )}
      {showPrint && !loading && (!!answer.citations.length || !!answer.notices?.length) && (
        <button type="button" className="text-button print-button" onClick={() => window.print()}>{t.print} <span>⎙</span></button>
      )}
    </article>
  );
}

type Props = {
  t: Copy;
  turns: Turn[];
  question: string;
  loading: boolean;
  serviceError: boolean;
  onQuestion: (value: string) => void;
  onSubmit: (event?: FormEvent) => void;
  onReset: () => void;
};

/**
 * The questions asked in this visit, newest last. History lives only in memory: it is gone on
 * reload and is never sent to the server or stored.
 */
export function Conversation({ t, turns, question, loading, serviceError, onQuestion, onSubmit, onReset }: Props) {
  const current = turns.at(-1);
  const earlier = turns.slice(0, -1);
  return (
    <section className="conversation" aria-live="polite">
      {earlier.map((turn, index) => (
        <div className="earlier-turn" key={`${index}-${turn.question}`}>
          <div className="section-kicker">{t.earlierQuestion}</div>
          <h3>{turn.question}</h3>
          <AnswerCard turn={turn} t={t} showPrint={false} />
        </div>
      ))}
      <div className="conversation-header">
        <div><div className="section-kicker">{t.yourQuestion}</div><h2>{current?.question}</h2></div>
        <button type="button" className="text-button" onClick={onReset}>{t.clear} <span>↺</span></button>
      </div>
      {current && <AnswerCard turn={current} t={t} showPrint />}
      {current && !current.pending && <PrintChecklist turn={current} t={t} />}
      <form className="followup-box" onSubmit={onSubmit}>
        <textarea rows={1} value={question} onChange={(event) => onQuestion(event.target.value)} placeholder={t.askAgain} aria-label={t.askAgain}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              onSubmit();
            }
          }} />
        <button type="submit" disabled={loading || !question.trim()} aria-label={t.ask}>↗</button>
      </form>
      {serviceError && <p className="api-note">{t.apiDown}</p>}
    </section>
  );
}
