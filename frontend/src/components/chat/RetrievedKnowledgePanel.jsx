import React from 'react';
import { BookOpen } from 'lucide-react';
import SourceCard from './SourceCard';

export default function RetrievedKnowledgePanel({ citations = [] }) {
  const guidelineCitations = citations.filter(c => c.type === 'guideline');

  if (guidelineCitations.length === 0) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col gap-3">
      <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
        <BookOpen className="w-4 h-4 text-cyan-400" />
        Retrieved Guidelines ({guidelineCitations.length})
      </h4>

      <div className="flex flex-col gap-2">
        {guidelineCitations.map((c, i) => (
          <SourceCard key={c.id || i} citation={c} />
        ))}
      </div>
    </div>
  );
}
