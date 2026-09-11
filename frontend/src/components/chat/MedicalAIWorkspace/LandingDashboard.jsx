import React from 'react';
import { Sparkles, Bot, ArrowRight } from 'lucide-react';

export default function LandingDashboard({ starters = [], onSelectQuestion }) {
  return (
    <div className="flex flex-col gap-4 bg-white border border-slate-200/80 p-5 rounded-2xl shadow-2xs text-slate-800">
      {/* Greeting Banner (Executive Theme) */}
      <div className="flex items-center gap-3.5 bg-gradient-to-r from-emerald-50 via-teal-50 to-indigo-50 border border-emerald-200/80 p-4 rounded-2xl shadow-2xs">
        <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold shrink-0 shadow-xs">
          <Bot className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
            Clinical Intelligence Ready
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
              Validated
            </span>
          </h3>
          <p className="text-xs text-slate-600 font-medium mt-0.5">
            GPT-5 Nano reasoning engine connected strictly to your verified lab dataset.
          </p>
        </div>
      </div>

      {/* Copilot-Style Prompt Starter Chips */}
      <div>
        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
          Ask Swasth-IQ Copilot:
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {starters.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => onSelectQuestion(chip.query)}
              className="p-3.5 rounded-2xl border border-slate-200/90 bg-slate-50/50 hover:bg-indigo-50/40 hover:border-indigo-300 text-left transition-all group flex items-center justify-between shadow-2xs cursor-pointer"
            >
              <div className="min-w-0 flex-1 pr-2">
                <div className="text-xs font-bold text-slate-900 group-hover:text-indigo-700 leading-snug line-clamp-2">
                  {chip.label}
                </div>
                <div className="text-[11px] text-slate-500 truncate mt-1 font-medium">
                  {chip.query}
                </div>
              </div>
              <div className="w-7 h-7 rounded-xl bg-white border border-slate-200 group-hover:border-indigo-300 group-hover:bg-indigo-600 group-hover:text-white flex items-center justify-center text-slate-400 shrink-0 transition-all">
                <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
