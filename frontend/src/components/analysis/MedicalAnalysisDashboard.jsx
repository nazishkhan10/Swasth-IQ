import React, { useState, useEffect } from 'react';
import { analysisApi } from '../../services/analysisApi';
import { HealthScoreCard } from './HealthScoreCard';
import { OrganHealthCard } from './OrganHealthCard';
import { DiseaseInsightCard } from './DiseaseInsightCard';
import { ConflictAlertCard } from './ConflictAlertCard';
import { MissingEvidenceCard } from './MissingEvidenceCard';
import { EvidenceViewer } from './EvidenceViewer';
import { RecommendationCard } from './RecommendationCard';
import { DoctorSummaryCard } from './DoctorSummaryCard';
import { PatientSummaryCard } from './PatientSummaryCard';
import { TimelineViewer } from './TimelineViewer';
import { ConfidenceCard } from './ConfidenceCard';
import { KnowledgeGraphViewer } from './KnowledgeGraphViewer';
import { AnalysisVersionCard } from './AnalysisVersionCard';

import {
  Activity, Cpu, ShieldCheck, Heart, FileText,
  RefreshCw, Loader2, Zap, Database
} from 'lucide-react';

export function MedicalAnalysisDashboard({ reportId }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reRunning, setReRunning] = useState(false);
  const [error, setError] = useState(null);
  const [activeSubTab, setActiveSubTab] = useState('overview');

  const loadAnalysis = async (force = false) => {
    if (force) setReRunning(true);
    else setLoading(true);
    setError(null);
    try {
      const data = await analysisApi.runAnalysis(reportId, force);
      setAnalysis(data);
    } catch (err) {
      console.error('Phase 6 Analysis error:', err);
      setError(err?.response?.data?.detail || 'Clinical Intelligence Engine execution failed.');
    } finally {
      setLoading(false);
      setReRunning(false);
    }
  };

  useEffect(() => {
    if (reportId) loadAnalysis(false);
  }, [reportId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-400 gap-3">
        <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
        <p className="text-sm font-bold text-slate-300">Running Clinical Intelligence &amp; Explainable AI Engine (Phase 6)…</p>
        <p className="text-xs text-slate-500">Evaluating deterministic disease rules, organ panel scores, and evidence links</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-rose-950/40 border border-rose-800 rounded-xl p-6 text-center space-y-3">
        <Activity className="w-8 h-8 text-rose-400 mx-auto" />
        <h4 className="text-sm font-bold text-rose-200">Analysis Engine Error</h4>
        <p className="text-xs text-rose-300">{error}</p>
        <button
          onClick={() => loadAnalysis(true)}
          className="px-4 py-2 bg-rose-900 hover:bg-rose-800 text-white text-xs font-semibold rounded-lg transition inline-flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Retry Analysis
        </button>
      </div>
    );
  }

  if (!analysis) return null;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Controls & Navigation Sub-Tabs */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-3 sm:p-4 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div className="flex items-center gap-1.5 flex-wrap">
          {[
            { id: 'overview', label: 'Executive Overview', icon: Activity },
            { id: 'organs', label: 'Organ Panels', icon: Heart },
            { id: 'evidence', label: 'Evidence Matrix', icon: Database },
            { id: 'recommendations', label: 'Recommendations', icon: Zap },
            { id: 'graph', label: 'Knowledge Graph', icon: Cpu },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                activeSubTab === tab.id
                  ? 'bg-sky-500 text-white shadow-md shadow-sky-500/20'
                  : 'bg-slate-50 text-slate-600 hover:bg-slate-100 hover:text-slate-900 border border-slate-100'
              }`}
            >
              <tab.icon className={`w-3.5 h-3.5 ${activeSubTab === tab.id ? 'text-white' : 'text-slate-400'}`} />
              {tab.label}
            </button>
          ))}
        </div>

        <button
          onClick={() => loadAnalysis(true)}
          disabled={reRunning}
          className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl border border-slate-200/80 transition disabled:opacity-50 flex-shrink-0"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-sky-500 ${reRunning ? 'animate-spin' : ''}`} />
          Re-run Intelligence Engine
        </button>
      </div>

      {/* Main Tab Content */}
      {activeSubTab === 'overview' && (
        <div className="space-y-6">
          <HealthScoreCard
            score={analysis.overall_health_score}
            risk={analysis.overall_risk}
            qualityStatus={analysis.quality_gate_status}
          />
          <ConflictAlertCard conflicts={analysis.conflicts} />
          <DiseaseInsightCard conditions={analysis.conditions} />
          <DoctorSummaryCard doctorSummary={analysis.doctor_summary} />
          <PatientSummaryCard patientSummary={analysis.patient_summary} />
          <ConfidenceCard confidenceBreakdown={analysis.confidence_breakdown} />
          <AnalysisVersionCard versioning={analysis.versioning} hash={analysis.determinism_hash} />
        </div>
      )}

      {activeSubTab === 'organs' && (
        <div className="space-y-6">
          <OrganHealthCard
            organPanels={analysis.organ_panels}
            organDependencies={analysis.organ_dependencies}
          />
          <MissingEvidenceCard
            missingEvidence={analysis.missing_evidence}
            coverageChecklist={analysis.coverage_checklist}
          />
          <TimelineViewer
            timelines={analysis.timelines}
            timelineDeltas={analysis.timeline_deltas}
          />
        </div>
      )}

      {activeSubTab === 'evidence' && (
        <div className="space-y-6">
          <EvidenceViewer evidence={analysis.evidence} />
          <MissingEvidenceCard
            missingEvidence={analysis.missing_evidence}
            coverageChecklist={analysis.coverage_checklist}
          />
        </div>
      )}

      {activeSubTab === 'recommendations' && (
        <div className="space-y-6">
          <RecommendationCard recommendations={analysis.recommendations} />
        </div>
      )}

      {activeSubTab === 'graph' && (
        <div className="space-y-6">
          <KnowledgeGraphViewer graph={analysis.graph} />
        </div>
      )}
    </div>
  );
}

