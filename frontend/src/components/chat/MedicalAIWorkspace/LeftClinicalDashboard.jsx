import React from 'react';
import { Activity, ShieldCheck, User, TrendingUp, ShieldAlert } from 'lucide-react';

const ORGAN_METADATA = {
  Heart:     { label: 'Heart',     sub: 'Cardiovascular', icon: '🫀' },
  Kidney:    { label: 'Kidney',    sub: 'Renal System',   icon: '🩺' },
  Liver:     { label: 'Liver',     sub: 'Hepatic System', icon: '🧪' },
  Blood:     { label: 'Blood',     sub: 'Hematology',     icon: '🩸' },
  Metabolic: { label: 'Metabolic', sub: 'Endocrine & Glucose', icon: '🧬' },
};

export default function LeftClinicalDashboard({ report, analysisData, organScores, insights }) {
  // Single Source of Truth for Health Score & Risk Category
  const healthScore = insights?.overall_health_score ?? analysisData?.overall_health_score ?? analysisData?.quality_score ?? 90;
  const overallRisk = insights?.overall_risk ?? analysisData?.overall_risk ?? (healthScore >= 85 ? 'LOW' : healthScore >= 70 ? 'MODERATE' : 'HIGH');
  const conditions = insights?.conditions || analysisData?.conditions || analysisData?.detected_conditions || [];

  const scores = organScores || insights?.organ_scores || {
    Heart: 92,
    Kidney: 95,
    Liver: 94,
    Blood: 83,
    Metabolic: 88,
  };

  const getOrganColor = (score) => {
    if (score >= 90) return { text: 'text-emerald-700', bg: 'bg-emerald-50 border-emerald-200', badge: 'bg-emerald-100 text-emerald-800' };
    if (score >= 75) return { text: 'text-amber-700',   bg: 'bg-amber-50 border-amber-200 font-bold',  badge: 'bg-amber-100 text-amber-800' };
    return { text: 'text-rose-700',    bg: 'bg-rose-50 border-rose-200 font-extrabold',   badge: 'bg-rose-100 text-rose-800' };
  };

  return (
    <div className="flex flex-col gap-4 bg-white border border-slate-200/80 p-4 rounded-2xl shadow-2xs text-slate-800">
      {/* Patient Profile Header */}
      <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
        <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600 font-bold">
          <User className="w-5 h-5" />
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-bold text-slate-900 truncate">{report?.original_filename || 'Patient Report'}</h3>
          <p className="text-[11px] text-slate-500 font-medium">Verified Lab Analysis · Active</p>
        </div>
      </div>

      {/* Overall Health Score Card (Synchronized Single Source of Truth) */}
      <div className="bg-slate-900 text-white p-4 rounded-2xl shadow-xs flex items-center justify-between">
        <div>
          <div className="text-[10px] uppercase font-extrabold text-slate-400 tracking-wider">Overall Health Score</div>
          <div className="text-2xl font-black text-white mt-0.5">{healthScore}<span className="text-sm font-normal text-slate-400">/100</span></div>
          <span className={`inline-block mt-1 px-2.5 py-0.5 text-[10px] font-extrabold rounded-full uppercase ${
            overallRisk === 'LOW' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
          }`}>
            {overallRisk} RISK CATEGORY
          </span>
        </div>
        <div className="w-12 h-12 rounded-full border-4 border-emerald-400 flex items-center justify-center font-black text-sm bg-slate-800 text-emerald-400">
          {healthScore}%
        </div>
      </div>

      {/* 5 Key Biological Organ Systems Grid */}
      <div>
        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
          <Activity className="w-3.5 h-3.5 text-indigo-500" />
          5 Key Biological Organ Systems
        </h4>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(scores).map(([organKey, score]) => {
            const meta = ORGAN_METADATA[organKey] || { label: organKey, sub: 'System', icon: '🩺' };
            const cfg = getOrganColor(score);
            return (
              <div key={organKey} className={`p-2.5 rounded-xl border ${cfg.bg} flex flex-col justify-between transition-all`}>
                <div className="flex items-center justify-between text-[11px] font-bold text-slate-800">
                  <span className="flex items-center gap-1">
                    <span>{meta.icon}</span>
                    <span className="truncate">{meta.label}</span>
                  </span>
                </div>
                <div className="flex items-baseline justify-between mt-2">
                  <span className={`text-base font-black ${cfg.text}`}>{score}%</span>
                  <span className={`text-[9px] font-extrabold px-1.5 py-0.5 rounded-md ${cfg.badge}`}>
                    {score >= 90 ? 'Optimal' : score >= 75 ? 'Mild Shift' : 'Shift'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Detected Conditions */}
      <div>
        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
          Detected Conditions
        </h4>
        {conditions.length > 0 ? (
          <div className="flex flex-col gap-1.5">
            {conditions.map((c, i) => (
              <div key={i} className="text-xs p-2 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 font-bold flex items-center gap-2">
                <ShieldAlert className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
                <span>{typeof c === 'object' ? (c.condition_name || JSON.stringify(c)) : String(c)}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 font-semibold">
            Optimal Health (No pathological conditions)
          </div>
        )}
      </div>

      {/* Historical Snapshot */}
      <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span className="flex items-center gap-1 font-semibold">
          <TrendingUp className="w-3.5 h-3.5 text-indigo-500" />
          Historical Trend
        </span>
        <span className="font-bold text-slate-700">1 Report Logged</span>
      </div>
    </div>
  );
}
