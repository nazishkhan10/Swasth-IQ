import React from 'react';
import { ShieldAlert, CheckCircle2, FileText, ChevronRight, HelpCircle, ShieldCheck } from 'lucide-react';

export function DiseaseInsightCard({ conditions = [] }) {
  if (conditions.length === 0) {
    return (
      <div className="bg-emerald-50/60 border border-emerald-200/80 rounded-2xl p-6 text-center shadow-xs">
        <ShieldCheck className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
        <h4 className="text-base font-bold text-emerald-900 mb-1">Optimal Hematologic &amp; Clinical Status</h4>
        <p className="text-xs text-emerald-700 max-w-md mx-auto leading-relaxed">
          All validated laboratory parameters remain within healthy reference boundaries with zero pathological disease markers detected.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200/80 rounded-2xl p-5 sm:p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-500" />
            Detected Clinical Conditions ({conditions.length})
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Evaluated against deterministic clinical diagnostic rule registries
          </p>
        </div>
        <span className="text-xs font-bold text-slate-600 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
          Deterministic Rule Engine
        </span>
      </div>

      <div className="space-y-4">
        {conditions.map((c, i) => {
          const sev = c.severity || 'MODERATE';
          const sevBg = sev === 'CRITICAL' ? 'bg-rose-50 text-rose-700 border-rose-200'
                      : sev === 'HIGH' ? 'bg-amber-50 text-amber-700 border-amber-200'
                      : 'bg-sky-50 text-sky-700 border-sky-200';

          return (
            <div key={i} className="bg-slate-50/70 border border-slate-200/80 rounded-2xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-slate-900">{c.condition_name}</span>
                  <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${sevBg}`}>
                    {sev}
                  </span>
                </div>
                <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
                  {Math.round((c.confidence || 0.9) * 100)}% Confidence
                </span>
              </div>

              {/* Rationale Explainability Box */}
              {c.explanation && (
                <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 space-y-2 text-xs text-slate-700 leading-relaxed shadow-2xs">
                  <div><strong className="text-sky-600">Why Detected:</strong> {c.explanation.why_detected}</div>
                  <div><strong className="text-emerald-600">Evidence Rationale:</strong> {c.explanation.why_confidence}</div>
                  <div><strong className="text-amber-600">Clinical Impact:</strong> {c.explanation.why_risk}</div>
                </div>
              )}

              {/* Supporting Parameters */}
              <div className="flex items-center gap-2 text-xs text-slate-600 flex-wrap">
                <span className="font-bold text-slate-700">Supporting Evidence:</span>
                {c.supporting_parameters?.map((p, idx) => (
                  <span key={idx} className="bg-white border border-slate-200 px-2.5 py-0.5 rounded-full text-xs font-semibold text-slate-800 shadow-2xs">
                    ✓ {p}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

