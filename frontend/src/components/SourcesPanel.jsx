import { useEffect, useRef } from "react";
import { pdfUrl } from "../api.js";
import { CloseIcon } from "./icons.jsx";

// Passages renvoyés par la recherche Qdrant pour une réponse de Dora.
// `activeN` est le numéro [n] sur lequel l'étudiant a cliqué.
export default function SourcesPanel({ sources, activeN, onClose }) {
  const activeRef = useRef(null);

  useEffect(() => {
    activeRef.current?.scrollIntoView({ block: "nearest" });
  }, [activeN, sources]);

  return (
    <aside className="sources" aria-labelledby="sources-title">
      <div className="sources-head">
        <div>
          <h2 id="sources-title">Sources</h2>
          <span className="count">
            {sources.length} passage{sources.length > 1 ? "s" : ""}
          </span>
        </div>
        <button type="button" className="icon-btn" aria-label="Fermer le volet Sources" onClick={onClose}>
          <CloseIcon />
        </button>
      </div>
      <ol>
        {sources.map((s) => {
          const active = s.numero === activeN;
          return (
            <li key={s.numero} className={`source${active ? " active" : ""}`} ref={active ? activeRef : null}>
              <div className="source-meta">
                <span className="source-n">{s.numero}</span>
                <span className="source-file">{s.filename}</span>
                <a
                  className="source-page"
                  href={pdfUrl(s.document_id, s.page)}
                  target="_blank"
                  rel="noreferrer"
                  title="Ouvrir le PDF à cette page"
                >
                  p. {s.page} ↗
                </a>
              </div>
              <blockquote>{s.text}</blockquote>
            </li>
          );
        })}
      </ol>
    </aside>
  );
}
