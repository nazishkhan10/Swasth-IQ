import React from 'react';
import { Table as TableIcon } from 'lucide-react';

export const TableViewer = ({ tables = [] }) => {
  if (!tables || tables.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center bg-slate-950/40 rounded-xl border border-slate-800 text-slate-500">
        <TableIcon className="w-8 h-8 mb-2 opacity-50" />
        <p className="text-sm font-medium">No structured tables detected in this page</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {tables.map((table, tIdx) => (
        <div key={tIdx} className="bg-slate-950/60 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <div className="px-4 py-2 bg-slate-900 border-b border-slate-800 flex items-center justify-between text-xs font-semibold text-slate-300">
            <span className="flex items-center gap-2">
              <TableIcon className="w-4 h-4 text-blue-400" />
              Detected Table #{tIdx + 1}
            </span>
            {table.bbox && (
              <span className="text-[10px] font-mono text-slate-500">
                BBox: [{table.bbox.join(', ')}]
              </span>
            )}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              {table.headers && table.headers.length > 0 && (
                <thead className="bg-slate-900/90 text-slate-200 uppercase font-semibold border-b border-slate-800">
                  <tr>
                    {table.headers.map((h, hIdx) => (
                      <th key={hIdx} className="px-4 py-2.5 font-medium border-r border-slate-800/60 last:border-0">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
              )}
              <tbody className="divide-y divide-slate-800/50 text-slate-300">
                {table.rows && table.rows.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-slate-900/50 transition-colors">
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="px-4 py-2 border-r border-slate-800/40 last:border-0 font-mono">
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TableViewer;
