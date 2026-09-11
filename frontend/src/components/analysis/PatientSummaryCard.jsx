import React from 'react';
import { Heart, CheckCircle2 } from 'lucide-react';

export function PatientSummaryCard({ patientSummary = '' }) {
  if (!patientSummary) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Heart className="w-4 h-4 text-emerald-400" />
          Patient View — Plain Language Summary
        </h3>
        <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
          Easy-to-Understand Language
        </span>
      </div>

      <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 leading-relaxed font-sans">
        {patientSummary}
      </div>
    </div>
  );
}
