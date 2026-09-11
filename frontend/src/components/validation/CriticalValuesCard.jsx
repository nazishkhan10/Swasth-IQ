import React from 'react';
import { ShieldAlert, AlertCircle } from 'lucide-react';

export function CriticalValuesCard({ items }) {
  if (!items || items.length === 0) return null;

  return (
    <div className="bg-rose-50 border-2 border-rose-300/90 rounded-2xl p-4 shadow-sm mb-5 text-slate-800">
      <div className="flex items-center gap-2.5 mb-3 border-b border-rose-200/80 pb-2.5">
        <div className="p-2 bg-rose-600 text-white rounded-xl shadow-xs">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-sm font-extrabold text-rose-900 tracking-wide uppercase flex items-center gap-1.5">
            🚨 Critical Clinical Alert ({items.length})
          </h3>
          <p className="text-xs text-rose-700 font-medium">
            Immediate safety threshold exceedance detected by Phase 5 Critical Rules Engine
          </p>
        </div>
      </div>

      <div className="space-y-2">
        {items.map((item, idx) => (
          <div key={idx} className="bg-white border border-rose-200 rounded-xl p-3 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 shadow-2xs">
            <div>
              <div className="text-xs font-bold text-slate-900 flex items-center gap-2">
                <span>{item.parameter_name}</span>
                <span className="text-[11px] font-mono bg-rose-100 text-rose-800 px-2 py-0.5 rounded-md font-bold border border-rose-200">
                  {item.raw_value} {item.normalized_unit}
                </span>
              </div>
              {item.validation_notes && (
                <p className="text-[11px] text-rose-700 mt-1 flex items-center gap-1 font-medium">
                  <AlertCircle className="w-3.5 h-3.5 flex-shrink-0 text-rose-600" />
                  {item.validation_notes}
                </p>
              )}
            </div>
            <span className="px-2.5 py-1 bg-rose-600 text-white text-[10px] font-bold rounded-lg uppercase shadow-2xs">
              {item.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
