import React, { useState } from 'react';
import { Search, Filter, Clock, Tag, MapPin, Award, CheckCircle2 } from 'lucide-react';

const CATEGORIES = ['All', 'CBC', 'LFT', 'KFT', 'Lipid', 'Sugar', 'Thyroid', 'Vitamin', 'Urine'];

const MedicalParameterTable = ({ parameters = [], search, setSearch, selectedCategory, setSelectedCategory }) => {
  const [selectedBbox, setSelectedBbox] = useState(null);

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl overflow-hidden backdrop-blur-md shadow-xl">
      {/* Header Controls: Search & Category Filter Tabs */}
      <div className="p-4 border-b border-slate-800/60 space-y-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Tag className="w-4 h-4 text-sky-400" />
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Structured Medical Parameters ({parameters.length})
            </h3>
          </div>

          {/* Search Input */}
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search parameter, code, value, unit, page..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-950/70 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 transition-colors"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 text-xs"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Category Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 custom-scrollbar">
          <Filter className="w-3.5 h-3.5 text-slate-400 flex-shrink-0 mr-1" />
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                selectedCategory === cat
                  ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/20'
                  : 'bg-slate-800/40 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-700/40'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Parameter Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
              <th className="py-3 px-4">Parameter & Code</th>
              <th className="py-3 px-4">Measured Value</th>
              <th className="py-3 px-4">Normalized Unit</th>
              <th className="py-3 px-4">Reference Range</th>
              <th className="py-3 px-4">Confidence</th>
              <th className="py-3 px-4">Page</th>
              <th className="py-3 px-4 text-right">Validation Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/40 font-mono text-slate-300">
            {parameters.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-10 text-slate-500 text-xs font-sans">
                  No medical parameters found matching filters.
                </td>
              </tr>
            ) : (
              parameters.map((param) => (
                <tr key={param.id} className="hover:bg-slate-800/30 transition-colors group">
                  {/* Parameter Name */}
                  <td className="py-3 px-4 font-sans font-semibold text-slate-100">
                    <div className="flex items-center gap-2">
                      <span>{param.parameter_name}</span>
                      {param.parameter_code && (
                        <span className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] font-mono text-sky-400 border border-slate-700/50">
                          {param.parameter_code}
                        </span>
                      )}
                      <span className="text-[10px] text-slate-500 font-normal ml-auto hidden group-hover:inline-block">
                        {param.category}
                      </span>
                    </div>
                  </td>

                  {/* Value */}
                  <td className="py-3 px-4 font-bold text-sky-300 text-sm">
                    {param.value}
                  </td>

                  {/* Unit */}
                  <td className="py-3 px-4 text-slate-300">
                    {param.unit || <span className="text-slate-600">—</span>}
                  </td>

                  {/* Reference Range */}
                  <td className="py-3 px-4 text-slate-300">
                    {param.reference_range ? (
                      <span className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-[11px]">
                        {param.reference_range}
                        {param.reference_context && param.reference_context !== 'General' && (
                          <span className="text-slate-500 ml-1 text-[9px]">({param.reference_context})</span>
                        )}
                      </span>
                    ) : (
                      <span className="text-slate-600">—</span>
                    )}
                  </td>

                  {/* Confidence */}
                  <td className="py-3 px-4 font-sans">
                    <div className="flex items-center gap-1.5">
                      <div className="w-12 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className="h-full bg-emerald-400 rounded-full"
                          style={{ width: `${(param.confidence * 100).toFixed(0)}%` }}
                        />
                      </div>
                      <span className="text-[10px] text-slate-400">{param.confidence}</span>
                    </div>
                  </td>

                  {/* Page / Source Bbox */}
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">
                      <MapPin className="w-2.5 h-2.5 text-sky-400" />
                      Page {param.page_number}
                    </span>
                  </td>

                  {/* Validation Status Badge — Phase 4: Pending Validation */}
                  <td className="py-3 px-4 text-right font-sans">
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      <Clock className="w-3 h-3 text-amber-400 animate-pulse" />
                      Pending Validation
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default MedicalParameterTable;
