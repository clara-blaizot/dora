// Tous les appels au backend passent par ce fichier.
export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Erreur ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

const postJson = (path, data) =>
  request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

export function uploadDocuments(files) {
  const form = new FormData();
  for (const f of files) form.append("files", f);
  return request("/documents", { method: "POST", body: form });
}

export const listDocuments = () => request("/documents");
export const deleteDocument = (id) => request(`/documents/${id}`, { method: "DELETE" });
export const pdfUrl = (id, page) => `${API_URL}/documents/${id}/pdf#page=${page}`;

export const askQuestion = (question, documentIds) =>
  postJson("/chat", { question, document_ids: documentIds });

export const createFiche = (documentIds, sujet) =>
  postJson("/fiches", { document_ids: documentIds, sujet });

export const createQuiz = (documentIds, nbQuestions, sujet) =>
  postJson("/quiz", { document_ids: documentIds, nb_questions: nbQuestions, sujet });
