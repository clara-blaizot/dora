import { useEffect, useRef, useState } from "react";
import { FicheIcon, QuizIcon, SendIcon } from "./icons.jsx";

export default function ChatPanel({ subject, nbDocs, conversation, thinking, onSend, onCite }) {
  const [draft, setDraft] = useState("");
  const messagesRef = useRef(null);
  const inputRef = useRef(null);
  const { messages, panel } = conversation;

  // Toujours afficher le dernier message
  useEffect(() => {
    const box = messagesRef.current;
    if (box) box.scrollTop = box.scrollHeight;
  }, [messages.length, thinking]);

  useEffect(() => {
    if (!thinking) inputRef.current?.focus();
  }, [thinking]);

  function send() {
    const q = draft.trim();
    if (!q || thinking) return;
    setDraft("");
    onSend(q);
  }

  return (
    <section className="chat" aria-labelledby="chat-title">
      <div className="chat-head">
        <div className="avatar" aria-hidden="true">D</div>
        <div className="chat-title">
          <h2 id="chat-title">Demande à Dora</h2>
          <span>{nbDocs === 0 ? "Aucun cours ajouté" : `Répond à partir de ${nbDocs} cours`}</span>
        </div>
        {/* Pas encore reliés au backend : désactivés */}
        <div className="tools">
          <button type="button" className="tool-btn" disabled title="Bientôt disponible">
            <FicheIcon /> Fiche <span className="soon">bientôt</span>
          </button>
          <button type="button" className="tool-btn" disabled title="Bientôt disponible">
            <QuizIcon /> Quiz <span className="soon">bientôt</span>
          </button>
        </div>
      </div>

      <div className="messages" ref={messagesRef} aria-live="polite">
        {messages.length === 0 && (
          <div className="empty">
            Pose une question sur tes cours de {subject.name}. Dora te répond et t'indique les
            passages des PDF qu'elle a utilisés.
          </div>
        )}

        {messages.map((m) =>
          m.role === "user" ? (
            <div key={m.id} className="msg-user">{m.text}</div>
          ) : (
            <div key={m.id} className="msg-dora">
              <div className="msg-dora-avatar" aria-hidden="true">D</div>
              <div className={`msg-dora-bubble${m.error ? " error" : ""}`}>
                <span className="txt">{m.text}</span>
                {m.sources?.length > 0 && (
                  <div className="cites">
                    {m.sources.map((s) => {
                      const on = panel.open && panel.messageId === m.id && panel.activeN === s.numero;
                      return (
                        <button
                          key={s.numero}
                          type="button"
                          className={`cite${on ? " active" : ""}`}
                          onClick={() => onCite(m.id, s.numero)}
                        >
                          <strong>[{s.numero}]</strong> {s.filename} · p. {s.page}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )
        )}

        {thinking && <div className="thinking">Dora réfléchit…</div>}
      </div>

      <div className="composer">
        <label htmlFor="question" className="sr-only">Ta question</label>
        <input
          id="question"
          ref={inputRef}
          type="text"
          placeholder="Pose ta question à Dora…"
          autoComplete="off"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              send();
            }
          }}
        />
        <button
          type="button"
          className="send"
          aria-label="Envoyer la question"
          disabled={thinking || !draft.trim()}
          onClick={send}
        >
          <SendIcon />
        </button>
      </div>
    </section>
  );
}
