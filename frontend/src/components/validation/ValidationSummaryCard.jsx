/**
 * ValidationSummaryCard — Phase 5 (Clinical Hardening)
 *
 * Shows aggregate clinical statistics: Normal | Low | High | Critical |
 * Invalid | Qualitative | Unknown | Warnings | Confidence
 * + Data Quality Score gauge for Phase 6 AI gating.
 */
import React from 'react';
import {
  Activity, CheckCircle, ArrowDown, ArrowUp, ShieldAlert,
  HelpCircle, AlertTriangle, Download, Zap, Database,
} from 'lucide-react';

const StatCard = ({ icon: Icon, label, value, color, pulse = false }) => (
  <div className={`rounded-2xl border p-3 text-center transition hover:shadow-sm ${color}`}>
    <div className="flex items-center justify-center gap-1 text-[10px] font-bold uppercase tracking-wider mb-1 opacity-90">
      <Icon className={`w-3.5 h-3.5 ${pulse ? 'animate-pulse' : ''}`} />
      {label}
    </div>
    <div className={`text-2xl font-extrabold ${pulse && value > 0 ? 'animate-pulse' : ''}`}>{value ?? 0}</div>
  </div>
);

export function ValidationSummaryCard({ summary, qualityScore, onExport }) {
  if (!summary) return null;

  const total = (summary.normal || 0) + (summary.low || 0) + (summary.high || 0)
    + (summary.critical || 0) + (summary.unknown || 0)
    + (summary.invalid || 0) + (summary.qualitative || 0);
  const conf  = Math.round((summary.overall_validation_confidence || 0) * 100);
  const qs    = qualityScore ?? null;
  const qsColor = qs == null ? '#64748b' : qs >= 80 ? '#16a34a' : qs >= 60 ? '#d97706' : '#dc2626';
  const aiReady = qs != null && qs >= 60;

  return (
    <div className="bg-white border border-slate-200/80 rounded-2xl p-5 sm:p-6 shadow-sm space-y-4">
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-4 border-b border-slate-100">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-sky-600" />
            Phase 5 — Medical Validation Engine
            <span className="ml-2 inline-flex items-center gap-1 text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              <CheckCircle className="w-3.5 h-3.5" /> Complete
            </span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Clinical Hardening · Unit Normalization · Demographic Reference Ranges
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => onExport('json')}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl border border-slate-200 transition"
          >
            <Download className="w-3.5 h-3.5 text-sky-600" /> JSON
          </button>
          <button
            onClick={() => onExport('csv')}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-sky-600 hover:bg-sky-700 text-white text-xs font-bold rounded-xl transition shadow-xs"
          >
            <Download className="w-3.5 h-3.5" /> CSV
          </button>
        </div>
      </div>

      {/* ── Stat Cards Grid ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5">
        <StatCard icon={CheckCircle}  label="Normal"     value={summary.normal}
          color="bg-emerald-50/70 text-emerald-800 border-emerald-200" />
        <StatCard icon={ArrowDown}    label="Low"         value={summary.low}
          color="bg-sky-50/70 text-sky-800 border-sky-200" />
        <StatCard icon={ArrowUp}      label="High"        value={summary.high}
          color="bg-amber-50/70 text-amber-800 border-amber-200" />
        <StatCard icon={ShieldAlert}  label="Critical"    value={summary.critical}
          color={`bg-rose-50/70 text-rose-800 border-rose-200 ${summary.critical > 0 ? 'ring-2 ring-rose-400' : ''}`}
          pulse={summary.critical > 0} />
        <StatCard icon={AlertTriangle} label="Invalid"    value={summary.invalid || 0}
          color="bg-orange-50/70 text-orange-800 border-orange-200" />
        <StatCard icon={Database}     label="Qualitative" value={summary.qualitative || 0}
          color="bg-purple-50/70 text-purple-800 border-purple-200" />
        <StatCard icon={HelpCircle}   label="Unknown"     value={summary.unknown}
          color="bg-slate-100/70 text-slate-700 border-slate-200" />
        <div className="rounded-2xl border bg-indigo-50/70 border-indigo-200 text-indigo-900 p-3 text-center">
          <div className="text-[10px] font-bold uppercase tracking-wider mb-1 opacity-80">Val. Conf.</div>
          <div className="text-2xl font-extrabold">{conf}%</div>
          <div className="w-full h-1.5 bg-slate-200 rounded-full mt-1.5 overflow-hidden">
            <div className={`h-full rounded-full ${conf >= 90 ? 'bg-emerald-500' : conf >= 75 ? 'bg-amber-500' : 'bg-rose-500'}`}
              style={{ width: `${conf}%` }} />
          </div>
        </div>
      </div>

      {/* ── Data Quality Score ───────────────────────────────────────────── */}
      {qs != null && (
        <div className="bg-slate-50/70 border border-slate-200/80 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                <Zap className="w-4 h-4 text-amber-500" /> Data Quality Score
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Phase 6 AI readiness gate</div>
            </div>
            <div style={{ color: qsColor }} className="text-3xl font-extrabold">
              {qs}<span className="text-base font-normal text-slate-400">/100</span>
            </div>
          </div>
          <div className="w-full h-2.5 bg-slate-200 rounded-full overflow-hidden">
            <div className="h-full rounded-full transition-all duration-500"
              style={{ width: `${qs}%`, background: qsColor }} />
          </div>
          <div className="flex justify-between mt-2">
            <span className="text-[10px] text-slate-400 font-semibold">0 — Poor</span>
            <span className="text-[10px] font-bold" style={{ color: qsColor }}>
              {aiReady ? 'Passed — Ready for Clinical Intelligence' : 'Quality Check Required'}
            </span>
            <span className="text-[10px] text-slate-400 font-semibold">100 — Excellent</span>
          </div>
        </div>
      )}

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pt-3 border-t border-slate-100">
        <p className="text-xs text-slate-600">
          <strong className="text-slate-900">{total}</strong> total parameters ·{' '}
          <strong className="text-emerald-700">{summary.normal || 0}</strong> optimal,{' '}
          <strong className="text-amber-700">{(summary.low || 0) + (summary.high || 0)}</strong> shifted,{' '}
          <strong className="text-rose-700">{summary.critical || 0}</strong> critical
        </p>
        <span className={`inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1 rounded-full border ${
          aiReady ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
                  : 'text-amber-700 bg-amber-50 border-amber-200'}`}>
          <Zap className="w-3.5 h-3.5" />
          {aiReady ? 'Clinical Intelligence Ready' : 'Quality Verification Required'}
        </span>
      </div>
    </div>
  );
}

