import React from 'react';
import { AlertTriangle, ShieldAlert } from 'lucide-react';

export function ConflictAlertCard({ conflicts = [] }) {
  if (conflicts.length === 0) return null;

  return (
    <div className="bg-amber-950/30 border border-amber-800/60 rounded-xl p-4 space-y-3">
      <div className="flex items-center gap-2 text-amber-300 font-bold text-xs">
        <AlertTriangle className="w-4 h-4 text-amber-400" />
        Clinical Contradiction / Mismatch Alert ({conflicts.length})
      </div>

      <div className="space-y-2">
        {conflicts.map((conf, i) => (
          <div key={i} className="bg-slate-950 border border-amber-900/50 rounded-lg p-3 text-xs space-y-1">
            <div className="flex items-center justify-between text-amber-200 font-bold">
              <span>{conf.title}</span>
              <span className="text-[10px] text-rose-400 border border-rose-900 px-2 py-0.5 rounded">
                Confidence Penalty -{Math.round((conf.confidence_penalty || 0.15) * 100)}%
              </span>
            </div>
            <p className="text-slate-300">{conf.description}</p>
            <div className="text-[11px] text-slate-400"><strong className="text-amber-400">Action:</strong> {conf.action_required}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
