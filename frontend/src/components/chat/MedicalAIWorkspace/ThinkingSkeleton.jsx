import React, { useState, useEffect } from 'react';
import { CheckCircle2, Loader2, Cpu } from 'lucide-react';

export default function ThinkingSkeleton() {
  const [stepIndex, setStepIndex] = useState(0);

  const steps = [
    'Loading Report Data',
    'Loading Clinical Intelligence',
    'Searching Medical Guidelines',
    'Preparing Validated Context',
    'Generating Explanation (GPT-5 Nano)',
    'Formatting Structured Response Cards'
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setStepIndex((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 400);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="bg-white border border-slate-200 p-4 rounded-2xl shadow-2xs my-3 flex flex-col gap-2 max-w-[85%]">
      <div className="flex items-center gap-2 text-xs font-bold text-slate-800 pb-2 border-b border-slate-100">
        <Cpu className="w-4 h-4 text-emerald-600 animate-spin" />
        AI Reasoning Pipeline Active
      </div>
      <div className="flex flex-col gap-1.5 pt-1">
        {steps.map((st, i) => {
          const isDone = i < stepIndex;
          const isCurrent = i === stepIndex;
          return (
            <div key={i} className="flex items-center gap-2 text-xs">
              {isDone ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              ) : isCurrent ? (
                <Loader2 className="w-3.5 h-3.5 text-indigo-500 animate-spin shrink-0" />
              ) : (
                <div className="w-3.5 h-3.5 rounded-full border border-slate-300 shrink-0" />
              )}
              <span className={isDone ? 'text-slate-700 font-semibold' : isCurrent ? 'text-indigo-600 font-bold' : 'text-slate-400'}>
                {st}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
