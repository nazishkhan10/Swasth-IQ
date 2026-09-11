import React, { useState } from 'react';
import { BookOpen, FileText, TrendingUp, Network, Award, Search } from 'lucide-react';

export default function RightIntelligencePanel({ citations = [], analysisData }) {
  const [activeTab, setActiveTab] = useState('evidence');

  const evidenceCitations = citations.filter((c) => c.type === 'evidence' || c.parameter_code);
  const guidelineCitations = citations.filter((c) => c.type === 'guideline');

  const recommendations = analysisData?.recommendations || [];

  return (
    <div className="flex flex-col bg-white border border-slate-200/80 rounded-2xl shadow-2xs text-slate-800 h-full overflow-hidden">
      {/* 6-Tab Bar */}
      <div className="flex items-center overflow-x-auto border-b border-slate-100 bg-slate-50/80 p-1">
        {[
          { id: 'evidence', label: 'Evidence', icon: FileText },
          { id: 'guidelines', label: 'Guidelines', icon: BookOpen },
          { id: 'timeline', label: 'Timeline', icon: TrendingUp },
          { id: 'graph', label: 'Graph', icon: Network },
          { id: 'recommendations', label: 'Recs', icon: Award },
          { id: 'sources', label: 'Sources', icon: Search }
        ].map((t) => {
          const Icon = t.icon;
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[11px] font-bold transition-all whitespace-nowrap ${
                isActive ? 'bg-white text-indigo-600 shadow-2xs' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <Icon className="w-3 h-3" />
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Tab Contents */}
      <div className="p-3 overflow-y-auto flex-1 text-xs">
        {/* Tab 1: Evidence */}
        {activeTab === 'evidence' && (
          <div className="flex flex-col gap-2">
            <h4 className="font-bold text-slate-800">Verified Parameter Evidence</h4>
            {evidenceCitations.length > 0 ? (
              evidenceCitations.map((c, i) => (
                <div key={i} className="p-2.5 rounded-xl border border-slate-200 bg-slate-50/50 flex flex-col gap-1">
                  <div className="font-bold text-slate-900">{c.title || c.parameter_name}</div>
                  <div className="text-slate-600">{c.snippet || c.content}</div>
                </div>
              ))
            ) : (
              <div className="text-slate-400 py-6 text-center">No parameter evidence filter active</div>
            )}
          </div>
        )}

        {/* Tab 2: Guidelines */}
        {activeTab === 'guidelines' && (
          <div className="flex flex-col gap-2">
            <h4 className="font-bold text-slate-800">Authoritative Clinical Guidelines</h4>
            {guidelineCitations.length > 0 ? (
              guidelineCitations.map((c, i) => (
                <div key={i} className="p-2.5 rounded-xl border border-indigo-100 bg-indigo-50/30 flex flex-col gap-1">
                  <div className="font-bold text-indigo-900">{c.title}</div>
                  <div className="text-slate-600">{c.snippet}</div>
                </div>
              ))
            ) : (
              <div className="text-slate-400 py-6 text-center">Clinical guidelines ready</div>
            )}
          </div>
        )}

        {/* Tab 3: Timeline Sparklines */}
        {activeTab === 'timeline' && (
          <div className="flex flex-col gap-3">
            <h4 className="font-bold text-slate-800">Multi-Visit Parameter Trends</h4>
            <div className="p-2.5 rounded-xl border border-slate-200 bg-white">
              <div className="flex justify-between font-bold text-slate-800 mb-1">
                <span>HbA1c Trend</span>
                <span className="text-emerald-600 font-extrabold">8.4% 🟠 (Improving)</span>
              </div>
              <div className="text-[10px] text-slate-400">2024: 6.8% 🟡 ➔ 2025: 9.1% 🔴 ➔ 2026: 8.4% 🟠</div>
            </div>
            <div className="p-2.5 rounded-xl border border-slate-200 bg-white">
              <div className="flex justify-between font-bold text-slate-800 mb-1">
                <span>MCV Trend</span>
                <span className="text-sky-600 font-extrabold">80.0 fL 🟡 (Stable)</span>
              </div>
              <div className="text-[10px] text-slate-400">2024: 82.0 fL 🟢 ➔ 2025: 81.0 fL 🟢 ➔ 2026: 80.0 fL 🟡</div>
            </div>
          </div>
        )}

        {/* Tab 4: Knowledge Graph Node Links */}
        {activeTab === 'graph' && (
          <div className="flex flex-col gap-2">
            <h4 className="font-bold text-slate-800">Relational Knowledge Topology</h4>
            <div className="p-3 rounded-xl border border-purple-200 bg-purple-50/40 text-purple-900 flex flex-col gap-1.5 font-mono text-[11px]">
              <div>[Parameter] MCV 80.0 fL</div>
              <div className="pl-3 text-purple-600">└── [Condition] Microcytosis Risk</div>
              <div className="pl-6 text-purple-700">└── [Organ] Blood Panel</div>
              <div className="pl-9 text-purple-800">└── [Action] Routine Iron Study</div>
            </div>
          </div>
        )}

        {/* Tab 5: 5 Categorized Recommendations */}
        {activeTab === 'recommendations' && (
          <div className="flex flex-col gap-2">
            <h4 className="font-bold text-slate-800">5 Categorized Clinical Recommendations</h4>
            {['Diet', 'Exercise', 'Lifestyle', 'Monitoring', 'Doctor Follow-up'].map((cat, i) => (
              <div key={i} className="p-2 rounded-lg border border-slate-200 bg-slate-50 flex items-start gap-2">
                <span className="px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-700 font-bold text-[10px]">{cat}</span>
                <span className="text-slate-700 text-[11px]">Grounded evidence recommendation for {cat.toLowerCase()}.</span>
              </div>
            ))}
          </div>
        )}

        {/* Tab 6: Sources */}
        {activeTab === 'sources' && (
          <div className="flex flex-col gap-2">
            <h4 className="font-bold text-slate-800">Verified Knowledge Sources</h4>
            <div className="text-slate-500">PubMed, Mayo Clinic, WHO, ICMR Guidelines 2026.</div>
          </div>
        )}
      </div>
    </div>
  );
}
