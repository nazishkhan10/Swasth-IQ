import React from 'react';
import { Cpu, AlertTriangle } from 'lucide-react';

export default function AIProviderBadge({ provider = 'OpenAI-gpt-5-nano', isFallback = false }) {
  const isOpenAI = provider.toLowerCase().includes('openai') || provider.toLowerCase().includes('gpt');
  const isSarvam = provider.toLowerCase().includes('sarvam');

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border shadow-2xs transition-all ${
        isOpenAI
          ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
          : isSarvam
          ? 'bg-purple-50 text-purple-700 border-purple-200'
          : 'bg-amber-50 text-amber-800 border-amber-300 animate-pulse'
      }`}
    >
      <Cpu className="w-3.5 h-3.5" />
      {isOpenAI
        ? 'OpenAI (GPT-5 Nano)'
        : isSarvam
        ? 'Sarvam 105B'
        : 'GLM 4.7 (Fallback)'}
    </span>
  );
}

