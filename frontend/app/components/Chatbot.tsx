'use client';

import { chatbotContexts } from '../utils/chatbotContext';

import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Maximize2, Minimize2, Minus, NotebookPen } from 'lucide-react';



type Message = {
  role: 'user' | 'assistant';
  content: string;
};

type ChatbotProps = {
  program?: string; // e.g., "MMI", "BMI", "default"
};

export default function Chatbot({ program = 'default' }: ChatbotProps) {
  const { greeting, suggestions } = chatbotContexts[program] || chatbotContexts['default'];
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
          history: messages.map((m) => ({ role: m.role, content: m.content })),
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

  return (
    <main className="relative" data-theme="HSD">
      {/* FAB Avatar */}
      <div
        className="fixed bottom-6 right-6 avatar cursor-pointer"
        onClick={() => {
          setIsOpen(!isOpen);
          if (!isOpen && messages.length === 0) {
            setMessages([
              {
                role: 'assistant',
                content: greeting,
              },
            ]);
          }
        }}
      >
        <div className="w-12 rounded-full ring-2 ring-neutral ring-offset-base-100 ring-offset-2">
          <img src="/chatbot.png" alt="Chatbot Avatar" />
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
            <div className="flex items-center gap-3">
              <div className="avatar">
                <div className="w-10 rounded-full">
                  <img src="/chatbot.png" alt="MeDi Avatar" />
                </div>
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-xs">MeDi, Dein KI-Assistent</span>
                <span className="text-xs font-light opacity-80">
                  Fachbereich Medien – HSD
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() =>
                  setMessages([{ role: 'user', content: 'Ich möchte ein neues Chat starten.' }])
                }
                className="btn btn-ghost btn-xs text-white"
                title="Neues Chat starten"
              >
                <NotebookPen className="w-4 h-4" />
              </button>
              <button
                onClick={() => setExpanded(!expanded)}
                className="btn btn-ghost btn-xs text-white"
                title={expanded ? 'Minimieren' : 'Maximieren'}
              >
                {expanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>
              <button
                onClick={() => {
                  if (expanded) setExpanded(false);
                  else setIsOpen(false);
                }}
                className="btn btn-ghost btn-xs text-white"
                title="Schließen"
              >
                <Minus className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4 text-sm">
            {messages.map((m, i) => (
              <div key={i}>
                <div className={`chat ${m.role === 'user' ? 'chat-end' : 'chat-start'}`}>
                  <div className="chat-image avatar">
                    <div className="w-8 rounded-full">
                      <img
                        alt={m.role === 'user' ? 'User' : 'Assistant'}
                        src={m.role === 'user' ? '/user.jpg' : '/chatbot.png'}
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
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {m.content}
                      </ReactMarkdown>
                    ) : (
                      m.content
                    )}
                  </div>
                </div>

                {/* Suggested questions */}
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


