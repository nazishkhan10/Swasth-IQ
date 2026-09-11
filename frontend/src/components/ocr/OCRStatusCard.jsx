import React from 'react';
import { Cpu, Clock, Layers, CheckCircle, RefreshCw } from 'lucide-react';
import ConfidenceBadge from './ConfidenceBadge';

export const OCRStatusCard = ({ ocrData, onRetry }) => {
  if (!ocrData) return null;

  const { status, engine, confidence, page_count, processing_time, version } = ocrData;

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Left Side: Status & Engine info */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-50 border border-indigo-100 rounded-xl text-indigo-600">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-bold text-slate-900">
                Engine: <span className="text-indigo-600 font-mono">{engine || 'Document Intelligence'}</span>
              </h4>
              <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-slate-100 text-slate-600 rounded-md border border-slate-200">
                v{version || 1}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5 flex items-center gap-2 font-medium">
              <span className="capitalize text-emerald-600 font-bold flex items-center gap-1">
                <CheckCircle className="w-3.5 h-3.5" /> {status || 'completed'}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-400" /> {processing_time ? `${processing_time}s` : 'Instant'}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Layers className="w-3.5 h-3.5 text-slate-400" /> {page_count || 1} {page_count === 1 ? 'Page' : 'Pages'}
              </span>
            </p>
          </div>
        </div>

        {/* Right Side: Confidence & Retry */}
        <div className="flex items-center gap-3">
          <ConfidenceBadge confidence={confidence} />

          {onRetry && (
            <button
              onClick={onRetry}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl border border-slate-200 transition-all cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Retry OCR
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default OCRStatusCard;
