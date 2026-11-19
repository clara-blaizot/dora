import { useRef, useState } from "react";
import { PlusIcon } from "./icons.jsx";

export default function Sidebar({ subjects, activeId, onSelect, onAdd }) {
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("");
  // Entrée puis perte de focus déclenchent tous deux `finish` : on ne crée qu'une fois
  const finished = useRef(false);

  function startCreating() {
    finished.current = false;
    setCreating(true);
  }

  function finish(save) {
    if (finished.current) return;
    finished.current = true;
    if (save && name.trim()) onAdd(name.trim());
    setName("");
    setCreating(false);
  }

  function handleSubmit(e) {
    e.preventDefault();
    finish(true);
  }

  return (
    <aside className="sidebar" aria-label="Matières">
      <div className="brand">
        <div className="brand-mark" aria-hidden="true">D</div>
        <div>
          <span className="brand-name">Dora</span>
          <span className="brand-sub">Ton assistante de révision</span>
        </div>
      </div>

      <nav className="nav" aria-label="Liste des matières">
        <span className="nav-label">Mes matières</span>
        {subjects.map((s) => (
          <button
            key={s.id}
            type="button"
            className="subject"
            aria-current={s.id === activeId ? "page" : undefined}
            onClick={() => onSelect(s.id)}
          >
            <span className="subject-dot" aria-hidden="true" style={{ background: s.color }} />
            <span className="subject-name">{s.name}</span>
          </button>
        ))}

        {creating ? (
          <form className="subject-form" onSubmit={handleSubmit}>
            <label htmlFor="new-subject" className="sr-only">Nom de la matière</label>
            <input
              id="new-subject"
              autoFocus
              value={name}
              placeholder="Nom de la matière"
              onChange={(e) => setName(e.target.value)}
              onBlur={() => finish(true)}
              onKeyDown={(e) => e.key === "Escape" && finish(false)}
            />
          </form>
        ) : (
          <button type="button" className="add-subject" onClick={startCreating}>
            <PlusIcon /> Nouvelle matière
          </button>
        )}
      </nav>
    </aside>
  );
}
