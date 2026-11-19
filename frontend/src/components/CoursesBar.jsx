import { CloseIcon, PlusIcon } from "./icons.jsx";

export default function CoursesBar({ docs, uploading, onUpload, onRemove }) {
  function handleChange(e) {
    const files = [...e.target.files].filter((f) => /\.pdf$/i.test(f.name));
    e.target.value = "";
    if (files.length) onUpload(files);
  }

  return (
    <section className="courses" aria-labelledby="pdf-title">
      <h2 id="pdf-title">Mes cours</h2>
      {docs.map((d) => (
        <span key={d.id} className="chip">
          <span className="chip-tag">PDF</span>
          <span className="chip-name" title={`${d.nb_pages} pages`}>{d.filename}</span>
          <button type="button" aria-label={`Supprimer ${d.filename}`} onClick={() => onRemove(d)}>
            <CloseIcon size={14} />
          </button>
        </span>
      ))}
      {docs.length === 0 && <span className="muted">Aucun PDF pour l'instant.</span>}
      <label className={`add-pdf${uploading ? " busy" : ""}`}>
        <PlusIcon size={14} /> {uploading ? "Import…" : "Ajouter"}
        <input
          className="sr-only"
          type="file"
          accept="application/pdf,.pdf"
          multiple
          disabled={uploading}
          onChange={handleChange}
        />
      </label>
    </section>
  );
}
