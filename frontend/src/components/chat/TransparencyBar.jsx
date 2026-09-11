import React from 'react';
import { ShieldCheck, BookOpen, Clock, Zap, Database } from 'lucide-react';
import AIProviderBadge from './AIProviderBadge';

export default function TransparencyBar({
  confidence = 0.95,
  provider = 'Sarvam-105B',
  isFallback = false,
  latencyMs = 0,
  evidenceCount = 0,
  guidelineCount = 0,
  knowledgeVersion = '2026.1'
}) {
  const confPct = Math.round(confidence * 100);

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900 text-white px-4 py-2.5 rounded-xl text-xs border border-slate-800 shadow-sm">
      <div className="flex items-center gap-4 flex-wrap">
        {/* Provider */}
        <AIProviderBadge provider={provider} isFallback={isFallback} />

        {/* Confidence */}
        <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
          <ShieldCheck className="w-4 h-4" />
          <span>Confidence: {confPct}%</span>
        </div>

        {/* Evidence */}
        <div className="flex items-center gap-1 text-slate-300">
          <Database className="w-3.5 h-3.5 text-indigo-400" />
          <span>{evidenceCount} Evidence Items</span>
        </div>

        {/* Guidelines */}
        <div className="flex items-center gap-1 text-slate-300">
          <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
          <span>{guidelineCount} Guidelines</span>
        </div>
      </div>

      <div className="flex items-center gap-3 text-slate-400">
        {/* Latency */}
        {latencyMs > 0 && (
          <div className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            <span>{latencyMs} ms</span>
          </div>
        )}

        {/* Knowledge Version */}
        <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono text-[10px]">
          v{knowledgeVersion}
        </span>
      </div>
    </div>
  );
}
