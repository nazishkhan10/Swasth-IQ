import React from 'react';
import { BookOpen, FileCheck, ExternalLink } from 'lucide-react';

export default function SourceCard({ citation }) {
  if (!citation) return null;

  const isGuideline = citation.type === 'guideline';

  return (
    <div className="bg-slate-800/80 text-slate-200 p-2.5 rounded-lg border border-slate-700 text-xs flex flex-col gap-1 hover:border-slate-600 transition-all">
      <div className="flex items-center justify-between gap-2">
        <span className="font-semibold text-slate-100 flex items-center gap-1.5 truncate">
          {isGuideline ? (
            <BookOpen className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
          ) : (
            <FileCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          )}
          <span className="truncate">{citation.title}</span>
        </span>
        <span className="bg-slate-700 text-slate-300 text-[10px] px-1.5 py-0.5 rounded shrink-0">
          P{citation.priority || 1}
        </span>
      </div>

      <div className="text-[11px] text-slate-400 italic line-clamp-2">
        "{citation.quote}"
      </div>

      <div className="text-[10px] text-slate-400 font-medium flex items-center justify-between mt-1">
        <span>Source: {citation.source}</span>
      </div>
    </div>
  );
}
