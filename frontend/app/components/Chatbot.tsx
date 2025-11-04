'use client';

import { chatbotContexts } from '../utils/chatbotContext';
import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { X } from 'lucide-react';

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
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const { greeting } = chatbotContexts[program] || chatbotContexts['default'];
    setMessages([{ role: 'assistant', content: greeting }]);
  }, [program]);

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

  const { greeting, suggestions } = chatbotContexts[program] || chatbotContexts['default'];

  return (
    <div className="w-full min-h-screen flex flex-col bg-white m-0 p-0 text-sm text-shadow-sm" data-theme="HSD-Medien">
      {/* Header with Close Icon */}
      <div className="p-4 sm:p-4 border-b bg-neutral text-white flex items-center justify-between">
        <div className="flex flex-col">
          <span className="font-bold text-sm">MeDi, Dein KI-Assistent</span>
          <span className="text-xs opacity-80">Fachbereich Medien HSD</span>
        </div>
        <button
          onClick={() => window.parent.postMessage({ type: 'close' }, '*')}
          className="p-2 rounded-full hover:bg-white/20 transition flex items-center justify-center"
          title="Chat schließen"
        >
          <X size={20} className="text-white" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 min-h-[300px] p-4 overflow-y-auto space-y-4 text-sm">
        {messages.map((m, i) => (
          <div key={i}>
            <div className={`chat ${m.role === 'user' ? 'chat-end' : 'chat-start'}`}>
              <div
                className={`chat-bubble ${
                  m.role === 'assistant'
                    ? 'chat-bubble-neutral'
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
                          className="text-white hover:text-cyan-200 hover:underline italic transition-colors duration-150 text-shadow-lg"
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

            {/* Suggested questions after greeting */}
            {/* Suggested questions after greeting */}
            {i === 0 && m.role === 'assistant' && (
              <div className="space-y-2 mt-2">
                {suggestions.map((s, idx) => (
                  <div className="chat chat-end" key={idx}>
                    <button
                      onClick={() => askQuestion(s)}
                      className="chat-bubble chat-bubble-secondary text-xs cursor-pointer hover:opacity-80 transition"
                      title="Beispielfrage auswählen"
                    >
                      {s}
                    </button>
                  </div>
                ))}
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
      <div className="p-3 border-t flex flex-col sm:flex-row gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && askQuestion()}
          placeholder="Stelle eine Frage..."
          className="w-full input input-bordered text-sm bg-gray-50 text-gray-700 placeholder-gray-400"
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
    </div>
  );
}
