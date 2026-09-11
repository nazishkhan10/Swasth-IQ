import React, { useState } from 'react';
import { Search, Copy, Download, RefreshCw, ChevronUp, ChevronDown, Check, FileText, Code, FileCode } from 'lucide-react';

export const OCRToolbar = ({
  searchTerm = '',
  onSearchChange,
  matchCount = 0,
  currentMatchIndex = 0,
  onNextMatch,
  onPrevMatch,
  onCopyText,
  onExport,
  onRetry,
  isProcessing = false
}) => {
  const [copied, setCopied] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [showRetryModal, setShowRetryModal] = useState(false);
  const [selectedEngine, setSelectedEngine] = useState('PyMuPDF');

  const handleCopy = () => {
    onCopyText();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportClick = (format) => {
    onExport(format);
    setShowExportMenu(false);
  };

  const handleConfirmRetry = () => {
    onRetry(selectedEngine);
    setShowRetryModal(false);
  };

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 bg-white border border-slate-200 rounded-2xl p-3 shadow-2xs">
      {/* Search Input & Navigation */}
      <div className="flex items-center gap-2 flex-1 min-w-[240px]">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search OCR text, headers, tables..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-20 py-2 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors font-medium"
          />

          {searchTerm && (
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[11px] font-mono text-slate-500 font-bold">
              {matchCount > 0 ? `${currentMatchIndex + 1}/${matchCount}` : 'No matches'}
            </span>
          )}
        </div>

        {matchCount > 0 && (
          <div className="flex items-center gap-1">
            <button
              onClick={onPrevMatch}
              className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600"
              title="Previous Match"
            >
              <ChevronUp className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onNextMatch}
              className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600"
              title="Next Match"
            >
              <ChevronDown className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>

      {/* Action Buttons: Copy, Export, Retry */}
      <div className="flex items-center gap-2">
        {/* Copy Button */}
        <button
          onClick={handleCopy}
          className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl border border-slate-200 transition-colors cursor-pointer"
          title="Copy Extracted Text"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-indigo-600" />}
          {copied ? 'Copied!' : 'Copy Text'}
        </button>

        {/* Export Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowExportMenu(!showExportMenu)}
            className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl border border-slate-200 transition-colors cursor-pointer"
          >
            <Download className="w-3.5 h-3.5 text-emerald-600" />
            Export
            <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
          </button>

          {showExportMenu && (
            <div className="absolute right-0 mt-2 w-44 bg-white border border-slate-200 rounded-xl shadow-xl z-30 py-1 text-xs font-medium">
              <button
                onClick={() => handleExportClick('txt')}
                className="w-full px-3 py-2 text-left text-slate-700 hover:bg-slate-50 flex items-center gap-2"
              >
                <FileText className="w-4 h-4 text-indigo-500" />
                Plain Text (.txt)
              </button>
              <button
                onClick={() => handleExportClick('json')}
                className="w-full px-3 py-2 text-left text-slate-700 hover:bg-slate-50 flex items-center gap-2"
              >
                <Code className="w-4 h-4 text-amber-500" />
                Unified JSON (.json)
              </button>
              <button
                onClick={() => handleExportClick('md')}
                className="w-full px-3 py-2 text-left text-slate-700 hover:bg-slate-50 flex items-center gap-2"
              >
                <FileCode className="w-4 h-4 text-emerald-500" />
                LLM Markdown (.md)
              </button>
            </div>
          )}
        </div>

        {/* Retry OCR Button */}
        <button
          onClick={() => setShowRetryModal(true)}
          disabled={isProcessing}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl shadow-xs transition-colors disabled:opacity-50 cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isProcessing ? 'animate-spin' : ''}`} />
          Retry OCR
        </button>
      </div>

      {/* Retry Modal */}
      {showRetryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 max-w-sm w-full shadow-2xl space-y-4 text-left">
            <h4 className="text-sm font-bold text-slate-900">Reprocess Report OCR</h4>
            <p className="text-xs text-slate-500">Select extraction engine for reprocessing:</p>

            <select
              value={selectedEngine}
              onChange={(e) => setSelectedEngine(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs font-bold rounded-xl p-2.5 focus:outline-none focus:border-indigo-500"
            >
              <option value="PyMuPDF">PyMuPDF Engine (Digital PDF)</option>
              <option value="SarvamDoc">Sarvam Document Intelligence (Scanned PDF)</option>
              <option value="SarvamVision">Sarvam Vision OCR (Image)</option>
              <option value="Tesseract">Tesseract Local OCR (Fallback)</option>
              <option value="PlainText">PlainText Reader (.txt)</option>
            </select>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setShowRetryModal(false)}
                className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmRetry}
                className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl shadow-xs"
              >
                Start Retry
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OCRToolbar;
