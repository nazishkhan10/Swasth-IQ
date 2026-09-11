import React from 'react';
import { Activity, ArrowUp, ArrowDown, Minus } from 'lucide-react';

export function TimelineViewer({ timelines = [], timelineDeltas = [] }) {
  if (timelines.length === 0 && timelineDeltas.length === 0) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Activity className="w-4 h-4 text-indigo-400" />
          Longitudinal Visit Timelines &amp; Parameter Trajectories
        </h3>
        <span className="text-xs text-slate-500 font-semibold">{timelines.length} Visit Checkpoints</span>
      </div>

      {/* Parameter Deltas */}
      {timelineDeltas.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs font-bold text-slate-300 mb-1">Inter-Visit Parameter Trajectory Deltas</div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {timelineDeltas.map((d, i) => {
              const icon = d.trend === 'Increasing' ? <ArrowUp className="w-3.5 h-3.5 text-rose-400" />
                         : d.trend === 'Decreasing' ? <ArrowDown className="w-3.5 h-3.5 text-emerald-400" />
                         : <Minus className="w-3.5 h-3.5 text-slate-400" />;

              return (
                <div key={i} className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs space-y-1">
                  <div className="flex items-center justify-between font-bold text-white">
                    <span className="flex items-center gap-1">
                      {icon} {d.parameter_name}
                    </span>
                    <span className="text-indigo-300 font-mono">
                      {d.previous_value} ➔ {d.current_value} {d.unit}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400">{d.interpretation}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
