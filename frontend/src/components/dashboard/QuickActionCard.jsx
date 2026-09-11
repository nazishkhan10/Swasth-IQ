import React from 'react';
import { Lock } from 'lucide-react';

export const QuickActionCard = ({ icon: Icon, title, description, color = 'slate' }) => {
  const colorMap = {
    blue: 'bg-sky-50 text-sky-600 border-sky-100',
    teal: 'bg-teal-50 text-teal-600 border-teal-100',
    violet: 'bg-violet-50 text-violet-600 border-violet-100',
    amber: 'bg-amber-50 text-amber-600 border-amber-100',
  };

  const iconBg = colorMap[color] || colorMap.blue;

  return (
    <div className="relative group bg-white border border-slate-100 rounded-2xl p-5 shadow-sm cursor-not-allowed overflow-hidden transition-all hover:border-slate-200">
      {/* Coming Soon Badge */}
      <div className="absolute top-3 right-3 flex items-center gap-1 bg-slate-100 text-slate-500 text-[10px] font-semibold px-2 py-0.5 rounded-full">
        <Lock className="w-3 h-3" />
        Phase 2
      </div>

      {/* Overlay */}
      <div className="absolute inset-0 bg-white/40 backdrop-blur-[1px] rounded-2xl z-10" />

      {/* Icon */}
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center border ${iconBg} mb-4`}>
        <Icon className="w-6 h-6" />
      </div>

      <h4 className="text-base font-semibold text-slate-800 mb-1">{title}</h4>
      <p className="text-sm text-slate-500 leading-relaxed">{description}</p>
    </div>
  );
};

export default QuickActionCard;
