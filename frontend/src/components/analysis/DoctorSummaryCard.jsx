import React from 'react';
import { FileText, Cpu, CheckCircle } from 'lucide-react';

export function DoctorSummaryCard({ doctorSummary = '' }) {
  if (!doctorSummary) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Cpu className="w-4 h-4 text-indigo-400" />
          Doctor View — Clinical Synthesis
        </h3>
        <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
          Formal Medical Terminology
        </span>
      </div>

      <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 leading-relaxed font-mono">
        {doctorSummary}
      </div>
    </div>
  );
}
