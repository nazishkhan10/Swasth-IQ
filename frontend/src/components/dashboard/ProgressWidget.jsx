import React from 'react';
import { CheckCircle2, Clock } from 'lucide-react';

const phases = [
  { label: 'Account & Auth',        done: true },
  { label: 'Upload & File Mgmt',    done: true },
  { label: 'OCR Processing',        done: false },
  { label: 'AI Analysis Engine',    done: false },
  { label: 'Reports & PDF Export',  done: false },
];

const COMPLETED = phases.filter((p) => p.done).length;
const TOTAL = phases.length;
const PCT = Math.round((COMPLETED / TOTAL) * 100);

export const ProgressWidget = () => {
  return (
    <div className="bg-gradient-to-br from-sky-600 to-teal-600 rounded-2xl p-6 text-white shadow-lg shadow-sky-600/20 h-full">
      <p className="text-xs font-bold uppercase tracking-widest text-sky-100 mb-0.5">Project Roadmap</p>
      <h3 className="text-base font-bold text-white mb-5">Medical Report Analyzer</h3>

      <ul className="space-y-3">
        {phases.map((phase) => (
          <li key={phase.label} className="flex items-center gap-3">
            {phase.done ? (
              <CheckCircle2 className="w-4.5 h-4.5 w-5 h-5 text-emerald-300 flex-shrink-0" />
            ) : (
              <Clock className="w-5 h-5 text-sky-300/60 flex-shrink-0" />
            )}
            <span className={`text-sm font-medium ${phase.done ? 'text-white' : 'text-sky-200/70'}`}>
              {phase.label}
            </span>
            <span className={`ml-auto text-[10px] font-bold px-2 py-0.5 rounded-full ${
              phase.done
                ? 'bg-emerald-500/20 text-emerald-200'
                : 'bg-white/10 text-sky-300 border border-white/10'
            }`}>
              {phase.done ? '✓ Live' : 'Planned'}
            </span>
          </li>
        ))}
      </ul>

      <div className="mt-5 pt-4 border-t border-white/10">
        <div className="flex items-center justify-between text-xs text-sky-200/70 mb-1.5">
          <span>Phase {COMPLETED} of {TOTAL} Complete</span>
          <span>{PCT}%</span>
        </div>
        <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-emerald-400 rounded-full transition-all"
            style={{ width: `${PCT}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default ProgressWidget;
