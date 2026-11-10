import type { Copy } from "./copy";
import type { Turn } from "./types";

/**
 * Print-only checklist for helpers (family members, e-Sevai staff, volunteers).
 * It contains the general question, the cited answer and official links — no personal data.
 */
export function PrintChecklist({ turn, t }: { turn: Turn; t: Copy }) {
  const printed = new Date().toISOString().slice(0, 10);
  return (
    <section className="print-checklist" aria-hidden="true">
      <h1>{t.printTitle}</h1>
      <p className="print-meta">{printed} · {t.notGov}</p>
      <h2>{t.printQuestion}</h2>
      <p>{turn.question}</p>
      <h2>{t.printAnswer}</h2>
      <p className="print-answer">{turn.answer.text}</p>
      {!!turn.answer.notices?.length && <ul>
        {turn.answer.notices.map((change) => <li key={change.id}><b>{change.scheme}</b> ({change.status === "official" ? t.changeOfficial : t.changeReported}): {change.summary} {change.source_url}</li>)}
      </ul>}
      {!!turn.answer.citations.length && <>
        <h2>{t.printSources}</h2>
        <ol>
          {turn.answer.citations.map((citation) => <li key={citation.id}>
            <b>{citation.title}</b> — {citation.owner}<br />{citation.url}
            {citation.desk_checked_at ? <> · {t.checked} {citation.desk_checked_at}</> : null}
          </li>)}
        </ol>
      </>}
      <h2>{t.printSteps}</h2>
      <ul className="print-steps">
        {(t.printStepsList as string[]).map((step) => <li key={step}>☐ {step}</li>)}
      </ul>
      {turn.answer.warning && <p className="print-warning">{turn.answer.warning}</p>}
      <p className="print-meta">{t.printFooter} {t.disclaimer}</p>
    </section>
  );
}
