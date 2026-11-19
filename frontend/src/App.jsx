import { useEffect, useState } from "react";
import { askQuestion, deleteDocument, listDocuments, uploadDocuments } from "./api.js";
import { useSubjects } from "./hooks/useSubjects.js";
import Sidebar from "./components/Sidebar.jsx";
import ChatPanel from "./components/ChatPanel.jsx";
import SourcesPanel from "./components/SourcesPanel.jsx";
import CoursesBar from "./components/CoursesBar.jsx";

const EMPTY_CONVERSATION = { messages: [], panel: { open: false } };

export default function App() {
  const { subjects, status, addSubject } = useSubjects();
  const [activeId, setActiveId] = useState(null);
  const [documents, setDocuments] = useState([]); // tous les PDF, chacun avec son subject_id
  // Conversation de chaque matière (gardée en mémoire, perdue au rechargement)
  const [conversations, setConversations] = useState({});
  const [thinkingId, setThinkingId] = useState(null); // matière qui attend une réponse
  const [uploading, setUploading] = useState(false);
  const [notice, setNotice] = useState(null);

  useEffect(() => {
    listDocuments().then(setDocuments).catch(() => {});
  }, []);

  if (status === "loading") return <p className="splash">Chargement…</p>;
  if (status === "error") {
    return <p className="splash">Impossible de joindre le backend. Est-il lancé sur le port 8000 ?</p>;
  }

  const subject = subjects.find((s) => s.id === activeId) ?? subjects[0];
  const docs = documents.filter((d) => d.subject_id === subject.id);
  const conversation = conversations[subject.id] ?? EMPTY_CONVERSATION;

  const panelMessage = conversation.panel.open
    ? conversation.messages.find((m) => m.id === conversation.panel.messageId)
    : null;
  const panelSources = panelMessage?.sources ?? [];

  function updateConversation(subjectId, update) {
    setConversations((all) => ({ ...all, [subjectId]: update(all[subjectId] ?? EMPTY_CONVERSATION) }));
  }

  function pushMessage(subjectId, message, openPanel = false) {
    updateConversation(subjectId, (c) => ({
      messages: [...c.messages, message],
      panel: openPanel ? { open: true, messageId: message.id, activeN: 1 } : c.panel,
    }));
  }

  async function handleSend(question) {
    const subjectId = subject.id; // la réponse va à cette matière, même si on en change entre-temps
    pushMessage(subjectId, { id: crypto.randomUUID(), role: "user", text: question });

    if (docs.length === 0) {
      pushMessage(subjectId, {
        id: crypto.randomUUID(),
        role: "dora",
        text: "Je n'ai encore aucun cours pour cette matière. Ajoute un PDF dans « Mes cours », puis repose ta question.",
      });
      return;
    }

    setThinkingId(subjectId);
    try {
      const { answer, sources } = await askQuestion(subjectId, question);
      pushMessage(subjectId, { id: crypto.randomUUID(), role: "dora", text: answer, sources }, sources.length > 0);
    } catch (err) {
      pushMessage(subjectId, { id: crypto.randomUUID(), role: "dora", text: err.message, error: true });
    } finally {
      setThinkingId(null);
    }
  }

  function handleCite(messageId, numero) {
    updateConversation(subject.id, (c) => ({ ...c, panel: { open: true, messageId, activeN: numero } }));
  }

  function handleCloseSources() {
    updateConversation(subject.id, (c) => ({ ...c, panel: { ...c.panel, open: false } }));
  }

  async function handleUpload(files) {
    setUploading(true);
    setNotice(null);
    try {
      const added = await uploadDocuments(subject.id, files);
      setDocuments((list) => [...list, ...added]);
    } catch (err) {
      setNotice(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleRemove(doc) {
    if (!window.confirm(`Supprimer « ${doc.filename} » ? Dora ne pourra plus s'en servir.`)) return;
    try {
      await deleteDocument(doc.id);
      setDocuments((list) => list.filter((d) => d.id !== doc.id));
    } catch (err) {
      setNotice(err.message);
    }
  }

  async function handleAddSubject(name) {
    try {
      const created = await addSubject(name);
      setActiveId(created.id);
      setNotice(null);
    } catch (err) {
      setNotice(err.message);
    }
  }

  function handleSelect(id) {
    setActiveId(id);
    setNotice(null);
  }

  return (
    <div className="app">
      <Sidebar subjects={subjects} activeId={subject.id} onSelect={handleSelect} onAdd={handleAddSubject} />

      <main className="main">
        <header>
          <h1>{subject.name}</h1>
        </header>

        {notice && <p className="notice" role="status">{notice}</p>}

        <div className="row">
          <ChatPanel
            key={subject.id}
            subject={subject}
            nbDocs={docs.length}
            conversation={conversation}
            thinking={thinkingId === subject.id}
            onSend={handleSend}
            onCite={handleCite}
          />
          {panelSources.length > 0 && (
            <SourcesPanel
              sources={panelSources}
              activeN={conversation.panel.activeN}
              onClose={handleCloseSources}
            />
          )}
        </div>

        <CoursesBar docs={docs} uploading={uploading} onUpload={handleUpload} onRemove={handleRemove} />
      </main>
    </div>
  );
}
