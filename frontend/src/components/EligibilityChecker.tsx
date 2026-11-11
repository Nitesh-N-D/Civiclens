import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { checkEligibility, compareSchemes, fetchEligibilityQuestions } from "../api";
import type { Copy, Language } from "../copy";
import type { Citation, ComparisonRow, EligibilityQuestion, EligibilityResult, SchemeCard } from "../types";

const label = (map: Record<string, string>, key: string) => map[key] ?? key;

/**
 * Voluntary screening against the conditions quoted from each scheme's official summary.
 * Answers live only in this component's state; nothing is saved in the browser. The parent keys
 * it by language, so switching language starts a fresh screening in that language.
 */
export function EligibilityChecker({ t, language, schemes }: { t: Copy; language: Language; schemes: SchemeCard[] }) {
  const [questions, setQuestions] = useState<EligibilityQuestion[]>([]);
  const [profile, setProfile] = useState<Record<string, string>>({});
  const [results, setResults] = useState<EligibilityResult[] | null>(null);
  const [sources, setSources] = useState<Citation[]>([]);
  const [error, setError] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetchEligibilityQuestions(language).then(setQuestions).catch(() => setQuestions([]));
  }, [language]);

  const screenable = schemes.filter((scheme) => scheme.eligibility_enabled);
  if (!screenable.length || !questions.length) return null;
  const titleOf = (id: string) => schemes.find((scheme) => scheme.id === id)?.title ?? id;
  const sourceOf = (id: string) => sources.find((source) => source.id === id);

  async function run(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(false);
    try {
      const data = await checkEligibility(profile, language);
      setResults(data.results);
      setSources(data.sources);
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  }

  function clear() {
    setProfile({});
    setResults(null);
  }

  return (
    <section className="eligibility" aria-labelledby="eligibility-title">
      <div className="section-kicker">{t.eligibilityKicker}</div>
      <h2 id="eligibility-title">{t.eligibilityTitle}</h2>
      <p className="panel-intro">{t.eligibilityIntro}</p>
      <form className="eligibility-form" onSubmit={(event) => void run(event)}>
        {questions.map((question) => (
          <label key={question.field} className="eligibility-field">
            <span className="field-label">{label(t.fieldLabels, question.field)}</span>
            <select value={profile[question.field] ?? ""}
              onChange={(event) => setProfile((current) => ({ ...current, [question.field]: event.target.value }))}>
              <option value="">{t.preferNot}</option>
              {question.options.map((option) => <option key={option} value={option}>{label(t.optionLabels, option)}</option>)}
            </select>
            <small><b>{t.whyAsked}:</b> {question.purpose}</small>
          </label>
        ))}
        <div className="eligibility-actions">
          <button type="submit" className="submit-button" disabled={busy}>{t.eligibilityRun}</button>
          <button type="button" className="secondary-button" onClick={clear}>{t.eligibilityReset}</button>
        </div>
      </form>
      {error && <p className="error-note" role="alert">{t.eligibilityError}</p>}
      {results && (
        <div className="eligibility-results" aria-live="polite">
          <p className="caveat">{t.eligibilityCaveat}</p>
          {results.map((result) => {
            const source = sourceOf(result.guidance.source_id);
            return (
              <article key={result.scheme_id} className={`eligibility-card status-${result.status}`}>
                <header>
                  <h3>{titleOf(result.scheme_id)}</h3>
                  <span className="status-badge">{label(t.statusLabels, result.status)}</span>
                </header>
                <h4>{t.criteriaHeading}</h4>
                <ul className="criteria-list">
                  {result.criteria.map((criterion) => (
                    <li key={criterion.id} className={`outcome-${criterion.outcome}`}>
                      <span className="outcome-mark" aria-hidden="true">{criterion.outcome === "met" ? "✓" : criterion.outcome === "not_met" ? "✕" : "?"}</span>
                      <span>{criterion.label} — <i>{label(t.outcomeLabels, criterion.outcome)}</i></span>
                    </li>
                  ))}
                </ul>
                {!!result.documents.length && <>
                  <h4>{t.documentsHeading}</h4>
                  <ul className="document-list">
                    {result.documents.map((document) => <li key={document.criterion_id}>☐ <b>{document.name}</b><br /><small>{document.reason}</small></li>)}
                  </ul>
                  <p className="field-note">{t.documentNote}</p>
                </>}
                <h4>{t.guidanceHeading}</h4>
                <p>{result.guidance.route}</p>
                <ol className="guidance-steps">{result.guidance.steps.map((step) => <li key={step}>{step}</li>)}</ol>
                <p><b>{t.contactLabel}:</b> {result.guidance.contact}</p>
                {source && <p className="field-note">{t.sourceLabel}: <a href={source.url} target="_blank" rel="noreferrer">{source.title} ↗</a>{source.desk_checked_at ? <> · {t.checked} {source.desk_checked_at}</> : null}</p>}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

/** Side-by-side conditions, documents and routes; every column links to its official source. */
export function SchemeComparison({ t, language, schemes }: { t: Copy; language: Language; schemes: SchemeCard[] }) {
  const screenable = schemes.filter((scheme) => scheme.eligibility_enabled);
  const [selected, setSelected] = useState<string[]>([]);
  const [rows, setRows] = useState<ComparisonRow[]>([]);
  const [sources, setSources] = useState<Citation[]>([]);

  if (screenable.length < 2) return null;
  const titleOf = (id: string) => schemes.find((scheme) => scheme.id === id)?.title ?? id;

  function toggle(id: string) {
    setSelected((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id].slice(-4));
  }

  async function run() {
    try {
      const data = await compareSchemes(selected, language);
      setRows(data.schemes);
      setSources(data.sources);
    } catch {
      setRows([]);
    }
  }

  return (
    <section className="comparison" aria-labelledby="compare-title">
      <h2 id="compare-title">{t.compareTitle}</h2>
      <fieldset className="compare-picker">
        <legend>{t.compareSelect}</legend>
        {screenable.map((scheme) => (
          <label key={scheme.id}><input type="checkbox" checked={selected.includes(scheme.id)} onChange={() => toggle(scheme.id)} /> {scheme.title}</label>
        ))}
      </fieldset>
      <button type="button" className="secondary-button" disabled={selected.length < 2} onClick={() => void run()}>{t.compareRun}</button>
      {rows.length > 1 && (
        <div className="compare-scroll">
          <table className="compare-table">
            <thead><tr><th scope="col" />{rows.map((row) => <th scope="col" key={row.scheme_id}>{titleOf(row.scheme_id)}</th>)}</tr></thead>
            <tbody>
              <tr><th scope="row">{t.compareConditions}</th>{rows.map((row) => <td key={row.scheme_id}><ul>{row.criteria.map((item) => <li key={item}>{item}</li>)}</ul></td>)}</tr>
              <tr><th scope="row">{t.compareDocuments}</th>{rows.map((row) => <td key={row.scheme_id}><ul>{row.documents.map((item) => <li key={item}>{item}</li>)}</ul></td>)}</tr>
              <tr><th scope="row">{t.compareRoute}</th>{rows.map((row) => <td key={row.scheme_id}>{row.route}</td>)}</tr>
              <tr><th scope="row">{t.compareContact}</th>{rows.map((row) => <td key={row.scheme_id}>{row.contact}</td>)}</tr>
              <tr><th scope="row">{t.sourceLabel}</th>{rows.map((row) => {
                const source = sources.find((item) => item.id === row.source_id);
                return <td key={row.scheme_id}>{source ? <a href={source.url} target="_blank" rel="noreferrer">{source.title} ↗</a> : null}</td>;
              })}</tr>
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
