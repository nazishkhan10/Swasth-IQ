import React from 'react';
import { ShieldCheck, CheckCircle } from 'lucide-react';

export function ConfidenceCard({ confidenceBreakdown = {} }) {
  const ocr = confidenceBreakdown.ocr_confidence ?? 95;
  const parser = confidenceBreakdown.parser_confidence ?? 93;
  const val = confidenceBreakdown.validation_confidence ?? 90;
  const analysis = confidenceBreakdown.analysis_confidence ?? 94;
  const overall = confidenceBreakdown.overall_confidence ?? 95;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          Layered Pipeline Confidence Breakdown
        </h3>
        <span className="text-xs font-extrabold text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-2.5 py-0.5 rounded-full">
          Overall: {overall}%
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Phase 3 — OCR', val: ocr, color: 'bg-indigo-500' },
          { label: 'Phase 4 — Parser', val: parser, color: 'bg-sky-500' },
          { label: 'Phase 5 — Validation', val: val, color: 'bg-emerald-500' },
          { label: 'Phase 6 — Reasoning', val: analysis, color: 'bg-purple-500' },
        ].map((item, i) => (
          <div key={i} className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-center">
            <div className="text-[11px] font-semibold text-slate-400 mb-1">{item.label}</div>
            <div className="text-xl font-extrabold text-white mb-1">{item.val}%</div>
            <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
              <div className={`h-full ${item.color}`} style={{ width: `${item.val}%` }} />
            </div>
          </div>
        ))}
      </div>

      {confidenceBreakdown.rationale && (
        <p className="text-xs text-slate-400 italic">
          Rationale: {confidenceBreakdown.rationale}
        </p>
      )}
    </div>
  );
}
