import React, { useEffect, useState } from 'react';
import { FileText, FileImage, File, RefreshCw, X, Upload } from 'lucide-react';

const formatBytes = (bytes) => {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

const FileTypeIcon = ({ mimeType }) => {
  if (!mimeType) return <File className="w-6 h-6" />;
  if (mimeType.startsWith('image/')) return <FileImage className="w-6 h-6" />;
  if (mimeType === 'application/pdf') return <FileText className="w-6 h-6" />;
  return <FileText className="w-6 h-6" />;
};

const FilePreview = ({ file, onReplace, onRemove, onUpload, uploading }) => {
  const [objectUrl, setObjectUrl] = useState(null);
  const [txtContent, setTxtContent] = useState(null);

  const isImage = file.type?.startsWith('image/');
  const isPDF = file.type === 'application/pdf';
  const isTxt = file.type === 'text/plain' || file.name?.endsWith('.txt');

  useEffect(() => {
    if (isImage || isPDF) {
      const url = URL.createObjectURL(file);
      setObjectUrl(url);
      return () => URL.revokeObjectURL(url);
    }
    if (isTxt) {
      const reader = new FileReader();
      reader.onload = (e) => setTxtContent(e.target.result);
      reader.readAsText(file);
    }
  }, [file]);

  return (
    <div className="bg-white border border-slate-100 rounded-2xl overflow-hidden shadow-sm animate-slide-up">
      {/* Header */}
      <div className="flex items-center gap-3 px-5 py-4 border-b border-slate-100 bg-slate-50/50">
        <div className="w-10 h-10 rounded-xl bg-sky-50 border border-sky-100 flex items-center justify-center text-sky-600">
          <FileTypeIcon mimeType={file.type} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-slate-900 truncate">{file.name}</p>
          <p className="text-xs text-slate-500 mt-0.5">{formatBytes(file.size)} · {file.type || 'Unknown type'}</p>
        </div>
        <button
          onClick={onRemove}
          disabled={uploading}
          className="p-2 rounded-xl text-slate-400 hover:bg-red-50 hover:text-red-500 transition-all disabled:opacity-40"
          title="Remove file"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Preview Area */}
      <div className="p-4">
        {isImage && objectUrl && (
          <div className="rounded-xl overflow-hidden bg-slate-50 border border-slate-100 flex items-center justify-center max-h-72">
            <img
              src={objectUrl}
              alt={file.name}
              className="max-h-72 max-w-full object-contain"
            />
          </div>
        )}

        {isPDF && objectUrl && (
          <div className="rounded-xl overflow-hidden border border-slate-100 bg-slate-50">
            <iframe
              src={objectUrl}
              title={file.name}
              className="w-full h-64 block"
              style={{ border: 'none' }}
            />
          </div>
        )}

        {isTxt && txtContent !== null && (
          <div className="rounded-xl bg-slate-950 border border-slate-800 p-4 max-h-56 overflow-y-auto">
            <pre className="text-xs text-slate-300 font-mono whitespace-pre-wrap break-words leading-relaxed">
              {txtContent.slice(0, 3000)}
              {txtContent.length > 3000 && '\n\n... (preview truncated)'}
            </pre>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-3 px-5 py-4 border-t border-slate-100 bg-slate-50/30">
        <button
          onClick={onReplace}
          disabled={uploading}
          className="flex items-center gap-2 px-4 py-2.5 border border-slate-200 hover:border-slate-300 bg-white text-slate-700 text-sm font-semibold rounded-xl transition-all disabled:opacity-50"
        >
          <RefreshCw className="w-4 h-4" />
          Replace
        </button>

        <button
          onClick={onUpload}
          disabled={uploading}
          className="flex-1 btn-primary py-2.5 text-sm rounded-xl"
        >
          {uploading ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Uploading...
            </span>
          ) : (
            <>
              <Upload className="w-4 h-4 mr-2" />
              Upload Report
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default FilePreview;
