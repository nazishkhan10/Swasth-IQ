import React, { useState } from 'react';
import { Cpu, Share2, Layers, Network, ChevronRight } from 'lucide-react';

export function KnowledgeGraphViewer({ graph = {} }) {
  const [selectedType, setSelectedType] = useState('All');
  const nodes = graph.nodes || [];
  const edges = graph.edges || [];

  if (nodes.length === 0) return null;

  const nodeTypes = ['All', ...new Set(nodes.map(n => n.type).filter(Boolean))];

  const filteredNodes = selectedType === 'All'
    ? nodes
    : nodes.filter(n => n.type === selectedType);

  const typeColors = {
    Patient: 'bg-purple-100 text-purple-700 border-purple-200',
    Report: 'bg-sky-100 text-sky-700 border-sky-200',
    Visit: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    Parameter: 'bg-blue-100 text-blue-700 border-blue-200',
    DetectedCondition: 'bg-rose-100 text-rose-700 border-rose-200',
    Recommendation: 'bg-amber-100 text-amber-700 border-amber-200',
    Evidence: 'bg-indigo-100 text-indigo-700 border-indigo-200'
  };

  return (
    <div className="bg-white border border-slate-200/80 rounded-2xl p-5 sm:p-6 shadow-sm space-y-5">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-slate-100 pb-4 gap-3">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Network className="w-5 h-5 text-purple-500" />
            Medical Knowledge Graph Topology Network
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Phase 7 RAG Input Topology ({nodes.length} Entity Nodes, {edges.length} Semantic Relationships)
          </p>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {nodeTypes.map(type => (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={`px-3 py-1 rounded-xl text-xs font-bold transition-all ${
                selectedType === type
                  ? 'bg-purple-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Nodes Map */}
      <div className="bg-slate-50/70 border border-slate-200/80 rounded-2xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Entity Graph Nodes ({filteredNodes.length})
          </span>
          <span className="text-[11px] text-slate-400 font-semibold">Structured Context Vectors</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {filteredNodes.map((n, i) => {
            const badgeStyle = typeColors[n.type] || 'bg-slate-100 text-slate-700 border-slate-200';
            return (
              <div key={i} className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-1.5 bg-white shadow-2xs`}>
                <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full border ${badgeStyle}`}>
                  {n.type}
                </span>
                <span className="text-slate-800 font-medium">{n.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Edges Linkages */}
      <div className="bg-slate-50/70 border border-slate-200/80 rounded-2xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Semantic Relational Edges ({edges.length})
          </span>
          <span className="text-[11px] text-slate-400 font-semibold">Knowledge Dependencies</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
          {edges.map((e, i) => (
            <div key={i} className="bg-white p-3 rounded-xl border border-slate-200/80 text-xs flex items-center justify-between gap-2 shadow-2xs">
              <span className="truncate font-bold text-slate-700 text-[11px]">
                {e.source.replace(/^Node_[^_]+_/, '')}
              </span>
              <span className="text-[10px] font-extrabold text-purple-600 bg-purple-50 px-2 py-0.5 rounded-full border border-purple-200 shrink-0">
                {e.relation}
              </span>
              <span className="truncate font-bold text-slate-700 text-[11px]">
                {e.target.replace(/^Node_[^_]+_/, '')}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

