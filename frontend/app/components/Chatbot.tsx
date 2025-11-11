'use client';

import { chatbotContexts } from '../utils/chatbotContext';
import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { X, Minus, RefreshCw } from 'lucide-react';

// Detect program from referrer
function detectProgramFromReferrer(): string {
  if (typeof document === 'undefined') return 'default';
  try {
    const ref = document.referrer.toLowerCase();
    if (ref.includes('/btb')) return 'BTB';
    if (ref.includes('/bmt')) return 'BMT';
    if (ref.includes('/mmi')) return 'MMI';
    if (ref.includes('/bdaisy')) return 'BDAISY';
    if (ref.includes('/bcsim')) return 'BCSIM';
    if (ref.includes('/mar')) return 'MAR';
    if (ref.includes('/bmi')) return 'BMI';
    return 'default';
  } catch {
    return 'default';
  }
}

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

export default function Chatbot() {
  const [program, setProgram] = useState(detectProgramFromReferrer());
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Auto scroll when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // greeting handler
  useEffect(() => {
    const { greeting } = chatbotContexts[program] || chatbotContexts['default'];

    const greetingArray = Array.isArray(greeting) ? greeting : [greeting];
    const greetingMessages = greetingArray.map((g) => ({
      role: 'assistant' as const,
      content: g,
    }));

    if (messages.length === 0) {
      setMessages(greetingMessages);
    }
  }, [program]);

  // LISTEN TO PROGRAM MESSAGE FROM PARENT PAGE
  useEffect(() => {
    const listener = (event: MessageEvent) => {
      if (event.data?.program) {
        const normalized = event.data.program.toUpperCase();
        if (chatbotContexts[normalized]) {
          setProgram(normalized);
        }
      }
    };
    window.addEventListener('message', listener);
    return () => window.removeEventListener('message', listener);
  }, []);

  // === ASK QUESTION ===
  const askQuestion = async (q?: string) => {
    const query = q || question;
    if (!query.trim()) return;

    setShowSuggestions(false); // hide suggestions after first interaction

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

  const { suggestions } = chatbotContexts[program] || chatbotContexts['default'];

  return (
    <div
      className="w-full min-h-screen flex flex-col bg-base-200 text-sm text-shadow-sm relative"
      data-theme="HSD-Medien"
    >
      {/* === Fixed Header === */}
      <div className="fixed top-0 left-0 right-0 z-50 p-4 sm:p-4 border-b bg-neutral text-white flex items-center justify-between">
        <div className="flex flex-col">
          <span className="font-bold text-sm">MeDi, Dein KI-Assistent</span>
          <span className="text-xs opacity-80">Fachbereich Medien HSD</span>
        </div>

        <div className="flex items-center gap-2">
          {/* New Chat button */}
          <button
            onClick={() => {
              setMessages([]); // clear chat
              setShowSuggestions(true);
              const { greeting } = chatbotContexts[program] || chatbotContexts['default'];
              const greetingArray = Array.isArray(greeting) ? greeting : [greeting];
              const greetingMessages = greetingArray.map((g) => ({
                role: 'assistant' as const,
                content: g,
              }));
              setMessages(greetingMessages);
            }}
            className="p-2 rounded-full hover:bg-white/20 transition flex items-center justify-center"
            title="Neuen Chat starten"
          >
            <RefreshCw size={18} className="text-white" />
          </button>

          {/* Minimize button */}
          <button
            onClick={() => window.parent.postMessage({ type: 'minimize' }, '*')}
            className="p-2 rounded-full hover:bg-white/20 transition flex items-center justify-center"
            title="Chat minimieren"
          >
            <Minus size={18} className="text-white" />
          </button>

          {/* Close button */}
          <button
            onClick={() => window.parent.postMessage({ type: 'close' }, '*')}
            className="p-2 rounded-full hover:bg-white/20 transition flex items-center justify-center"
            title="Chat schließen"
          >
            <X size={18} className="text-white" />
          </button>
        </div>
      </div>


      {/* === Scrollable Messages === */}
      <div className="flex-1 overflow-y-auto p-3 mt-[70px] mb-[80px]">
        {messages.map((m, i) => (
          <div key={i}>
            <div className={`chat ${m.role === 'user' ? 'chat-end' : 'chat-start'}`}>
              <div
                className={`chat-bubble ${
                  m.role === 'assistant'
                    ? 'chat-bubble-primary'
                    : 'chat-bubble-secondary'
                }`}
              >
                {m.role === 'assistant' ? (
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      a: ({ node, ...props }) => (
                        <a
                          {...props}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-black hover:text-gray-500 hover:underline italic transition-colors duration-150 text-shadow-lg"
                        />
                      ),
                    }}
                  >
                    {m.content}
                  </ReactMarkdown>
                ) : (
                  m.content
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Suggested questions shown only once after greetings */}
        {showSuggestions && (
          <div>
            {suggestions.map((s, idx) => (
              <div className="chat chat-end" key={idx}>
                <button
                  onClick={() => askQuestion(s)}
                  className="chat-bubble chat-bubble-secondary cursor-pointer hover:opacity-80 transition"
                  title="Beispielfrage auswählen"
                >
                  {s}
                </button>
              </div>
            ))}
          </div>
        )}

        {loading && (
          <div className="chat chat-start">
            <div className="chat-bubble chat-bubble-primary">
              <span className="loading loading-dots loading-sm"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

        {/* === Fixed Bottom Section (Input + Collapsible Disclaimer) === */}
        <div className="fixed bottom-0 left-0 right-0 z-50 border-t border-base-300 bg-base-200">
          {/* Input Bar */}
          <div className="pt-3 px-3 flex flex-col sm:flex-row gap-2">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && askQuestion()}
              placeholder="Stelle eine Frage..."
              className="w-full input input-ghost text-sm bg-gray-50 text-gray-700 placeholder-gray-400"
            />
            <button
              onClick={() => askQuestion()}
              disabled={loading}
              className="btn btn-neutral w-full sm:w-auto text-sm"
              title="Frage senden"
            >
              Senden
            </button>
          </div>

          {/* Collapsible AI Disclaimer */}
          <div className="bg-base-200">
            <div className="collapse collapse-arrow bg-base-200 rounded-none">
              <input type="checkbox" className="peer" placeholder='disclaimer' />
              <div className="collapse-title text-x font-semibold text-gray-700 peer-checked:text-neutral">
                AI-Disclaimer
              </div>
              <div className="collapse-content text-xs leading-relaxed">
                <p>
                  Die Antworten werden durch eine künstliche Intelligenz generiert. Sie
                  entstehen auf der Grundlage von Informationen aus verschiedenen
                  Originalquellen des Fachbereichs Medien (wie Modulhandbuch,
                  Fachbereichsseite). Die KI bemüht sich, präzise Informationen
                  bereitzustellen. Ungenauigkeiten oder Unvollständigkeiten können jedoch
                  nicht ausgeschlossen werden.
                </p>

                <p className="mt-2">
                  Durch KI erstellte Antworten dienen einer ersten Orientierung und
                  sollten nicht die alleinige Grundlage für Entscheidungen der
                  Nutzer*innen sein. Für umfassende Informationen zum Fachbereich und
                  Studium konsultieren Sie bitte auch die offiziellen Seiten des{' '}
                  <a
                    href="https://medien.hs-duesseldorf.de/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-neutral hover:underline"
                  >
                    Fachbereichs Medien
                  </a>
                  , der{' '}
                  <a
                    href="https://fachschaftmedien.de/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-neutral hover:underline"
                  >
                    Fachschaft
                  </a>{' '}
                  oder des{' '}
                  <a
                    href="https://medien.hs-duesseldorf.de/studium/pruefungen/Seiten/default.aspx"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-neutral hover:underline"
                  >
                    Studienbüros
                  </a>
                  . Weitere Informationen zur{' '}
                  <a
                    href="https://medien.hs-duesseldorf.de/studium/beratung-im-studium"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-neutral hover:underline"
                  >
                    Beratung im Studium
                  </a>{' '}
                  finden Sie ebenfalls auf den offiziellen Seiten.
                </p>
              </div>
            </div>
          </div>
        </div>

    </div>
  );
}
