import type { Copy } from "../copy";
import type { Citation } from "../types";

const suggestions = [
  { icon: "✦", tone: "lavender" },
  { icon: "⌂", tone: "mint" },
  { icon: "◷", tone: "sand" },
];

type Props = { t: Copy; sources: Citation[]; serviceError: boolean; onAsk: (question: string) => void };

/** Starting point before the first question: suggested questions and the source library. */
export function Discovery({ t, sources, serviceError, onAsk }: Props) {
  return (
    <div className="discovery-grid">
      <div className="suggestions-panel">
        <div className="section-kicker">{t.beginKicker}</div>
        <h2>{t.prompt}</h2>
        <div className="suggestion-list">
          {suggestions.map((item, index) => {
            const prompt = t.prompts[index];
            return (
              <button type="button" className="suggestion" key={item.tone} onClick={() => onAsk(prompt)}>
                <span className={`suggestion-icon ${item.tone}`}>{item.icon}</span>
                <span>{prompt}</span>
                <span className="suggestion-arrow">↗</span>
              </button>
            );
          })}
        </div>
      </div>
      <aside className="sources-panel">
        <div className="panel-heading">
          <div><div className="section-kicker">{t.sourceCount}</div><h2>{t.sources}</h2></div>
          <span className="source-stack"><i /><i /><i /></span>
        </div>
        <p className="panel-intro">{t.sourceIntro}</p>
        {sources.length ? (
          <div className="source-list">
            {sources.slice(0, 3).map((source) => (
              <a className="source-row" href={source.url} key={source.id} target="_blank" rel="noreferrer">
                <span className="source-favicon">↗</span>
                <span className="source-row-copy"><b>{source.title}</b><small>{source.owner}</small></span>
                <span className="external-arrow">↗</span>
              </a>
            ))}
          </div>
        ) : (
          <div className="source-loading">{serviceError ? t.startApi : t.sourceEmpty}</div>
        )}
        <div className="source-footnote"><span className="footnote-dot" />{t.linkedBack}</div>
      </aside>
    </div>
  );
}
