import type { Copy } from "./copy";
import type { Change } from "./types";

function ChangeBadge({ change, t }: { change: Change; t: Copy }) {
  return <span className={`change-badge change-${change.status}`}>{change.status === "official" ? t.changeOfficial : t.changeReported}</span>;
}

/** Notices shown beside an answer. They are context, never answer evidence. */
export function ChangeNotices({ notices, t }: { notices: Change[]; t: Copy }) {
  return (
    <div className="change-notices" role="note" aria-label={t.changesTitle}>
      {notices.map((change) => (
        <div className="change-notice" key={change.id}>
          <div className="change-notice-top"><b>{change.scheme}</b><ChangeBadge change={change} t={t} /></div>
          <p>{change.summary}</p>
          <a href={change.source_url} target="_blank" rel="noreferrer">{change.source_title} ↗</a>
          <small> · {t.checked} {change.checked_at}</small>
        </div>
      ))}
    </div>
  );
}

export function ChangeList({ changes, t }: { changes: Change[]; t: Copy }) {
  return (
    <section className="change-list">
      <div className="section-kicker">{t.changesTitle.toUpperCase()}</div>
      <h2>{t.changesTitle}</h2>
      <p className="panel-intro">{t.changesIntro}</p>
      <ChangeNotices notices={changes} t={t} />
    </section>
  );
}
