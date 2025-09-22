'use client';

import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Maximize2, Minimize2, Minus, NotebookPen } from 'lucide-react';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

export default function HomePage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const askQuestion = async (q?: string) => {
    const query = q || question;
    if (!query.trim()) return;

    const newMessages: Message[] = [...messages, { role: 'user', content: query }];
    setMessages(newMessages);
    setQuestion('');
    setLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: query,
          history: messages.map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      const data = await res.json();
      const answer = data.answer || 'Keine Antwort erhalten.';

      setMessages([...newMessages, { role: 'assistant', content: answer }]);
    } catch (err) {
      console.error(err);
      setMessages([
        ...newMessages,
        { role: 'assistant', content: 'Fehler beim Senden der Anfrage.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Suggested quick questions
  const suggestions = [
    'Was sind die Voraussetzungen für das Modul Datenbank System 1?',
    'Welches Modul im Studiengang BMI ist relevant für Webentwicklung?',
    'An wen kann ich mich bei Fragen über Bachelorarbeiten in BDAISY wenden?',
  ];

  return (
    <main className="relative min-h-screen bg-gray-50" data-theme="caramellatte">
      {/* Floating Avatar / FAB Button */}
      <div
        className="fixed bottom-6 right-6 avatar cursor-pointer"
        onClick={() => {
          setIsOpen(!isOpen);
          if (!isOpen && messages.length === 0) {
            setMessages([
              {
                role: 'assistant',
                content:
                        'Hallo! 👋 Ich bin MeMo, dein KI-Assistent der **Medienfachschaft der Hochschule Düsseldorf**, unterstützt von OpenAI API.\n\nFrag mich alles rund um deinen Studieninhalt!\n\n\n\nFür bessere Ergebnisse gib bitte in deiner Frage an:\n\n- **Dein Studienprogramm**\n- **Namen des Moduls**, zu dem du Informationen möchtest\n- **Thematisch Inhalte** aus einem Studienprogramm',
                      },
                  ]);
          }
        }}
      >
        <div className="w-12 rounded-full ring-3 ring-neutral ring-offset-base-100 ring-offset-2">
          <img
            src="https://img.daisyui.com/images/profile/demo/yellingcat@192.webp"
            alt="Chatbot Avatar"
          />
        </div>
      </div>

      {/* Chat window */}
      {isOpen && (
        <div
          className={`fixed bg-white border rounded-lg shadow-lg flex flex-col transition-all duration-300
            ${
              expanded
                ? 'inset-10 w-auto h-auto max-w-[90vw] max-h-[85vh] m-auto'
                : 'bottom-24 right-6 w-96 max-w-[90vw] sm:w-96 max-h-[70vh]'
            }`}
        >
          {/* Header */}
          <div className="p-3 border-b bg-neutral text-white rounded-t-lg flex justify-between items-center">
            {/* Left side: Avatar + Title */}
            <div className="flex items-center gap-3">
              <div className="avatar">
                <div className="w-10 rounded-full">
                  <img
                    src="https://img.daisyui.com/images/profile/demo/yellingcat@192.webp"
                    alt="MeMo Avatar"
                  />
                </div>
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-xs">MeMo, Dein KI-Assistent</span>
                <span className="text-xs font-light opacity-80">
                  Für Studieninhalte der HSD Medienfachschaft
                </span>
              </div>
            </div>

            {/* Right side: Icons */}
            <div className="flex items-center gap-2">
              <div className="tooltip text-xs" data-tip="neues Chat starten">
                <button
                  onClick={() => {
                    setMessages([
                      {
                        role: 'user',
                        content: 'Ich möchte ein neues Chat starten.',
                      },
                    ]);
                  }}
                  className="btn btn-ghost btn-xs text-white"
                  title="neues Chat starten"
                >
                  <NotebookPen className="w-4 h-4" />
                </button>
              </div>

              <div
                className="tooltip text-xs"
                data-tip={expanded ? 'Minimieren' : 'Maximieren'}
              >
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="btn btn-ghost btn-xs text-white"
                  title={expanded ? 'Minimieren' : 'Maximieren'}
                >
                  {expanded ? (
                    <Minimize2 className="w-4 h-4" />
                  ) : (
                    <Maximize2 className="w-4 h-4" />
                  )}
                </button>
              </div>

              <div className="tooltip text-xs" data-tip="Fenster schließen">
                <button
                  onClick={() => {
                    if (expanded) {
                      setExpanded(false);
                    } else {
                      setIsOpen(false);
                    }
                  }}
                  className="btn btn-ghost btn-xs text-white"
                  title="Fenster schließen"
                >
                  <Minus className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4 text-sm">
            {messages.map((m, i) => (
              <div key={i}>
                <div
                  className={`chat ${m.role === 'user' ? 'chat-end' : 'chat-start'}`}
                >
                  <div className="chat-image avatar">
                    <div className="w-8 rounded-full">
                      <img
                        alt={m.role === 'user' ? 'User' : 'Assistant'}
                        src={
                          m.role === 'user'
                            ? 'https://img.daisyui.com/images/profile/demo/kenobee@192.webp'
                            : 'https://img.daisyui.com/images/profile/demo/yellingcat@192.webp'
                        }
                      />
                    </div>
                  </div>
                  <div
                    className={`chat-bubble max-w-[80%] ${
                      m.role === 'assistant'
                        ? 'chat-bubble-neutral'
                        : 'chat-bubble-secondary'
                    }`}
                  >
                    {m.role === 'assistant' ? (
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          ul: ({ node, ...props }) => (
                            <ul className="list-disc list-inside space-y-1" {...props} />
                          ),
                          ol: ({ node, ...props }) => (
                            <ol className="list-decimal list-inside space-y-1" {...props} />
                          ),
                          li: ({ node, ...props }) => <li className="ml-2" {...props} />,
                          strong: ({ node, ...props }) => (
                            <strong className="font-bold" {...props} />
                          ),
                          p: ({ node, ...props }) => <p className="mb-2" {...props} />,
                        }}
                      > 
                        {m.content}
                      </ReactMarkdown>
                    ) : (
                      m.content
                    )}
                  </div>
                </div>

                {/* Suggestions only after the greeting message */}
                {i === 0 && m.role === 'assistant' && (
                  <div className="chat chat-end mt-2">
                    <div className="flex flex-wrap gap-2 max-w-full">
                      {suggestions.map((s, idx) => (
                        <button
                          key={idx}
                          onClick={() => askQuestion(s)}
                          className="chat-bubble chat-bubble-secondary text-xs cursor-pointer hover:opacity-80 transition"
                          title="Beispielfrage auswählen"
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="chat chat-start">
                <div className="chat-bubble chat-bubble-neutral">
                  <span className="loading loading-dots loading-sm"></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-3 border-t flex space-x-2">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && askQuestion()}
              placeholder="Stelle eine Frage..."
              className="flex-1 input input-bordered bg-gray-50 text-gray-700 placeholder-gray-400"
            />
            <button
              onClick={() => askQuestion()}
              disabled={loading}
              className="btn btn-neutral"
              title="Frage senden"
            >
              Senden
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
