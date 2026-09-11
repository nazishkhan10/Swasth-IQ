import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';

export default function ChatInput({ onSend, loading = false }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || loading) return;
    onSend(text.trim());
    setText('');
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2 bg-slate-900 border border-slate-800 p-2 rounded-xl shadow-lg">
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask Swasth-IQ about your report, lab values, or recommendations..."
        disabled={loading}
        className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-sm px-3 py-2 outline-hidden border-none disabled:opacity-50"
      />

      <button
        type="submit"
        disabled={!text.trim() || loading}
        className="btn-primary p-2.5 rounded-lg flex items-center justify-center shrink-0 disabled:opacity-50 transition-all cursor-pointer"
      >
        {loading ? <Loader2 className="w-4 h-4 animate-spin text-white" /> : <Send className="w-4 h-4 text-white" />}
      </button>
    </form>
  );
}
