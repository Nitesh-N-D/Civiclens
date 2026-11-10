import { useState } from "react";
import type { FormEvent } from "react";
import { fetchAdminOverview, recordSourceCheck, supabaseSignIn, supabaseSignOut } from "../api";
import type { SignInConfig } from "../api";
import type { Copy } from "../copy";
import type { AdminOverview } from "../types";

const OUTCOMES = ["reachable", "changed", "unreachable", "manual_review"] as const;

function CheckForm({ t, overview, onSave }: { t: Copy; overview: AdminOverview; onSave: (source: string, outcome: string, note: string) => Promise<void> }) {
  const [source, setSource] = useState(overview.sources[0]?.id ?? "");
  const [outcome, setOutcome] = useState<string>("reachable");
  const [note, setNote] = useState("");
  const [state, setState] = useState<"idle" | "saving" | "saved" | "error">("idle");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setState("saving");
    try {
      await onSave(source, outcome, note.trim());
      setNote("");
      setState("saved");
    } catch {
      setState("error");
    }
  }

  return (
    <form className="admin-check" onSubmit={submit}>
      <h3>{t.recordCheck}</h3>
      <label>{t.sourceLabel}
        <select value={source} onChange={(event) => setSource(event.target.value)}>
          {overview.sources.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}
        </select>
      </label>
      <label>{t.outcomeLabel}
        <select value={outcome} onChange={(event) => setOutcome(event.target.value)}>
          {OUTCOMES.map((value) => <option key={value} value={value}>{t.outcomes[value]}</option>)}
        </select>
      </label>
      <label>{t.noteLabel}
        <input value={note} maxLength={500} onChange={(event) => setNote(event.target.value)} />
      </label>
      <button type="submit" disabled={state === "saving" || note.trim().length < 3 || !source}>{t.saveCheck}</button>
      {state === "saved" && <p role="status">{t.checkSaved}</p>}
      {state === "error" && <p role="alert">{t.checkError}</p>}
    </form>
  );
}

export function AdminPanel({ t, signIn }: { t: Copy; signIn: SignInConfig | null }) {
  const [open, setOpen] = useState(false);
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [error, setError] = useState(false);
  const [busy, setBusy] = useState(false);
  // Held in memory only; a reload signs this page out.
  const [session, setSession] = useState("");

  async function load(event: FormEvent) {
    event.preventDefault();
    setError(false);
    setBusy(true);
    try {
      const bearer = signIn ? await supabaseSignIn(signIn, email.trim(), password) : token;
      setPassword("");
      setOverview(await fetchAdminOverview(bearer));
      setSession(bearer);
    } catch {
      setOverview(null);
      setError(true);
    } finally {
      setBusy(false);
    }
  }

  async function saveCheck(source: string, outcome: string, note: string) {
    await recordSourceCheck(session, source, outcome, note);
    setOverview(await fetchAdminOverview(session));
  }

  function clear() {
    if (signIn && session) void supabaseSignOut(signIn, session);
    setToken("");
    setPassword("");
    setSession("");
    setOverview(null);
    setError(false);
  }

  const canSubmit = signIn ? !!email.trim() && !!password : !!token.trim();

  return (
    <section className="admin-entry">
      <button type="button" className="admin-toggle" onClick={() => setOpen((shown) => !shown)} aria-expanded={open}>{t.maintainer} <span>{open ? "−" : "+"}</span></button>
      {open && (
        <div className="admin-panel">
          <div className="admin-panel-heading">
            <div>
              <div className="section-kicker">CIVICLENS · INTERNAL</div>
              <h2>{t.maintainer}</h2>
              <p>{overview?.mutations_enabled ? `${t.signedInAs} ${overview.you?.email} · ${t.roleLabel}: ${overview.you?.role}` : t.readOnly}</p>
            </div>
            <button type="button" className="text-button" onClick={() => { setOpen(false); clear(); }}>{t.closeOverview}</button>
          </div>
          {!overview && (
            <form className="admin-auth" onSubmit={load}>
              {signIn ? (
                <>
                  <p className="admin-hint">{t.signInHint}</p>
                  <label htmlFor="maintainer-email">{t.email}</label>
                  <input id="maintainer-email" type="email" autoComplete="username" value={email} onChange={(event) => setEmail(event.target.value)} />
                  <label htmlFor="maintainer-password">{t.password}</label>
                  <div>
                    <input id="maintainer-password" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} />
                    <button type="submit" disabled={busy || !canSubmit}>{t.signIn}</button>
                  </div>
                  {error && <p role="alert">{t.signInError}</p>}
                </>
              ) : (
                <>
                  <label htmlFor="maintainer-token">{t.adminToken}</label>
                  <div>
                    <input id="maintainer-token" type="password" autoComplete="off" value={token} onChange={(event) => setToken(event.target.value)} />
                    <button type="submit" disabled={busy || !canSubmit}>{t.loadOverview}</button>
                  </div>
                  {error && <p role="alert">{t.adminError}</p>}
                </>
              )}
            </form>
          )}
          {overview && (
            <>
              <div className="admin-kpis">
                <div><b>{overview.source_count}</b><small>{t.sources}</small></div>
                <div><b>{overview.human_verified_count}</b><small>{t.verified}</small></div>
                <div><b>{overview.review_pending_count}</b><small>{t.pendingReview}</small></div>
                <div><b>{overview.provider.configured ? `${overview.provider.configured_keys} key(s)` : "Off"}</b><small>Gemini</small></div>
              </div>
              <p className="admin-monitoring">{overview.monitoring === "manual_checks" ? t.monitoringManual : t.monitoringOff} {t.providerStatus}: {overview.provider.state ?? overview.provider.last_failure_category ?? "unknown"}</p>
              {overview.mutations_enabled && <CheckForm t={t} overview={overview} onSave={saveCheck} />}
              {!!overview.recent_checks?.length && (
                <div className="admin-log">
                  <h3>{t.recentChecks}</h3>
                  <ul>{overview.recent_checks.map((check) => <li key={check.id}><b>{check.source_id}</b> · {t.outcomes[check.outcome as keyof Copy["outcomes"]] ?? check.outcome} · {check.note} <small>{check.checked_at.slice(0, 16).replace("T", " ")}</small></li>)}</ul>
                </div>
              )}
              {!!overview.recent_audit?.length && (
                <div className="admin-log">
                  <h3>{t.recentAudit}</h3>
                  <ul>{overview.recent_audit.map((entry) => <li key={entry.id}><b>{entry.action}</b> · {entry.entity_id} · {entry.actor} <small>{entry.created_at.slice(0, 16).replace("T", " ")}</small></li>)}</ul>
                </div>
              )}
              <div className="admin-source-list">
                {overview.sources.map((source) => (
                  <div className="admin-source-row" key={source.id}>
                    <span><b>{source.title}</b><small>{source.owner} · {source.desk_checked_at ? `${t.deskReview} ${source.desk_checked_at}` : "—"}</small></span>
                    <em>{source.human_verified_at || t.pendingReview}</em>
                  </div>
                ))}
              </div>
              <button type="button" className="text-button admin-clear" onClick={clear}>{signIn ? t.signOut : t.clearToken}</button>
            </>
          )}
        </div>
      )}
    </section>
  );
}
