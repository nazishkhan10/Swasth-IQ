import React, { useState } from 'react';
import { AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';

const TYPE_COLORS = {
  'Missing Reference':   'text-amber-900 bg-white border-amber-200',
  'Unknown Unit':        'text-orange-900 bg-white border-orange-200',
  'Negative Value':      'text-red-900 bg-white border-red-200',
  'Duplicate Parameter': 'text-purple-900 bg-white border-purple-200',
  'Unknown Parameter':   'text-slate-800 bg-white border-slate-200',
  'Invalid Unit':        'text-orange-900 bg-white border-orange-200',
  'Missing Metadata':    'text-yellow-900 bg-white border-yellow-200',
  'Validation Warning':  'text-amber-900 bg-white border-amber-200',
};

export function ValidationWarningsCard({ warnings }) {
  const [expanded, setExpanded] = useState(true);

  if (!warnings || warnings.length === 0) return null;

  return (
    <div className="bg-amber-50/60 border border-amber-200 rounded-2xl overflow-hidden shadow-2xs mb-4">
      {/* Header (collapsible) */}
      <button
        onClick={() => setExpanded(x => !x)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-amber-100/50 transition cursor-pointer"
      >
        <div className="flex items-center gap-2 text-amber-900 text-xs font-bold uppercase tracking-wider">
          <AlertTriangle className="w-4 h-4 text-amber-600" />
          Validation Engine Warnings ({warnings.length})
          <span className="text-[11px] font-normal text-amber-700 capitalize"> — Review before AI analysis</span>
        </div>
        {expanded
          ? <ChevronUp className="w-4 h-4 text-amber-600" />
          : <ChevronDown className="w-4 h-4 text-amber-600" />}
      </button>

      {expanded && (
        <div className="px-4 pb-3 space-y-1.5 max-h-56 overflow-y-auto">
          {warnings.map((w, idx) => {
            const typeClass = TYPE_COLORS[w.warning_type] || TYPE_COLORS['Validation Warning'];
            return (
              <div
                key={idx}
                className={`flex items-start justify-between gap-3 text-xs border rounded-xl p-2.5 shadow-2xs ${typeClass}`}
              >
                <div className="min-w-0">
                  <span className="font-extrabold text-amber-800">[{w.warning_type || 'Warning'}]</span>
                  {' '}
                  <span className="text-slate-700 font-medium">{w.message}</span>
                  {w.parameter_name && (
                    <span className="ml-1 font-mono text-slate-500 text-[11px]">({w.parameter_name})</span>
                  )}
                </div>
                {w.page_number && (
                  <span className="shrink-0 text-[10px] font-bold text-slate-400">pg {w.page_number}</span>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
