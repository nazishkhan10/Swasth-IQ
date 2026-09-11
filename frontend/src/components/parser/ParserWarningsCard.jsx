import React, { useState } from 'react';
import { AlertTriangle, ChevronDown, ChevronUp, Info } from 'lucide-react';

const ParserWarningsCard = ({ warnings = [] }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!warnings || warnings.length === 0) return null;

  return (
    <div className="bg-slate-900/60 border border-amber-500/20 rounded-2xl overflow-hidden backdrop-blur-md shadow-lg">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-5 py-3.5 bg-amber-500/5 hover:bg-amber-500/10 flex items-center justify-between transition-colors text-left"
      >
        <div className="flex items-center gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          <span className="text-xs font-bold text-amber-300 uppercase tracking-wider">
            Pipeline Audit & Parse Warnings ({warnings.length})
          </span>
          <span className="text-[11px] text-slate-400 hidden sm:inline">
            — Duplicate resolutions & unit checks
          </span>
        </div>

        <div className="flex items-center gap-2 text-slate-400">
          <span className="text-xs font-semibold">{isOpen ? 'Hide Audit Log' : 'View Audit Log'}</span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {isOpen && (
        <div className="p-4 space-y-2 border-t border-amber-500/10 bg-slate-950/50 max-h-60 overflow-y-auto custom-scrollbar">
          {warnings.map((w, idx) => (
            <div key={idx} className="flex items-start gap-3 p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs">
              <Info className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold text-amber-300">{w.warning_type}</span>
                  <span className="text-[10px] text-slate-500 font-mono">Page {w.page_number}</span>
                </div>
                <p className="text-slate-300 mt-0.5">{w.message}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ParserWarningsCard;
