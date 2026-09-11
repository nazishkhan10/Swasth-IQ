/**
 * MedicalDataViewer — Phase 4 + Phase 5 Integrated View
 *
 * Pipeline:
 *   Phase 4: Extract medical parameters  (parserApi)
 *   Phase 5: Validate against reference  (validationApi)
 *
 * The viewer auto-runs validation immediately after extraction.
 * "Pending Validation" badges are gone — every row shows a live status.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { parserApi }     from '../../services/parserApi';
import { validationApi } from '../../services/validationApi';

import PatientInformationCard                from './PatientInformationCard';
import { ValidationSummaryCard }             from '../validation/ValidationSummaryCard';
import ValidationStatusTable                 from '../validation/ValidationStatusTable';
import { CriticalValuesCard }                from '../validation/CriticalValuesCard';
import { ValidationWarningsCard }            from '../validation/ValidationWarningsCard';
import ParameterDetailDrawer                 from '../validation/ParameterDetailDrawer';

import {
  Download, RefreshCw, ShieldCheck, CheckCircle2,
  AlertCircle, Activity, Loader2, Upload, Cpu, Sparkles,
} from 'lucide-react';

/* ─── Loading-step sequence shown during pipeline execution ──────────────── */
const PIPELINE_STEPS = [
  'Running Medical Extraction Engine (Phase 4)…',
  'Checking Clinical Reference Ranges…',
  'Evaluating Critical Safety Thresholds…',
  'Applying Age & Gender Demographic Rules…',
  'Building Validated Dataset (Phase 5)…',
];

/* ─── Pipeline breadcrumb – shows ✓ for completed phases ─────────────────── */
const PipelineBreadcrumb = ({ validationDone, onReRun, reRunning }) => (
  <div className="bg-white border border-slate-200/80 rounded-2xl px-4 py-3 flex flex-wrap justify-between items-center gap-3 shadow-sm">
    <div className="flex items-center gap-1.5 text-xs font-semibold flex-wrap">
      {[
        { label: '📤 Upload',     done: true },
        { label: '🔍 OCR',       done: true },
        { label: '📑 Extraction', done: true },
        { label: '🩺 Validation', done: validationDone },
        { label: '🧠 Intelligence', done: true },
      ].map(({ label, done, future }, i) => (
        <React.Fragment key={i}>
          {i > 0 && <span className="text-slate-300">›</span>}
          <span className={`flex items-center gap-1 px-3 py-1 rounded-full border text-[11px] font-bold transition-all ${
            done
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
              : 'bg-amber-50 text-amber-700 border-amber-200 animate-pulse'
          }`}>
            {done ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> : <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            {label}
          </span>
        </React.Fragment>
      ))}
    </div>

    <button
      onClick={onReRun}
      disabled={reRunning}
      className="flex items-center gap-1.5 px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl border border-slate-200 transition disabled:opacity-50 active:scale-95"
    >
      <RefreshCw className={`w-3.5 h-3.5 text-sky-600 ${reRunning ? 'animate-spin' : ''}`} />
      Re-run Validation
    </button>
  </div>
);


/* ─── Main Component ─────────────────────────────────────────────────────── */
const MedicalDataViewer = ({ reportId, reportName = 'Medical Report' }) => {
  const [parsedData,      setParsedData]      = useState(null);
  const [validatedData,   setValidatedData]   = useState(null);
  const [summary,         setSummary]         = useState(null);
  const [criticalValues,  setCriticalValues]  = useState([]);
  const [warnings,        setWarnings]        = useState([]);
  const [qualityScore,    setQualityScore]    = useState(null);

  const [loading,         setLoading]         = useState(true);
  const [reRunning,       setReRunning]       = useState(false);
  const [stepIdx,         setStepIdx]         = useState(0);
  const [error,           setError]           = useState(null);

  const [search,            setSearch]            = useState('');
  const [selectedCategory,  setSelectedCategory]  = useState('All');
  const [selectedParam,     setSelectedParam]      = useState(null);

  /* ── Animated step cycling during load ────────────────────────────────── */
  useEffect(() => {
    if (!loading && !reRunning) return;
    const t = setInterval(() => setStepIdx(i => (i + 1) % PIPELINE_STEPS.length), 1200);
    return () => clearInterval(t);
  }, [loading, reRunning]);

  /* ── Full pipeline load ───────────────────────────────────────────────── */
  const loadPipelineData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      /* Phase 4 — fetch or run parser */
      let pResult = await parserApi.getParsedData(reportId);
      if (!pResult.parameters || pResult.parameters.length === 0) {
        pResult = await parserApi.runParser(reportId);
      }
      setParsedData(pResult);

      /* Phase 5 — fetch or run validation */
      let vResult = await validationApi.getValidationResults(reportId);
      if (!vResult.validated_values || vResult.validated_values.length === 0) {
        vResult = await validationApi.validateReport(reportId);
      }
      setValidatedData(vResult);

      const [sumRes, critRes, warnRes, qualRes] = await Promise.all([
        validationApi.getValidationSummary(reportId),
        validationApi.getCriticalValues(reportId),
        parserApi.getWarnings(reportId),
        validationApi.getQualityScore(reportId).catch(() => null),
      ]);

      setSummary(sumRes);
      setCriticalValues(critRes || []);
      setWarnings(warnRes?.warnings || []);
      setQualityScore(qualRes?.score ?? null);
    } catch (err) {
      console.error('Pipeline error:', err);
      setError(err?.response?.data?.detail || 'Medical Validation Pipeline failed. Please retry.');
    } finally {
      setLoading(false);
    }
  }, [reportId]);

  useEffect(() => {
    if (reportId) loadPipelineData();
  }, [reportId]);

  /* ── Re-run validation only ───────────────────────────────────────────── */
  const handleReRunValidation = async () => {
    setReRunning(true);
    setError(null);
    try {
      const vResult = await validationApi.retryValidation(reportId);
      setValidatedData(vResult);

      const [sumRes, critRes, warnRes, qualRes] = await Promise.all([
        validationApi.getValidationSummary(reportId),
        validationApi.getCriticalValues(reportId),
        parserApi.getWarnings(reportId),
        validationApi.getQualityScore(reportId).catch(() => null),
      ]);
      setSummary(sumRes);
      setCriticalValues(critRes || []);
      setWarnings(warnRes?.warnings || []);
      setQualityScore(qualRes?.score ?? null);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Re-run validation failed.');
    } finally {
      setReRunning(false);
    }
  };

  /* ── Export ───────────────────────────────────────────────────────────── */
  const handleExport = async (format) => {
    const baseName = reportName.replace(/\.[^/.]+$/, '');
    if (format === 'json') {
      const payload = {
        resourceType: 'DiagnosticReport',
        status: 'final',
        report_id: reportId,
        detected_report_type: parsedData?.detected_report_type,
        patient: parsedData?.patient,
        summary,
        validated_parameters: validatedData?.validated_values || [],
        critical_alerts: criticalValues,
        warnings,
      };
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      const url  = URL.createObjectURL(blob);
      const a    = Object.assign(document.createElement('a'), { href: url, download: `${baseName}_validated_clinical_dataset.json` });
      a.click(); URL.revokeObjectURL(url);
    } else if (format === 'csv') {
      try {
        const blobData = await validationApi.exportValidatedDataset(reportId, 'csv');
        const url  = URL.createObjectURL(new Blob([blobData]));
        const link = Object.assign(document.createElement('a'), { href: url, download: `${baseName}_validated_clinical_dataset.csv` });
        document.body.appendChild(link); link.click(); link.remove();
      } catch (err) {
        console.error('CSV export failed:', err);
      }
    }
  };

  /* ── Filtered parameter list ──────────────────────────────────────────── */
  const validatedList = validatedData?.validated_values || [];
  const filteredList  = validatedList.filter(p => {
    const catOk    = selectedCategory === 'All' || p.category?.toLowerCase() === selectedCategory.toLowerCase();
    const haystack = `${p.parameter_name} ${p.parameter_code||''} ${p.raw_value} ${p.normalized_unit||''} ${p.status}`.toLowerCase();
    return catOk && (!search || haystack.includes(search.toLowerCase()));
  });
  const categories = ['All', ...new Set(validatedList.map(p => p.category).filter(Boolean))];

  /* ── LOADING SCREEN ───────────────────────────────────────────────────── */
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-slate-400 gap-4">
        <div className="relative">
          <div className="w-16 h-16 rounded-full bg-indigo-950 border-2 border-indigo-700 flex items-center justify-center">
            <Activity className="w-7 h-7 text-indigo-400 animate-pulse" />
          </div>
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center">
            <Loader2 className="w-3 h-3 text-white animate-spin" />
          </span>
        </div>
        <div className="text-center">
          <p className="text-sm font-bold text-slate-200 mb-1">{PIPELINE_STEPS[stepIdx]}</p>
          <p className="text-xs text-slate-500">Applying clinical reference ranges, age/gender rules & critical safety checks</p>
        </div>
        {/* Mini pipeline progress */}
        <div className="flex items-center gap-1.5 text-[10px] font-semibold mt-2">
          {['Upload','OCR','Extract','Validate'].map((s, i) => (
            <React.Fragment key={s}>
              {i > 0 && <span className="text-slate-700">›</span>}
              <span className={`px-2 py-0.5 rounded ${i <= stepIdx % 4 ? 'bg-indigo-900 text-indigo-300' : 'bg-slate-800 text-slate-600'}`}>{s}</span>
            </React.Fragment>
          ))}
        </div>
      </div>
    );
  }

  /* ── ERROR SCREEN ─────────────────────────────────────────────────────── */
  if (error) {
    return (
      <div className="bg-rose-950/40 border border-rose-800 rounded-xl p-8 text-center">
        <AlertCircle className="w-10 h-10 text-rose-400 mx-auto mb-3" />
        <h3 className="text-md font-bold text-rose-200 mb-1">Validation Pipeline Error</h3>
        <p className="text-sm text-rose-300 mb-5">{error}</p>
        <button
          onClick={loadPipelineData}
          className="px-5 py-2.5 bg-rose-900 hover:bg-rose-800 text-rose-100 text-sm font-semibold rounded-xl transition flex items-center gap-2 mx-auto"
        >
          <RefreshCw className="w-4 h-4" /> Retry Pipeline
        </button>
      </div>
    );
  }

  const validationDone = !!validatedData && validatedList.length > 0;

  /* ── MAIN VIEW ────────────────────────────────────────────────────────── */
  return (
    <div className="space-y-5">
      {/* ── Pipeline Breadcrumb ─────────────────────────────────────────── */}
      <PipelineBreadcrumb
        validationDone={validationDone}
        onReRun={handleReRunValidation}
        reRunning={reRunning}
      />

      {/* ── Re-run spinner overlay ──────────────────────────────────────── */}
      {reRunning && (
        <div className="bg-indigo-950/40 border border-indigo-800/60 rounded-xl p-4 flex items-center gap-3 text-indigo-300 text-sm font-semibold">
          <Loader2 className="w-5 h-5 animate-spin text-indigo-400" />
          Re-evaluating clinical reference ranges & critical thresholds…
        </div>
      )}

      {/* ── Patient Metadata ────────────────────────────────────────────── */}
      {parsedData?.patient && (
        <PatientInformationCard
          patient={parsedData.patient}
          reportType={parsedData.detected_report_type}
        />
      )}

      {/* ── Phase 5 Validation Summary ──────────────────────────────────── */}
      {summary && (
        <ValidationSummaryCard summary={summary} qualityScore={qualityScore} onExport={handleExport} />
      )}

      {/* ── Critical Values Alert Banner ────────────────────────────────── */}
      {criticalValues.length > 0 && (
        <CriticalValuesCard items={criticalValues} />
      )}

      {/* ── No critical values — reassurance message ────────────────────── */}
      {validationDone && criticalValues.length === 0 && (
        <div className="flex items-center gap-3 bg-emerald-950/30 border border-emerald-800/40 rounded-xl px-4 py-3 text-emerald-300 text-xs font-semibold">
          <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          No critical laboratory values detected in this report.
        </div>
      )}

      {/* ── Validation Warnings ─────────────────────────────────────────── */}
      {warnings.length > 0 && (
        <ValidationWarningsCard warnings={warnings} />
      )}

      {/* ── Category Filter + Search Bar ────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 bg-slate-900 px-4 py-3 rounded-xl border border-slate-800">
        <div className="flex flex-wrap gap-1.5">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                selectedCategory === cat
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
        <input
          type="text"
          placeholder="Filter by parameter, value, status…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="px-3.5 py-1.5 bg-slate-950 border border-slate-800 text-white placeholder-slate-500 rounded-lg text-xs w-full sm:w-64 focus:outline-none focus:border-indigo-500 transition"
        />
      </div>

      {/* ── Validated Parameters Table ──────────────────────────────────── */}
      <ValidationStatusTable
        validatedValues={validatedList}
        searchTerm={search}
        selectedCategory={selectedCategory}
      />

      {/* ── Empty state (no validated parameters yet) ───────────────────── */}
      {!reRunning && validatedList.length === 0 && (
        <div className="text-center py-14 text-slate-500">
          <ShieldCheck className="w-10 h-10 text-slate-700 mx-auto mb-3" />
          <p className="text-sm font-medium text-slate-400 mb-1">No validated parameters found.</p>
          <p className="text-xs text-slate-600 mb-5">Run the Medical Parser first, then re-run validation.</p>
          <button
            onClick={handleReRunValidation}
            className="px-5 py-2.5 bg-indigo-700 hover:bg-indigo-600 text-white text-sm font-semibold rounded-xl transition flex items-center gap-2 mx-auto"
          >
            <Activity className="w-4 h-4" /> Run Validation
          </button>
        </div>
      )}

      {/* ── Parameter Detail Drawer ─────────────────────────────────────── */}
      <ParameterDetailDrawer
        parameter={selectedParam}
        onClose={() => setSelectedParam(null)}
      />
    </div>
  );
};

export default MedicalDataViewer;
