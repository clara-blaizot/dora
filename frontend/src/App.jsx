import { useEffect, useState } from "react";
import { listDocuments } from "./api.js";
import DocumentsPanel from "./components/DocumentsPanel.jsx";
import Chat from "./components/Chat.jsx";
import Fiches from "./components/Fiches.jsx";
import Quiz from "./components/Quiz.jsx";

const TABS = {
  chat: { label: "Questions", component: Chat },
  fiches: { label: "Fiches", component: Fiches },
  quiz: { label: "Quiz", component: Quiz },
};

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [tab, setTab] = useState("chat");

  const refresh = () => listDocuments().then(setDocuments).catch(console.error);
  useEffect(() => { refresh(); }, []);

  const Active = TABS[tab].component;

  return (
    <div className="app">
      <aside>
        <h1>Dora</h1>
        <DocumentsPanel
          documents={documents}
          selectedIds={selectedIds}
          onSelect={setSelectedIds}
          onChange={refresh}
        />
      </aside>
      <main>
        <nav>
          {Object.entries(TABS).map(([key, t]) => (
            <button key={key} className={tab === key ? "active" : ""} onClick={() => setTab(key)}>
              {t.label}
            </button>
          ))}
        </nav>
        <Active documentIds={selectedIds} />
      </main>
    </div>
  );
}
