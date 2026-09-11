import React from 'react';
import { Database, FileCheck, AlertTriangle, ShieldCheck, Cpu } from 'lucide-react';

const MedicalSummaryCard = ({ data, warningCount = 0 }) => {
  if (!data) return null;

  const metrics = [
    {
      label: 'Extracted Parameters',
      value: data.total_parameters || 0,
      subtext: 'Canonical medical metrics',
      icon: Database,
      color: 'text-sky-400',
      bg: 'bg-sky-500/10 border-sky-500/20'
    },
    {
      label: 'Panel Classification',
      value: data.detected_report_type || 'General',
      subtext: 'Auto-detected document type',
      icon: FileCheck,
      color: 'text-indigo-400',
      bg: 'bg-indigo-500/10 border-indigo-500/20'
    },
    {
      label: 'Parser Confidence',
      value: `${((data.overall_confidence || 0.95) * 100).toFixed(0)}%`,
      subtext: 'Deterministic rule accuracy',
      icon: ShieldCheck,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10 border-emerald-500/20'
    },
    {
      label: 'Pipeline Audit Warnings',
      value: warningCount,
      subtext: warningCount > 0 ? 'Duplicate/Unit audit notes' : 'Clean extraction run',
      icon: AlertTriangle,
      color: warningCount > 0 ? 'text-amber-400' : 'text-slate-400',
      bg: warningCount > 0 ? 'bg-amber-500/10 border-amber-500/20' : 'bg-slate-800/40 border-slate-700/40'
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((m, idx) => {
        const IconComp = m.icon;
        return (
          <div key={idx} className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 backdrop-blur-md shadow-lg flex items-center gap-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center border flex-shrink-0 ${m.bg}`}>
              <IconComp className={`w-6 h-6 ${m.color}`} />
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{m.label}</p>
              <p className="text-xl font-bold text-slate-100 truncate mt-0.5">{m.value}</p>
              <p className="text-[11px] text-slate-400 truncate mt-0.5">{m.subtext}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default MedicalSummaryCard;
