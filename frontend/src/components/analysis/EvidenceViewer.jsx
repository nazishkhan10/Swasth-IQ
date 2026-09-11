import React from 'react';
import { Database, FileText, CheckCircle2, ShieldCheck } from 'lucide-react';

export function EvidenceViewer({ evidence = [] }) {
  if (evidence.length === 0) return null;

  return (
    <div className="bg-white border border-slate-200/80 rounded-2xl p-5 sm:p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Database className="w-5 h-5 text-indigo-500" />
            Clinical Evidence Traceability Matrix
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Full audit log of {evidence.length} validated lab parameter line items
          </p>
        </div>
        <span className="text-xs font-bold text-slate-600 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
          Phase 5 Validated Inputs
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50/80 text-slate-600 text-[11px] font-bold uppercase tracking-wider">
              <th className="py-3 px-3 rounded-l-xl">Evidence ID</th>
              <th className="py-3 px-3">Parameter Name</th>
              <th className="py-3 px-3">Measured Value</th>
              <th className="py-3 px-3">Reference Range</th>
              <th className="py-3 px-3">Deviation Metric</th>
              <th className="py-3 px-3">Validation Conf.</th>
              <th className="py-3 px-3 rounded-r-xl">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-xs">
            {evidence.map((item, idx) => {
              const isNormal = (item.status || 'NORMAL').toUpperCase() === 'NORMAL';
              const statusBg = isNormal ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                             : 'bg-amber-50 text-amber-700 border-amber-200';

              return (
                <tr key={idx} className="hover:bg-slate-50/60 transition">
                  <td className="py-3 px-3 text-indigo-600 font-bold font-mono">{item.evidence_id}</td>
                  <td className="py-3 px-3 text-slate-900 font-bold">{item.parameter_name}</td>
                  <td className="py-3 px-3 text-slate-900 font-extrabold font-mono">
                    {item.canonical_value} <span className="text-slate-500 font-normal">{item.canonical_unit}</span>
                  </td>
                  <td className="py-3 px-3 text-slate-600 font-mono">{item.reference_range || '—'}</td>
                  <td className="py-3 px-3 font-semibold text-slate-600">{item.deviation}</td>
                  <td className="py-3 px-3 text-slate-500 font-mono">{Math.round((item.validation_confidence || 0.9) * 100)}%</td>
                  <td className="py-3 px-3">
                    <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${statusBg}`}>
                      {item.status}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

