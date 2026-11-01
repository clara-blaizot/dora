import { useState } from "react";
import { deleteDocument, uploadDocuments } from "../api.js";

export default function DocumentsPanel({ documents, selectedIds, onSelect, onChange }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  async function handleUpload(e) {
    const files = [...e.target.files];
    if (!files.length) return;
    setUploading(true);
    setError(null);
    try {
      const added = await uploadDocuments(files);
      onSelect([...selectedIds, ...added.map((d) => d.id)]);
      onChange();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleDelete(id) {
    await deleteDocument(id);
    onSelect(selectedIds.filter((x) => x !== id));
    onChange();
  }

  const toggle = (id) =>
    onSelect(selectedIds.includes(id) ? selectedIds.filter((x) => x !== id) : [...selectedIds, id]);

  return (
    <section className="documents">
      <h2>Mes cours</h2>
      <label className="upload">
        {uploading ? "Envoi…" : "+ Ajouter des PDF"}
        <input type="file" accept="application/pdf" multiple hidden onChange={handleUpload} />
      </label>
      {error && <p className="error">{error}</p>}
      <ul>
        {documents.map((d) => (
          <li key={d.id}>
            <label>
              <input type="checkbox" checked={selectedIds.includes(d.id)} onChange={() => toggle(d.id)} />
              {d.filename}
            </label>
            <button className="icon" title="Supprimer" onClick={() => handleDelete(d.id)}>×</button>
          </li>
        ))}
      </ul>
    </section>
  );
}
