import React from 'react';
import { FileText, Lock } from 'lucide-react';

export const RecentReportsEmpty = () => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      {/* Illustration */}
      <div className="relative mb-6">
        <div className="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center border-2 border-dashed border-slate-200">
          <FileText className="w-10 h-10 text-slate-300" />
        </div>
        <div className="absolute -bottom-1 -right-1 w-8 h-8 bg-sky-100 rounded-full flex items-center justify-center border-2 border-white">
          <Lock className="w-3.5 h-3.5 text-sky-500" />
        </div>
      </div>

      <h3 className="text-lg font-semibold text-slate-800 mb-2">No reports yet</h3>
      <p className="text-sm text-slate-500 max-w-xs leading-relaxed mb-6">
        Your medical report history will appear here once you start uploading. 
        Upload functionality is coming in Phase 2.
      </p>

      <button
        disabled
        className="flex items-center gap-2 px-5 py-2.5 bg-sky-50 text-sky-400 text-sm font-semibold rounded-xl border border-sky-100 cursor-not-allowed select-none"
      >
        <Lock className="w-4 h-4" />
        Upload First Report — Phase 2
      </button>
    </div>
  );
};

export default RecentReportsEmpty;
