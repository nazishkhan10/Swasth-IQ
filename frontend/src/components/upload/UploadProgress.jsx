import React from 'react';
import { CheckCircle2 } from 'lucide-react';

const stages = ['Validating', 'Uploading', 'Saving', 'Complete'];

const UploadProgress = ({ progress = 0 }) => {
  const stageIndex =
    progress < 25 ? 0
    : progress < 75 ? 1
    : progress < 99 ? 2
    : 3;

  return (
    <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm animate-slide-up">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-semibold text-slate-800">
          {stageIndex < 3 ? stages[stageIndex] + '...' : 'Upload Complete!'}
        </span>
        <span className="text-sm font-bold text-sky-600">{progress}%</span>
      </div>

      {/* Progress Bar */}
      <div className="h-2 bg-slate-100 rounded-full overflow-hidden mb-4">
        <div
          className="h-full bg-gradient-to-r from-sky-500 to-teal-500 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Stage Indicators */}
      <div className="flex items-center justify-between">
        {stages.map((stage, i) => (
          <div key={stage} className="flex flex-col items-center gap-1">
            <div
              className={`w-6 h-6 rounded-full flex items-center justify-center transition-all ${
                i < stageIndex
                  ? 'bg-teal-500'
                  : i === stageIndex
                  ? 'bg-sky-500 ring-4 ring-sky-100 animate-pulse-subtle'
                  : 'bg-slate-100'
              }`}
            >
              {i < stageIndex ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-white" />
              ) : (
                <span className="w-2 h-2 rounded-full bg-current opacity-50" />
              )}
            </div>
            <span
              className={`text-[10px] font-medium hidden sm:block ${
                i <= stageIndex ? 'text-slate-700' : 'text-slate-400'
              }`}
            >
              {stage}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UploadProgress;
