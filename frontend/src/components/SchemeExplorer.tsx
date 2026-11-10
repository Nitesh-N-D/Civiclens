import { useMemo, useState } from "react";
import type { Copy } from "../copy";
import type { SchemeCard } from "../types";

/** Case-insensitive match on the visible scheme text (works for Tamil and English). */
export function filterSchemes(schemes: SchemeCard[], query: string, category: string): SchemeCard[] {
  const needle = query.trim().toLocaleLowerCase();
  return schemes.filter((scheme) => {
    if (category && scheme.category !== category) return false;
    if (!needle) return true;
    return [scheme.title, scheme.department, scheme.category, scheme.overview].some((field) => field.toLocaleLowerCase().includes(needle));
  });
}

export function SchemeExplorer({ t, schemes }: { t: Copy; schemes: SchemeCard[] }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const categories = useMemo(() => [...new Set(schemes.map((scheme) => scheme.category))].sort(), [schemes]);
  // A category from the other language no longer exists after switching; treat it as "all".
  const activeCategory = categories.includes(category) ? category : "";
  const visible = filterSchemes(schemes, query, activeCategory);

  return (
    <section className="scheme-explorer">
      <div className="explorer-heading">
        <div><div className="section-kicker">{t.directoryKicker}</div><h2>{t.explore}</h2><p>{t.exploreIntro}</p></div>
        <span className="explorer-count">{visible.length.toString().padStart(2, "0")} <small>{t.programs}</small></span>
      </div>
      {schemes.length > 0 && (
        <div className="scheme-filters">
          <input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t.schemeSearch} aria-label={t.schemeSearch} />
          <select value={activeCategory} onChange={(event) => setCategory(event.target.value)} aria-label={t.categoryLabel}>
            <option value="">{t.allCategories}</option>
            {categories.map((name) => <option key={name} value={name}>{name}</option>)}
          </select>
        </div>
      )}
      <div className="scheme-cards">
        {visible.map((scheme) => (
          <article className="scheme-card" key={scheme.id}>
            <div className="scheme-card-top"><span className="scheme-icon">✳</span><span className="scheme-category">{scheme.category}</span></div>
            <h3>{scheme.title}</h3>
            <p className="scheme-department">{scheme.department}</p>
            <p className="scheme-overview">{scheme.overview}</p>
            <div className="scheme-card-footer">
              <span className="unverified-label"><i />{t.unverified}</span>
              <a href={scheme.url} target="_blank" rel="noreferrer">{t.openDirectory} <span>↗</span></a>
            </div>
          </article>
        ))}
      </div>
      {schemes.length > 0 && !visible.length && <p className="panel-intro">{t.noSchemeMatch}</p>}
    </section>
  );
}
