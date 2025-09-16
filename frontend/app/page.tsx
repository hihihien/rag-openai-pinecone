'use client';

import { useState } from 'react';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

export default function HomePage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    if (!question.trim()) return;

    // add user message
    const newMessages: Message[] = [...messages, { role: 'user', content: question }];
    setMessages(newMessages);
    setQuestion('');
    setLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          question,
          history: messages.map(m => ({ 
            role: m.role, 
            content: m.content 
          })),
        }),
      });

      const data = await res.json();

      const answer = data.answer || 'Keine Antwort erhalten.';

      // add assistant message
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
    <main className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-50">
      <div className="w-full max-w-2xl flex flex-col space-y-4">
        <h1 className="text-3xl font-bold text-center text-black">HSD Medienstudiengänge Chatbot</h1>

        {/* Chat messages */}
        <div className="flex-1 p-4 bg-white border rounded-lg overflow-y-auto max-h-[70vh] space-y-4">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`p-3 rounded-lg max-w-[80%] ${
                m.role === 'user'
                  ? 'bg-blue-500 text-white self-end text-right'
                  : 'bg-gray-100 text-black self-start text-left'
              }`}
            >
              {m.content}
            </div>
          ))}
          {loading && (
            <div className="p-3 rounded-lg bg-gray-200 self-start text-left">
              Antwort wird generiert...
            </div>
          )}
        </div>

        {/* Input box */}
        <div className="flex space-x-2">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Stelle eine Frage zum Modulhandbuch..."
            rows={2}
            className="flex-1 p-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          />
          <button
            onClick={askQuestion}
            disabled={loading}
            className="px-4 py-2 text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            Senden
          </button>
        </div>
      </div>
    </main>
  );
}
