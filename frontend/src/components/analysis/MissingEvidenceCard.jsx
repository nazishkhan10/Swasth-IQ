import React from 'react';
import { HelpCircle, FileText, CheckCircle2 } from 'lucide-react';

export function MissingEvidenceCard({ missingEvidence = [], coverageChecklist = [] }) {
  if (missingEvidence.length === 0 && coverageChecklist.length === 0) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <HelpCircle className="w-4 h-4 text-sky-400" />
          Clinical Coverage &amp; Recommended Follow-up Panels
        </h3>
      </div>

      {/* Coverage Checklist */}
      {coverageChecklist.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
          {coverageChecklist.map((c, i) => (
            <div key={i} className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs">
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-white truncate">{c.panel_name}</span>
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${c.coverage_percentage === 100 ? 'bg-emerald-950 text-emerald-300' : 'bg-amber-950 text-amber-300'}`}>
                  {c.coverage_percentage}%
                </span>
              </div>
              <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden mb-1.5">
                <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${c.coverage_percentage}%` }} />
              </div>
              <div className="text-[10px] text-slate-400 flex justify-between">
                <span>{c.found_count}/{c.total_required} parameters</span>
                <span className="capitalize text-slate-500">{c.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Missing Evidence Items */}
      {missingEvidence.length > 0 && (
        <div className="space-y-2 pt-2">
          {missingEvidence.map((item, idx) => (
            <div key={idx} className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
              <div>
                <div className="font-bold text-sky-300">{item.panel_name} — Incomplete Diagnostic Panel</div>
                <div className="text-slate-400 text-[11px] mt-0.5">{item.recommendation}</div>
              </div>
              <span className="text-[10px] font-semibold text-amber-400 bg-amber-950/40 border border-amber-800/50 px-2 py-1 rounded flex-shrink-0">
                Missing: {item.missing_parameters?.join(', ')}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
