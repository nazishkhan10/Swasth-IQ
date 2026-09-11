import React from 'react';
import { Cpu, ShieldCheck } from 'lucide-react';

export function AnalysisVersionCard({ versioning = {}, hash = '' }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
      <div className="flex items-center gap-2">
        <Cpu className="w-4 h-4 text-indigo-400" />
        <span className="font-bold text-white">Engine Versioning &amp; SHA256 Determinism Audit</span>
      </div>

      <div className="flex items-center gap-2 flex-wrap font-mono text-[11px]">
        <span className="bg-slate-950 border border-slate-800 px-2 py-0.5 rounded text-indigo-300">
          Engine v{versioning.analysis_version || '3.0.0'}
        </span>
        <span className="bg-slate-950 border border-slate-800 px-2 py-0.5 rounded text-sky-300">
          Rules v{versioning.rule_version || '1.1.0'}
        </span>
        <span className="bg-slate-950 border border-slate-800 px-2 py-0.5 rounded text-emerald-300">
          Ref DB v{versioning.reference_db_version || '2026.1'}
        </span>
        {hash && (
          <span className="bg-slate-950 border border-slate-800 px-2 py-0.5 rounded text-slate-400 font-bold" title={hash}>
            SHA: {hash.substring(0, 12)}…
          </span>
        )}
      </div>
    </div>
  );
}
