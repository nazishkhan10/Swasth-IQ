import React, { useCallback } from 'react';
import { Upload, FileUp, Image, FileText, Camera } from 'lucide-react';
import { FEATURES } from '../../config/features';

const ACCEPTED = '.pdf,.png,.jpg,.jpeg,.txt';

const sourceCards = [
  { key: 'pdf',    icon: FileUp,   label: 'PDF',   desc: 'Lab report, discharge summary', accept: '.pdf', mime: 'application/pdf' },
  { key: 'image',  icon: Image,    label: 'Image',  desc: 'JPG, PNG scan or photo',        accept: '.png,.jpg,.jpeg', mime: 'image/*' },
  { key: 'txt',    icon: FileText, label: 'Text',   desc: 'Plain text report data',        accept: '.txt', mime: 'text/plain' },
  { key: 'camera', icon: Camera,   label: 'Camera', desc: 'Capture via device camera',     accept: null,   mime: null },
];

const DropZone = ({ onFileSelected, onCameraOpen }) => {
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) onFileSelected(file);
  }, [onFileSelected]);

  const handleDragOver = (e) => e.preventDefault();

  const handleBrowse = (accept) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = accept || ACCEPTED;
    input.onchange = (e) => {
      const file = e.target.files?.[0];
      if (file) onFileSelected(file);
    };
    input.click();
  };

  return (
    <div className="space-y-5">
      {/* Main Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="relative group border-2 border-dashed border-slate-200 hover:border-sky-400 rounded-2xl p-10 text-center transition-all cursor-pointer bg-white hover:bg-sky-50/30"
        onClick={() => handleBrowse(ACCEPTED)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && handleBrowse(ACCEPTED)}
        aria-label="Click or drag a file to upload"
      >
        <div className="w-16 h-16 bg-sky-50 group-hover:bg-sky-100 rounded-2xl flex items-center justify-center mx-auto mb-4 transition-all border border-sky-100">
          <Upload className="w-8 h-8 text-sky-500" />
        </div>
        <h3 className="text-lg font-semibold text-slate-800 mb-1">Drop your file here</h3>
        <p className="text-sm text-slate-500 mb-4">or click to browse your device</p>
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white text-sm font-semibold rounded-xl transition-all shadow-md shadow-sky-600/20">
          <FileUp className="w-4 h-4" />
          Browse Files
        </div>
        <p className="mt-4 text-xs text-slate-400">PDF, JPG, PNG, TXT — up to 20 MB</p>
      </div>

      {/* Source Quick-Select Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {sourceCards.map((src) => (
          <button
            key={src.key}
            onClick={() => {
              if (src.key === 'camera') {
                onCameraOpen?.();
              } else {
                handleBrowse(src.accept);
              }
            }}
            className="flex flex-col items-center gap-2 p-4 bg-white border border-slate-100 hover:border-sky-200 hover:bg-sky-50/40 rounded-2xl transition-all group text-left"
          >
            <div className="w-10 h-10 rounded-xl bg-slate-50 group-hover:bg-sky-100 flex items-center justify-center border border-slate-100 transition-all">
              <src.icon className="w-5 h-5 text-slate-500 group-hover:text-sky-600 transition-colors" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-800">{src.label}</p>
              <p className="text-[11px] text-slate-400 mt-0.5 leading-tight">{src.desc}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default DropZone;
