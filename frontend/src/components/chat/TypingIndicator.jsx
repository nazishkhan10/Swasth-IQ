import React from 'react';
import { Bot } from 'lucide-react';

export default function TypingIndicator({ provider = 'Sarvam-105B' }) {
  return (
    <div className="flex items-start gap-3 my-3">
      <div className="w-8 h-8 rounded-full bg-purple-900/60 border border-purple-500/30 flex items-center justify-center shrink-0">
        <Bot className="w-4 h-4 text-purple-400 animate-pulse" />
      </div>
      <div className="bg-slate-800 text-slate-300 px-4 py-3 rounded-2xl rounded-tl-xs border border-slate-700 text-xs flex items-center gap-2">
        <span className="font-semibold text-purple-300">{provider} thinking</span>
        <div className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
          <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
          <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
        </div>
      </div>
    </div>
  );
}
