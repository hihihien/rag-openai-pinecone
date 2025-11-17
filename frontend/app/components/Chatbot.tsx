'use client';

import { chatbotContexts } from '../utils/chatbotContext';
import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { X, Minus, RefreshCw, Send, Menu } from 'lucide-react';

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
  const [hasInteracted, setHasInteracted] = useState(false);
  const hasInteractedRef = useRef(false);
  useEffect(() => {
    hasInteractedRef.current = hasInteracted;
  }, [hasInteracted]);

  const [program, setProgram] = useState(detectProgramFromReferrer());
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const [bottomPadding, setBottomPadding] = useState(120);
  
  useEffect(() => {
    const el = bottomRef.current;
    if (!el) return;
    const ro = new ResizeObserver(entries => {
      for (const entry of entries) {
        setBottomPadding(entry.contentRect.height);
      }
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Auto scroll only after the user has interacted (not on initial greetings)
  useEffect(() => {
    if (!hasInteracted) return;
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, hasInteracted]);

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

  // listen for messages from parent site
  // when parent sends program, update program and refresh greetings
  useEffect(() => {
    const listener = (event: MessageEvent) => {
      if (event.data?.program) {
        const normalized = String(event.data.program).toUpperCase();
        if (chatbotContexts[normalized]) {
          setProgram(normalized);

          if (!hasInteractedRef.current) {
            const { greeting } = chatbotContexts[normalized] || chatbotContexts['default'];
            const greetingArray = Array.isArray(greeting) ? greeting : [greeting];
            const greetingMessages = greetingArray.map((g) => ({
              role: 'assistant' as const,
              content: g,
            }));
            setMessages(greetingMessages);
            setShowSuggestions(true);
          }
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

    setHasInteracted(true);
    setShowSuggestions(false); 

    const newMessages: Message[] = [...messages, { role: 'user', content: query }];
    setMessages(newMessages);
    setQuestion('');
    setLoading(true);

    try {
      const payload: any = {
        question: query,
        history: messages.map((m) => ({ role: m.role, content: m.content })),
      };
      if (program && program !== 'default') {
        payload.program = program;
      }
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
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
      className="w-full min-h-screen flex flex-col bg-base-200 text-xs relative"
      data-theme="HSD-Medien"
    >
      {/* === Fixed Header === */}
      <div className="fixed top-0 left-0 right-0 z-50 p-4 sm:p-4 border-b bg-neutral text-white flex items-center justify-between">
        <div className="flex flex-col">
          <span className="font-bold text-x">MeDi, Dein KI-Assistent</span>
          <span className="text-xs opacity-80">Fachbereich Medien HSD</span>
        </div>

        {/* Right controls: icons (sm & lg+), burger (md..lg-) */}
        <div className="flex items-center gap-2">
          {/* Separate icons: visible on <md and ≥lg */}
          <div className="flex items-center gap-2 md:hidden lg:flex">
            {/* New Chat */}
            <button
              onClick={() => {
                setMessages([]);
                setShowSuggestions(true);
                const { greeting } = chatbotContexts[program] || chatbotContexts['default'];
                const greetingArray = Array.isArray(greeting) ? greeting : [greeting];
                const greetingMessages = greetingArray.map((g) => ({
                  role: 'assistant' as const,
                  content: g,
                }));
                setMessages(greetingMessages);
                setHasInteracted(false);
              }}
              className="p-2 rounded-full hover:bg-white/20 transition flex items-center justify-center"
              title="Neuen Chat starten"
              aria-label="Neuen Chat starten"
            >
              <RefreshCw size={18} className="text-white" />
            </button>

            {/* Minimize */}
            <button
              onClick={() => window.parent.postMessage({ type: 'minimize' }, '*')}
              className="p-2 rounded-full hover:bg-white/20 transition flex items-center justify-center"
              title="Chat minimieren"
              aria-label="Chat minimieren"
            >
              <Minus size={18} className="text-white" />
            </button>

            {/* Close */}
            <button
              onClick={() => window.parent.postMessage({ type: 'close' }, '*')}
              className="p-2 rounded-full hover:bg-white/20 transition flex items-center justify-center"
              title="Chat schließen"
              aria-label="Chat schließen"
            >
              <X size={18} className="text-white" />
            </button>
          </div>

          {/* Burger menu: visible only on md..lg- */}
          <div className="hidden md:block lg:hidden">
            <div className="dropdown dropdown-end">
              <button
                tabIndex={0}
                className="btn btn-ghost btn-circle"
                aria-label="Menü öffnen"
                title="Menü"
              >
                <Menu size={20} className="text-white" />
              </button>
              <ul
                tabIndex={0}
                className="menu dropdown-content bg-base-100 text-base-content rounded-box shadow mt-3 w-56"
              >
                <li>
                  <button
                    onClick={() => {
                      setMessages([]);
                      setShowSuggestions(true);
                      const { greeting } = chatbotContexts[program] || chatbotContexts['default'];
                      const greetingArray = Array.isArray(greeting) ? greeting : [greeting];
                      const greetingMessages = greetingArray.map((g) => ({
                        role: 'assistant' as const,
                        content: g,
                      }));
                      setMessages(greetingMessages);
                      setHasInteracted(false);
                    }}
                    aria-label="Neuen Chat starten"
                    title="Neuen Chat starten"
                  >
                    <RefreshCw size={16} />
                    Neuer Chat
                  </button>
                </li>
                <li>
                  <button
                    onClick={() => window.parent.postMessage({ type: 'minimize' }, '*')}
                    aria-label="Chat minimieren"
                    title="Chat minimieren"
                  >
                    <Minus size={16} />
                    Minimieren
                  </button>
                </li>
                <li>
                  <button
                    onClick={() => window.parent.postMessage({ type: 'close' }, '*')}
                    aria-label="Chat schließen"
                    title="Chat schließen"
                  >
                    <X size={16} />
                    Schließen
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>


      </div>


      {/* === Scrollable Messages === */}
      <div className="flex-1 overflow-y-auto p-3 mt-[70px]" style={{ paddingBottom: bottomPadding + 16 }}>
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
                    a: ({ node, ...props }) => {
                      const href = String(props.href || '');
                      // slugs use in chatbotContext
                      const programSlugs = new Set(['/bmi','/bmt','/btb','/bdaisy','/bcsim','/mmi','/mar']);
                      const isProgramLink = programSlugs.has(href);
                      // where these pages live on site
                      const BASE = '/webredaktion/chatbot-test';
                      const ORIGIN = 'https://medien.hs-duesseldorf.de';
                      const finalHref = isProgramLink ? `${ORIGIN}${BASE}${href}` : href;
                      const target = '_blank';
                      return (
                        <a
                          {...props}
                          href={finalHref}
                          target={target}
                          rel="noopener noreferrer"
                          className="hover:text-shadow-sm italic transition-colors duration-150"
                        />
                    );
                   },
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

      {/* Fixed bottom (Input + Disclaimer) */}
      <div ref={bottomRef} className="fixed bottom-0 left-0 right-0 z-50 border-t border-base-300 bg-base-200">
        <form
          onSubmit={(e) => { e.preventDefault(); askQuestion(); }}
          className="p-3 pb-0 border-base-300"
        >
          <div className="relative w-full">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Stelle eine Frage..."
              className="w-full input input-ghost text-xs bg-gray-50 text-gray-700 placeholder-gray-400 pr-12"
            />
            <button
              type="submit"
              disabled={loading}
              aria-label="Senden"
              title="Senden"
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full hover:bg-base-200 disabled:opacity-50 z-10"
            >
              <Send size={18} className="text-gray-700" />
            </button>
          </div>
        </form>


        {/* Collapsible AI Disclaimer*/}
        <div className="bg-base-200">
          <div className="collapse collapse-arrow bg-base-200 rounded-none">
            <input type="checkbox" className="peer border-none" placeholder="disclaimer" />
            <div className="collapse-title text-xs font-semibold text-gray-700 peer-checked:text-neutral">
              AI-Disclaimer
            </div>
            <div className="collapse-content text-xs leading-relaxed">
              <p>
                Die Antworten werden durch eine künstliche Intelligenz generiert. Sie entstehen
                auf der Grundlage von Informationen aus verschiedenen Originalquellen des
                Fachbereichs Medien (wie Modulhandbuch, Fachbereichsseite). Die KI bemüht sich,
                präzise Informationen bereitzustellen. Ungenauigkeiten oder Unvollständigkeiten
                können jedoch nicht ausgeschlossen werden.
              </p>

              <p className="mt-2">
                Durch KI erstellte Antworten dienen einer ersten Orientierung und sollten nicht
                die alleinige Grundlage für Entscheidungen der Nutzer*innen sein. Für
                umfassende Informationen zum Fachbereich und Studium konsultieren Sie bitte
                auch die offiziellen Seiten des{' '}
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