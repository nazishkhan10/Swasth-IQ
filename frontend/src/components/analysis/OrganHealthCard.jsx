import React, { useState } from 'react';
import { Activity, ShieldCheck, Heart, ChevronDown, ChevronUp } from 'lucide-react';

export function OrganHealthCard({ organPanels = {}, organDependencies = [] }) {
  const [expandedOrgan, setExpandedOrgan] = useState(null);
  const panelList = Object.entries(organPanels);

  if (panelList.length === 0) return null;

  return (
    <div className="bg-white border border-slate-200/80 rounded-2xl p-5 sm:p-6 shadow-sm space-y-5">
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
            <Activity className="w-5 h-5 text-sky-500" />
            Organ System Health &amp; Clinical Panels
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Systemic evaluation of 10 organ panels and cross-organ linkages
          </p>
        </div>
        <span className="text-xs font-bold text-slate-600 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
          {panelList.length} Organ Panels Evaluated
        </span>
      </div>

      {/* Grid of Organ Panels */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {panelList.map(([name, data]) => {
          const score = data.score ?? 100;
          const status = data.status || 'Optimal Health';
          const isExpanded = expandedOrgan === name;
          const params = data.parameters || [];

          const badgeColor = score >= 85 ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                           : score >= 65 ? 'bg-amber-50 text-amber-700 border-amber-200'
                           : 'bg-rose-50 text-rose-700 border-rose-200';

          return (
            <div key={name} className="bg-slate-50/70 border border-slate-200/80 rounded-2xl p-4 flex flex-col justify-between transition hover:shadow-sm">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-bold text-slate-900">{name} Panel</span>
                  <span className={`text-xs font-extrabold px-2.5 py-0.5 rounded-full border ${badgeColor}`}>
                    {score}/100
                  </span>
                </div>
                <div className="text-xs font-bold text-slate-600 mb-3">{status}</div>

                {/* Progress bar */}
                <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden mb-3">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      score >= 85 ? 'bg-emerald-500' : score >= 65 ? 'bg-amber-500' : 'bg-rose-500'
                    }`}
                    style={{ width: `${score}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="text-xs text-slate-500 border-t border-slate-200/80 pt-3 flex items-center justify-between">
                  {data.abnormal_parameters_count > 0 ? (
                    <span className="text-amber-600 font-bold">{data.abnormal_parameters_count} parameter(s) shift</span>
                  ) : (
                    <span className="text-emerald-600 font-semibold flex items-center gap-1">
                      <ShieldCheck className="w-3.5 h-3.5" /> All parameters optimal
                    </span>
                  )}

                  {params.length > 0 && (
                    <button
                      onClick={() => setExpandedOrgan(isExpanded ? null : name)}
                      className="text-xs font-bold text-sky-600 hover:text-sky-700 flex items-center gap-1"
                    >
                      {isExpanded ? 'Hide' : 'Details'} {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>
                  )}
                </div>

                {/* Expandable Parameter List */}
                {isExpanded && params.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-200 space-y-2 animate-fade-in">
                    {params.map((p, idx) => (
                      <div key={idx} className="bg-white p-2.5 rounded-xl border border-slate-200/80 flex items-center justify-between text-xs">
                        <div>
                          <span className="font-bold text-slate-800">{p.name}</span>
                          <span className="text-[10px] text-slate-400 block">Ref: {p.ref_range || 'Standard'}</span>
                        </div>
                        <div className="text-right">
                          <span className="font-bold text-slate-900">{p.value} {p.unit}</span>
                          <span className={`text-[10px] font-bold block ${
                            p.status === 'NORMAL' ? 'text-emerald-600' : 'text-amber-600'
                          }`}>{p.status}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Cross-organ Linkages */}
      {organDependencies.length > 0 && (
        <div className="bg-sky-50/50 border border-sky-100 rounded-2xl p-4 mt-3">
          <div className="text-xs font-bold text-sky-900 mb-3 flex items-center gap-1.5">
            <Heart className="w-4 h-4 text-sky-500" /> Cross-Organ Dependency Cascade
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {organDependencies.map((link, idx) => (
              <div key={idx} className="bg-white border border-sky-100 rounded-xl p-3 text-xs shadow-sm">
                <div className="flex items-center gap-2 font-bold text-slate-900 mb-1">
                  <span className="text-sky-600">{link.source}</span>
                  <span className="text-slate-400">➔</span>
                  <span className="text-indigo-600">{link.target}</span>
                  <span className="ml-auto text-[10px] font-bold px-2.5 py-0.5 bg-sky-100 text-sky-700 rounded-full">
                    {link.relationship}
                  </span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">{link.clinical_description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

