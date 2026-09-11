import React from 'react';
import { Activity, ShieldAlert, CheckCircle, Zap } from 'lucide-react';

export function HealthScoreCard({ score = 100, risk = 'LOW', qualityStatus = 'FULL' }) {
  const color = score >= 85 ? '#10b981' : score >= 65 ? '#f59e0b' : score >= 45 ? '#f97316' : '#ef4444';
  const riskBg = risk === 'LOW' ? 'bg-emerald-950/60 text-emerald-300 border-emerald-800'
               : risk === 'MODERATE' ? 'bg-amber-950/60 text-amber-300 border-amber-800'
               : risk === 'HIGH' ? 'bg-orange-950/60 text-orange-300 border-orange-800'
               : 'bg-rose-950/60 text-rose-300 border-rose-800 animate-pulse';

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col sm:flex-row items-center justify-between gap-6">
      <div className="flex items-center gap-5">
        {/* Radial Dial */}
        <div className="relative w-24 h-24 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
            <path
              className="text-slate-800"
              strokeWidth="3.5"
              stroke="currentColor"
              fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <path
              strokeWidth="3.5"
              strokeDasharray={`${score}, 100`}
              strokeLinecap="round"
              stroke={color}
              fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-extrabold text-white">{score}</span>
            <span className="text-[10px] text-slate-500 font-semibold">/100</span>
          </div>
        </div>

        {/* Text Info */}
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Activity className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-bold text-white">Overall Health Score</h3>
            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${riskBg}`}>
              {risk} RISK
            </span>
          </div>
          <p className="text-xs text-slate-400 max-w-md">
            Computed using deterministic clinical rules, organ panel degradation, and multi-system risk weights.
          </p>
        </div>
      </div>

      {/* Quality Gate Status */}
      <div className="flex items-center gap-3 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 flex-shrink-0">
        <Zap className="w-4 h-4 text-amber-400" />
        <div>
          <div className="text-[11px] font-semibold text-slate-400">Quality Gate Status</div>
          <div className="text-xs font-bold text-white flex items-center gap-1">
            <CheckCircle className="w-3 h-3 text-emerald-400" />
            {qualityStatus} ANALYSIS
          </div>
        </div>
      </div>
    </div>
  );
}
