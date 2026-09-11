import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';

export default function ChatWindow({ messages = [], loading = false, activeProvider = 'Sarvam-105B' }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-1 min-h-[380px] max-h-[560px] bg-slate-50/60 rounded-2xl border border-slate-200/80 shadow-2xs">
      {messages.length === 0 && !loading && (
        <div className="flex flex-col items-center justify-center h-full py-16 text-center text-slate-500 text-xs">
          <p className="font-bold text-slate-800 text-sm mb-1">Swasth-IQ Medical AI Assistant</p>
          <p className="max-w-md text-slate-500 leading-relaxed">
            Ask any question about your lab results, CBC parameters, reference ranges, or recommendations.
          </p>
        </div>
      )}

      {messages.map((m, i) => (
        <MessageBubble key={m.id || i} message={m} />
      ))}

      {loading && <TypingIndicator provider={activeProvider} />}
      <div ref={bottomRef} />
    </div>
  );
}
