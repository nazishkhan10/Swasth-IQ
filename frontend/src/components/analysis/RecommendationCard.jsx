import React, { useState } from 'react';
import { CheckCircle2, ChevronRight, Activity, Zap, Sparkles } from 'lucide-react';

export function RecommendationCard({ recommendations = [] }) {
  const [selectedCategory, setSelectedCategory] = useState('All');

  if (recommendations.length === 0) return null;

  const categories = ['All', ...new Set(recommendations.map(r => r.category).filter(Boolean))];

  const filtered = selectedCategory === 'All'
    ? recommendations
    : recommendations.filter(r => r.category === selectedCategory);

  return (
    <div className="bg-white border border-slate-200/80 rounded-2xl p-5 sm:p-6 shadow-sm space-y-5">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" />
            Categorized Clinical Recommendations ({recommendations.length})
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Actionable clinical guidance stratified by triage levels
          </p>
        </div>

        {/* Category Tabs */}
        <div className="flex flex-wrap gap-1.5">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-xl text-xs font-bold transition-all ${
                selectedCategory === cat
                  ? 'bg-amber-500 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((r, i) => {
          const prio = r.priority || 'INFORMATIONAL';
          const prioBg = prio === 'CRITICAL' ? 'bg-rose-50 text-rose-700 border-rose-200'
                       : prio === 'HIGH' ? 'bg-amber-50 text-amber-700 border-amber-200'
                       : prio === 'MEDIUM' ? 'bg-sky-50 text-sky-700 border-sky-200'
                       : 'bg-slate-100 text-slate-600 border-slate-200';

          return (
            <div key={i} className="bg-slate-50/70 border border-slate-200/80 rounded-2xl p-4 flex flex-col justify-between space-y-3 transition hover:shadow-sm">
              <div className="space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-bold text-slate-900">{r.title}</span>
                  <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${prioBg}`}>
                    {prio}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold text-slate-500 bg-white px-2.5 py-0.5 rounded-full border border-slate-200">
                    {r.category}
                  </span>
                  <span className="text-[10px] font-semibold text-slate-400">
                    Triage: {r.triage_level || 'Routine'}
                  </span>
                </div>

                <div className="text-xs text-slate-800 font-semibold bg-white p-3 rounded-xl border border-slate-200/80 leading-relaxed">
                  👉 {r.action}
                </div>
              </div>

              <p className="text-xs text-slate-500 italic bg-slate-100/50 p-2.5 rounded-xl border border-slate-200/60">
                <strong className="not-italic text-slate-700 font-bold">Rationale:</strong> {r.rationale}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

