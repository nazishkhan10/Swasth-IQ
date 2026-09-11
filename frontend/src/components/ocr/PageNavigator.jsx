import React from 'react';
import { ChevronLeft, ChevronRight, Bookmark } from 'lucide-react';

export const PageNavigator = ({
  currentPage = 1,
  totalPages = 1,
  onPageChange,
  currentVersion = 1,
  onVersionChange
}) => {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 bg-white border border-slate-200 rounded-2xl px-4 py-2.5 text-xs shadow-2xs">
      {/* Page controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(Math.max(1, currentPage - 1))}
          disabled={currentPage <= 1}
          className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 disabled:opacity-40 text-slate-700 font-bold transition-colors cursor-pointer"
          title="Previous Page"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>

        <span className="text-slate-600 font-semibold px-1">
          Page <strong className="text-indigo-600 font-bold">{currentPage}</strong> of <strong className="text-slate-900 font-bold">{totalPages}</strong>
        </span>

        <button
          onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
          disabled={currentPage >= totalPages}
          className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 disabled:opacity-40 text-slate-700 font-bold transition-colors cursor-pointer"
          title="Next Page"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Version Selector */}
      {onVersionChange && (
        <div className="flex items-center gap-2">
          <Bookmark className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-500 font-medium">OCR Version:</span>
          <select
            value={currentVersion}
            onChange={(e) => onVersionChange(Number(e.target.value))}
            className="bg-slate-50 border border-slate-200 text-indigo-600 text-xs font-bold rounded-lg px-2 py-1 focus:outline-none focus:border-indigo-500"
          >
            {Array.from({ length: currentVersion }, (_, i) => i + 1).map((v) => (
              <option key={v} value={v}>
                v{v} {v === currentVersion ? '(Latest)' : ''}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
};

export default PageNavigator;
