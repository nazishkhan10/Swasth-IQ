import React from 'react';
import { Database } from 'lucide-react';
import SourceCard from './SourceCard';

export default function EvidencePanel({ citations = [] }) {
  const evidenceCitations = citations.filter(c => c.type === 'evidence');

  if (evidenceCitations.length === 0) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col gap-3">
      <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
        <Database className="w-4 h-4 text-emerald-400" />
        Cited Lab Evidence ({evidenceCitations.length})
      </h4>

      <div className="flex flex-col gap-2">
        {evidenceCitations.map((c, i) => (
          <SourceCard key={c.id || i} citation={c} />
        ))}
      </div>
    </div>
  );
}
