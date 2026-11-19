// Tous les appels au backend passent par ce fichier.
export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    // FastAPI renvoie soit un texte, soit une liste d'erreurs de validation
    const detail = typeof body.detail === "string" ? body.detail : null;
    throw new Error(detail ?? `Erreur ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

const sendJson = (method, path, data) =>
  request(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

// --- Matières ---
export const listSubjects = () => request("/subjects");
export const createSubject = (name, color) => sendJson("POST", "/subjects", { name, color });
export const updateSubject = (id, changes) => sendJson("PATCH", `/subjects/${id}`, changes);
export const deleteSubject = (id) => request(`/subjects/${id}`, { method: "DELETE" });

// --- Documents ---
export const listDocuments = () => request("/documents");

export function uploadDocuments(subjectId, files) {
  const form = new FormData();
  for (const f of files) form.append("files", f);
  return request(`/subjects/${subjectId}/documents`, { method: "POST", body: form });
}

export const deleteDocument = (id) => request(`/documents/${id}`, { method: "DELETE" });
export const pdfUrl = (id, page) => `${API_URL}/documents/${id}/pdf#page=${page}`;

// --- Questions, fiches, quiz (toujours dans une matière) ---
export const askQuestion = (subjectId, question) =>
  sendJson("POST", `/subjects/${subjectId}/ask`, { question });

export const createFiche = (subjectId, sujet) =>
  sendJson("POST", `/subjects/${subjectId}/fiches`, { sujet });

export const createQuiz = (subjectId, nbQuestions, sujet) =>
  sendJson("POST", `/subjects/${subjectId}/quiz`, { nb_questions: nbQuestions, sujet });
