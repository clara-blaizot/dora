import { useState } from "react";
import { askQuestion } from "../api.js";
import Sources from "./Sources.jsx";

export default function Chat({ documentIds }) {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!question.trim()) return;
    const q = question;
    setQuestion("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const { answer, sources } = await askQuestion(q, documentIds);
      setMessages((m) => [...m, { role: "dora", text: answer, sources }]);
    } catch (err) {
      setMessages((m) => [...m, { role: "dora", text: err.message, sources: [] }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat">
      <div className="messages">
        {messages.map((msg, i) =>
          msg.role === "user" ? (
            <p key={i} className="msg user">{msg.text}</p>
          ) : (
            <div key={i} className="msg dora">
              <p>{msg.text}</p>
              <Sources sources={msg.sources} />
            </div>
          )
        )}
        {loading && <p className="msg dora">Dora réfléchit…</p>}
      </div>
      <form onSubmit={handleSubmit}>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={documentIds.length ? "Pose une question sur tes cours…" : "Sélectionne d'abord un PDF"}
          disabled={!documentIds.length || loading}
        />
        <button disabled={!documentIds.length || loading}>Envoyer</button>
      </form>
    </div>
  );
}
