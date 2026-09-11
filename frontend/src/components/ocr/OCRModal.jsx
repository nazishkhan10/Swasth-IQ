import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { Cpu, X, Sparkles, FileSearch } from 'lucide-react';
import OCRViewer from './OCRViewer';
import MedicalDataViewer from '../parser/MedicalDataViewer';
import FEATURES from '../../config/features';

export const OCRModal = ({ isOpen, onClose, report, ocrData, onRetry, isProcessing }) => {
  const [activeTab, setActiveTab] = useState('medical'); // 'medical' | 'ocr'

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen || !ocrData) return null;

  const modalContent = (
    <div className="fixed inset-0 z-[9999] bg-slate-950/95 backdrop-blur-md flex flex-col w-screen h-screen overflow-hidden animate-fade-in">
      {/* Top Fixed Header with Tabs */}
      <div className="sticky top-0 z-50 bg-slate-900 border-b border-slate-800 px-6 py-3.5 flex items-center justify-between shadow-xl">
        <div className="flex items-center gap-4 min-w-0">
          <div className="p-2 bg-blue-500/10 border border-blue-500/30 rounded-xl text-blue-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <h3 className="text-base font-bold text-slate-100 truncate">
              Document Intelligence & Medical Analysis
            </h3>
            <p className="text-xs text-slate-400 truncate">
              {report?.original_filename || 'Medical Report'}
            </p>
          </div>

          {/* Mode Tabs */}
          {FEATURES.PARSER && (
            <div className="hidden sm:flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 ml-4">
              <button
                onClick={() => setActiveTab('medical')}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'medical'
                    ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" />
                Medical Data Viewer
              </button>
              <button
                onClick={() => setActiveTab('ocr')}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'ocr'
                    ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <FileSearch className="w-3.5 h-3.5" />
                OCR Raw Text & Blocks
              </button>
            </div>
          )}
        </div>

        <button
          onClick={onClose}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors shadow-sm"
        >
          <X className="w-4 h-4" />
          Close Viewer
        </button>
      </div>

      {/* Mobile Tab switcher */}
      {FEATURES.PARSER && (
        <div className="flex sm:hidden items-center justify-around bg-slate-900 border-b border-slate-800 p-2">
          <button
            onClick={() => setActiveTab('medical')}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold ${
              activeTab === 'medical' ? 'bg-sky-500 text-white' : 'text-slate-400'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Medical Data
          </button>
          <button
            onClick={() => setActiveTab('ocr')}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold ${
              activeTab === 'ocr' ? 'bg-sky-500 text-white' : 'text-slate-400'
            }`}
          >
            <FileSearch className="w-3.5 h-3.5" />
            OCR Raw
          </button>
        </div>
      )}

      {/* Modal Scrollable Body */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
        <div className="max-w-7xl mx-auto w-full">
          {activeTab === 'medical' && FEATURES.PARSER ? (
            <MedicalDataViewer reportId={report?.id} reportName={report?.original_filename} />
          ) : (
            <OCRViewer
              report={report}
              ocrData={ocrData}
              onRetry={onRetry}
              isProcessing={isProcessing}
            />
          )}
        </div>
      </div>
    </div>
  );

  return ReactDOM.createPortal(modalContent, document.body);
};

export default OCRModal;
