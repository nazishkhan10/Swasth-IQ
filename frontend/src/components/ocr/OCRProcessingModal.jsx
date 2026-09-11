import React, { useEffect, useState } from 'react';
import { Loader2, FileText, Layout, ShieldCheck, CheckCircle } from 'lucide-react';

const STEPS = [
  { id: 1, title: 'Extracting Text...', desc: 'Running document OCR engine', icon: FileText },
  { id: 2, title: 'Detecting Structure...', desc: 'Parsing paragraphs, headers, and tables', icon: Layout },
  { id: 3, title: 'Calculating Confidence...', desc: 'Scoring page layout accuracy', icon: ShieldCheck },
  { id: 4, title: 'Finalizing...', desc: 'Storing structured OCR results', icon: CheckCircle },
];

export const OCRProcessingModal = ({ isOpen }) => {
  const [currentStep, setCurrentStep] = useState(1);

  useEffect(() => {
    if (!isOpen) {
      setCurrentStep(1);
      return;
    }

    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 600);

    return () => clearInterval(interval);
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-6 text-center">
        {/* Animated Icon */}
        <div className="relative inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-500/10 border border-blue-500/30 text-blue-400">
          <Loader2 className="w-8 h-8 animate-spin" />
        </div>

        <div>
          <h3 className="text-lg font-bold text-slate-100">Processing Document Intelligence</h3>
          <p className="text-xs text-slate-400 mt-1">Please wait while we extract text and structure</p>
        </div>

        {/* Steps List */}
        <div className="space-y-3 text-left">
          {STEPS.map((step) => {
            const Icon = step.icon;
            const isDone = currentStep > step.id;
            const isCurrent = currentStep === step.id;

            return (
              <div
                key={step.id}
                className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${
                  isCurrent
                    ? 'bg-blue-500/10 border-blue-500/40 text-blue-300'
                    : isDone
                    ? 'bg-emerald-500/5 border-emerald-500/20 text-emerald-400'
                    : 'bg-slate-950/40 border-slate-800/60 text-slate-500 opacity-60'
                }`}
              >
                <div className="flex-shrink-0">
                  {isDone ? (
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                  ) : isCurrent ? (
                    <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                  ) : (
                    <Icon className="w-5 h-5 text-slate-600" />
                  )}
                </div>
                <div>
                  <h5 className="text-xs font-semibold text-slate-200">{step.title}</h5>
                  <p className="text-[11px] text-slate-400">{step.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default OCRProcessingModal;
