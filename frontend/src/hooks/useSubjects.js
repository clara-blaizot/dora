import { useEffect, useState } from "react";

// Les matières n'existent pas (encore) dans le backend : elles sont gérées ici
// et sauvegardées dans le navigateur. Chaque matière garde les ids de ses PDF.
const STORAGE_KEY = "dora.subjects";
const COLORS = ["#D6336C", "#F783AC", "#A61E4D", "#E599B8", "#F06595", "#C2255C"];

const newSubject = (name, index) => ({
  id: crypto.randomUUID(),
  name,
  color: COLORS[index % COLORS.length],
  docIds: [],
});

function load() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    return Array.isArray(saved) && saved.length ? saved : null;
  } catch {
    return null;
  }
}

export function useSubjects() {
  const [subjects, setSubjects] = useState(() => load() ?? [newSubject("Ma matière", 0)]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(subjects));
    } catch {
      // stockage indisponible (navigation privée…) : les matières restent en mémoire
    }
  }, [subjects]);

  function addSubject(name) {
    const subject = newSubject(name, subjects.length);
    setSubjects((list) => [...list, subject]);
    return subject.id;
  }

  function addDocs(subjectId, docIds) {
    setSubjects((list) =>
      list.map((s) => (s.id === subjectId ? { ...s, docIds: [...s.docIds, ...docIds] } : s))
    );
  }

  function removeDoc(docId) {
    setSubjects((list) => list.map((s) => ({ ...s, docIds: s.docIds.filter((id) => id !== docId) })));
  }

  // PDF présents dans le backend mais rangés dans aucune matière (importés
  // avant l'existence des matières, ou depuis un autre navigateur) : on les
  // range dans la première matière pour qu'ils restent accessibles.
  function adoptOrphans(allDocIds) {
    setSubjects((list) => {
      const known = new Set(list.flatMap((s) => s.docIds));
      const orphans = allDocIds.filter((id) => !known.has(id));
      if (!orphans.length) return list;
      return list.map((s, i) => (i === 0 ? { ...s, docIds: [...s.docIds, ...orphans] } : s));
    });
  }

  return { subjects, addSubject, addDocs, removeDoc, adoptOrphans };
}
