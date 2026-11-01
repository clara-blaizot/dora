import { pdfUrl } from "../api.js";

// Affiche les passages des cours retrouvés dans Qdrant pour cette question.
// Le numéro [n] correspond aux références dans la réponse de Dora.
export default function Sources({ sources }) {
  if (!sources.length) return null;

  return (
    <details className="sources">
      <summary>Sources ({sources.length})</summary>
      <ul>
        {sources.map((s) => (
          <li key={s.numero}>
            <a href={pdfUrl(s.document_id, s.page)} target="_blank" rel="noreferrer">
              [{s.numero}] {s.filename}, p. {s.page}
            </a>
            <span className="score"> — pertinence {Math.round(s.score * 100)} %</span>
            <blockquote>{s.text}</blockquote>
          </li>
        ))}
      </ul>
    </details>
  );
}
