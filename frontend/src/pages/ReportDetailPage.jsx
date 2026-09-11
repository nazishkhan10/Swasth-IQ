import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Cpu, Sparkles, ShieldCheck, Download,
  Loader2, AlertCircle, RefreshCw, FileText,
  ScanText, Activity, ChevronRight, Bot
} from 'lucide-react';
import { ocrApi } from '../services/ocrApi';
import { parserApi } from '../services/parserApi';
import { validationApi } from '../services/validationApi';
import { getFiles } from '../services/filesApi';
import { useToast } from '../hooks/useToast';
import { ROUTES } from '../config/constants';

import OCRViewer from '../components/ocr/OCRViewer';
import MedicalDataViewer from '../components/parser/MedicalDataViewer';
import { ValidationSummaryCard } from '../components/validation/ValidationSummaryCard';
import ValidationStatusTable from '../components/validation/ValidationStatusTable';
import { CriticalValuesCard } from '../components/validation/CriticalValuesCard';
import ParameterDetailDrawer from '../components/validation/ParameterDetailDrawer';
import MedicalAIWorkspace from '../components/chat/MedicalAIWorkspace/MedicalAIWorkspace';


const TABS = [
  { id: 'ocr',        label: 'OCR & Text Extraction', icon: ScanText,    phase: 'Phase 3' },
  { id: 'validation', label: 'Medical Data & Validation', icon: ShieldCheck, phase: 'Phase 4 & 5' },
  { id: 'chat',       label: 'Medical AI Assistant',  icon: Bot,         phase: 'Phase 7' },
];

/* ─────────────────────────────────────────────────────────────── */
/*  Main Page                                                      */
/* ─────────────────────────────────────────────────────────────── */
const ReportDetailPage = () => {
  const { id: reportId } = useParams();
  const navigate = useNavigate();
  const { showSuccess, showError } = useToast();

  const [activeTab, setActiveTab] = useState('ocr');
  const [report, setReport] = useState(null);
  const [loadingReport, setLoadingReport] = useState(true);

  // OCR state
  const [ocrData, setOcrData] = useState(null);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrError, setOcrError] = useState(null);

  // Unified Validation state
  const [validationData, setValidationData] = useState(null);
  const [validationSummary, setValidationSummary] = useState(null);
  const [criticalValues, setCriticalValues] = useState([]);
  const [qualityScore, setQualityScore] = useState(null);
  const [validationLoading, setValidationLoading] = useState(false);
  const [validationError, setValidationError] = useState(null);
  const [selectedParam, setSelectedParam] = useState(null);

  /* ── Fetch report metadata ──────────────────────────────────── */
  useEffect(() => {
    const load = async () => {
      try {
        const files = await getFiles();
        const found = files.find((f) => String(f.id) === String(reportId));
        if (!found) {
          navigate(ROUTES.MY_REPORTS);
          return;
        }
        setReport(found);
      } catch {
        showError('Could not load report.');
        navigate(ROUTES.MY_REPORTS);
      } finally {
        setLoadingReport(false);
      }
    };
    load();
  }, [reportId]);

  /* ── OCR Pipeline ───────────────────────────────────────────── */
  const runOCR = useCallback(async (forceRetry = false) => {
    setOcrLoading(true);
    setOcrError(null);
    try {
      const data = await ocrApi.startOcr(Number(reportId), forceRetry);
      setOcrData(data);
      showSuccess('OCR pipeline complete.');
    } catch (err) {
      setOcrError(err?.response?.data?.detail || 'OCR failed. Please retry.');
      showError('OCR pipeline failed.');
    } finally {
      setOcrLoading(false);
    }
  }, [reportId]);

  // Auto-run OCR when switching to OCR tab
  useEffect(() => {
    if (activeTab === 'ocr' && !ocrData && !ocrLoading) {
      runOCR(false);
    }
  }, [activeTab]);

  /* ── Unified Validation & Data Extraction ────────────────────── */
  const runValidation = useCallback(async (retry = false) => {
    setValidationLoading(true);
    setValidationError(null);
    try {
      const fn = retry ? validationApi.retryValidation : validationApi.getValidationResults;
      const [vData, vSummary, vCritical, vQuality] = await Promise.all([
        fn(Number(reportId)),
        validationApi.getValidationSummary(Number(reportId)),
        validationApi.getCriticalValues(Number(reportId)),
        validationApi.getQualityScore(Number(reportId)).catch(() => null),
      ]);
      setValidationData(vData);
      setValidationSummary(vSummary);
      setCriticalValues(vCritical);
      setQualityScore(vQuality?.score ?? null);
      if (retry) showSuccess('Validation & Data Extraction complete.');
    } catch (err) {
      setValidationError(err?.response?.data?.detail || 'Validation failed. Please retry.');
      showError('Validation engine error.');
    } fontinally: {
      setValidationLoading(false);
    }
  }, [reportId]);

  // Auto-load validation when tab becomes active
  useEffect(() => {
    if (activeTab === 'validation' && !validationData && !validationLoading) {
      runValidation(false);
    }
  }, [activeTab]);

  /* ── CSV / JSON Export ──────────────────────────────────────── */
  const handleExport = async (format) => {
    try {
      if (format === 'csv') {
        const blob = await validationApi.exportValidatedDataset(Number(reportId), 'csv');
        const url = URL.createObjectURL(new Blob([blob], { type: 'text/csv' }));
        const a = document.createElement('a');
        a.href = url;
        a.download = `validated_report_${reportId}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        showSuccess('CSV exported.');
      } else {
        const data = await validationApi.exportValidatedDataset(Number(reportId), 'json');
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `validated_report_${reportId}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showSuccess('JSON exported.');
      }
    } catch {
      showError('Export failed. Please try again.');
    }
  };

  /* ── Guards ─────────────────────────────────────────────────── */
  if (loadingReport) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 text-sky-500 animate-spin" />
      </div>
    );
  }

  const validatedValues = validationData?.validated_values || [];

  /* ── Render ─────────────────────────────────────────────────── */
  return (
    <div className="max-w-7xl mx-auto animate-fade-in">
      {/* ── Breadcrumb / Header ──────────────────────────────── */}
      <div className="flex items-center gap-3 mb-6">
        <Link
          to={ROUTES.MY_REPORTS}
          className="p-2 rounded-xl hover:bg-slate-100 transition-all text-slate-500"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 text-xs text-slate-400 mb-0.5">
            <Link to={ROUTES.MY_REPORTS} className="hover:text-sky-600 transition">My Reports</Link>
            <ChevronRight className="w-3 h-3" />
            <span className="text-slate-600 truncate">{report?.original_filename || `Report #${reportId}`}</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 truncate">
            {report?.original_filename || `Report #${reportId}`}
          </h1>
        </div>
      </div>

      {/* ── Pipeline Stage Tabs ──────────────────────────────── */}
      <div className="bg-white border border-slate-100 rounded-2xl shadow-sm mb-6 overflow-hidden">
        <div className="flex items-center gap-0 border-b border-slate-100 overflow-x-auto">
          {TABS.map((tab, idx) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <React.Fragment key={tab.id}>
                <button
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2.5 px-5 py-4 text-sm font-semibold whitespace-nowrap transition-all border-b-2 ${
                    isActive
                      ? 'border-sky-500 text-sky-600 bg-sky-50/50'
                      : 'border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-sky-500' : 'text-slate-400'}`} />
                  <span>{tab.label}</span>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                    isActive ? 'bg-sky-100 text-sky-600' : 'bg-slate-100 text-slate-400'
                  }`}>
                    {tab.phase}
                  </span>
                </button>
                {idx < TABS.length - 1 && (
                  <ChevronRight className="w-3.5 h-3.5 text-slate-300 flex-shrink-0" />
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* ── Tab Body ─────────────────────────────────────── */}
        <div className="p-5 sm:p-6">

          {/* ═══ OCR TAB ══════════════════════════════════════ */}
          {activeTab === 'ocr' && (
            <div>
              {ocrLoading && (
                <div className="flex flex-col items-center justify-center py-20 gap-3">
                  <Loader2 className="w-8 h-8 text-sky-500 animate-spin" />
                  <p className="text-sm text-slate-500">Running OCR pipeline…</p>
                </div>
              )}
              {ocrError && !ocrLoading && (
                <div className="flex flex-col items-center justify-center py-16 gap-4">
                  <AlertCircle className="w-10 h-10 text-red-400" />
                  <p className="text-sm text-slate-600">{ocrError}</p>
                  <button
                    onClick={() => runOCR(true)}
                    className="btn-primary px-5 py-2.5 text-sm rounded-xl flex items-center gap-2"
                  >
                    <RefreshCw className="w-4 h-4" /> Retry OCR
                  </button>
                </div>
              )}
              {!ocrLoading && !ocrError && ocrData && (
                <OCRViewer
                  report={report}
                  ocrData={ocrData}
                  onRetry={(engine) => runOCR(true)}
                  isProcessing={ocrLoading}
                />
              )}
            </div>
          )}

          {/* ═══ UNIFIED MEDICAL DATA EXTRACTION & CLINICAL VALIDATION TAB (PHASE 4 & 5) ═════ */}
          {activeTab === 'validation' && (
            <div>
              {/* Medical Data Patient Metadata Viewer */}
              <MedicalDataViewer
                reportId={Number(reportId)}
                reportName={report?.original_filename}
              />

              {/* Validation Section Header & Toolbar */}
              <div className="mt-8 pt-6 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3 mb-5">
                <div>
                  <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
                    <Activity className="w-4 h-4 text-indigo-500" />
                    Phase 5 — Medical Validation Engine
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Rule-based clinical status classification &amp; reference range validation
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => runValidation(true)}
                    disabled={validationLoading}
                    className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-all disabled:opacity-50"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${validationLoading ? 'animate-spin' : ''}`} />
                    Re-run Validation
                  </button>
                  <button
                    onClick={() => handleExport('csv')}
                    className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all shadow-sm"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Export CSV
                  </button>
                  <button
                    onClick={() => handleExport('json')}
                    className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold transition-all"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Export JSON
                  </button>
                </div>
              </div>

              {/* Loading */}
              {validationLoading && (
                <div className="flex flex-col items-center justify-center py-16 gap-3">
                  <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
                  <p className="text-sm text-slate-500">Running Clinical Validation Engine…</p>
                </div>
              )}

              {/* Error */}
              {validationError && !validationLoading && (
                <div className="flex flex-col items-center justify-center py-14 gap-4">
                  <AlertCircle className="w-10 h-10 text-red-400" />
                  <p className="text-sm text-slate-600">{validationError}</p>
                  <button
                    onClick={() => runValidation(true)}
                    className="btn-primary px-5 py-2.5 text-sm rounded-xl flex items-center gap-2"
                  >
                    <RefreshCw className="w-4 h-4" /> Retry Validation
                  </button>
                </div>
              )}

              {/* Results */}
              {!validationLoading && !validationError && validationData && (
                <div>
                  {/* Critical alerts banner (if any) */}
                  {criticalValues.length > 0 && (
                    <CriticalValuesCard items={criticalValues} />
                  )}

                  {/* Summary metrics */}
                  <ValidationSummaryCard
                    summary={validationSummary}
                    qualityScore={qualityScore}
                    onExport={handleExport}
                  />

                  {/* Parameter table */}
                  <ValidationStatusTable
                    validatedValues={validatedValues}
                    onSelectParameter={setSelectedParam}
                  />

                  {/* Empty state */}
                  {validatedValues.length === 0 && (
                    <div className="text-center py-12 text-slate-500 text-sm">
                      <FileText className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                      No validated parameters found. Run the Medical Parser first, then re-run validation.
                    </div>
                  )}
                </div>
              )}

              {/* Not yet loaded */}
              {!validationLoading && !validationError && !validationData && (
                <div className="flex flex-col items-center justify-center py-16 gap-4">
                  <ShieldCheck className="w-10 h-10 text-indigo-300" />
                  <p className="text-sm text-slate-500">
                    Clinical Validation not yet run. Click below to start.
                  </p>
                  <button
                    onClick={() => runValidation(false)}
                    className="btn-primary px-6 py-2.5 text-sm rounded-xl flex items-center gap-2"
                  >
                    <Activity className="w-4 h-4" /> Run Clinical Validation
                  </button>
                </div>
              )}
            </div>
          )}

          {/* ═══ MEDICAL AI CLINICAL WORKSTATION TAB (PHASE 7 FREEZE V8.2) ════════════ */}
          {activeTab === 'chat' && (
            <MedicalAIWorkspace reportId={reportId} report={report} analysisData={validationSummary} />
          )}

        </div>
      </div>

      {/* ── Parameter Detail Drawer ──────────────────────────── */}
      {selectedParam && (
        <ParameterDetailDrawer
          parameter={selectedParam}
          onClose={() => setSelectedParam(null)}
        />
      )}
    </div>
  );
};

export default ReportDetailPage;
