import { useState } from "react";
import type { FormEvent } from "react";
import { fetchAdminOverview } from "../api";
import type { Copy } from "../copy";
import type { AdminOverview } from "../types";

export function AdminPanel({ t }: { t: Copy }) {
  const [open, setOpen] = useState(false);
  const [token, setToken] = useState("");
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [error, setError] = useState(false);

  async function load(event: FormEvent) {
    event.preventDefault();
    setError(false);
    try {
      setOverview(await fetchAdminOverview(token));
    } catch {
      setOverview(null);
      setError(true);
    }
  }

  function clear() {
    setToken("");
    setOverview(null);
    setError(false);
  }

  return (
    <section className="admin-entry">
      <button type="button" className="admin-toggle" onClick={() => setOpen((shown) => !shown)} aria-expanded={open}>{t.maintainer} <span>{open ? "−" : "+"}</span></button>
      {open && (
        <div className="admin-panel">
          <div className="admin-panel-heading">
            <div><div className="section-kicker">CIVICLENS · INTERNAL</div><h2>{t.maintainer}</h2><p>{t.readOnly}</p></div>
            <button type="button" className="text-button" onClick={() => { setOpen(false); clear(); }}>{t.closeOverview}</button>
          </div>
          {!overview && (
            <form className="admin-auth" onSubmit={load}>
              <label htmlFor="maintainer-token">{t.adminToken}</label>
              <div>
                <input id="maintainer-token" type="password" autoComplete="off" value={token} onChange={(event) => setToken(event.target.value)} />
                <button type="submit" disabled={!token.trim()}>{t.loadOverview}</button>
              </div>
              {error && <p role="alert">{t.adminError}</p>}
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
              <p className="admin-monitoring">{t.monitoringOff} {t.providerStatus}: {overview.provider.state ?? overview.provider.last_failure_category ?? "unknown"}</p>
              <div className="admin-source-list">
                {overview.sources.map((source) => (
                  <div className="admin-source-row" key={source.id}>
                    <span><b>{source.title}</b><small>{source.owner} · {source.desk_checked_at ? `${t.deskReview} ${source.desk_checked_at}` : "—"}</small></span>
                    <em>{source.human_verified_at || t.pendingReview}</em>
                  </div>
                ))}
              </div>
              <button type="button" className="text-button admin-clear" onClick={clear}>{t.clearToken}</button>
            </>
          )}
        </div>
      )}
    </section>
  );
}
