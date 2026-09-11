import React, { useState } from 'react';
import { FileText, FileImage, File, Trash2, Eye, Cpu, MoreVertical, Sparkles, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ConfidenceBadge from '../ocr/ConfidenceBadge';
import FEATURES from '../../config/features';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

const formatBytes = (bytes) => {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

const formatDate = (dateStr) => {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
  });
};

const getMimeLabel = (mime) => {
  if (!mime) return 'File';
  if (mime === 'application/pdf') return 'PDF';
  if (mime.startsWith('image/')) return mime.split('/')[1].toUpperCase();
  if (mime === 'text/plain') return 'TXT';
  return 'File';
};

const FileTypeIcon = ({ mime, className = '' }) => {
  if (mime?.startsWith('image/')) return <FileImage className={className} />;
  if (mime === 'application/pdf') return <FileText className={className} />;
  return <File className={className} />;
};

const statusColors = {
  uploaded:   'bg-emerald-50 text-emerald-700 border-emerald-100',
  processing: 'bg-amber-50 text-amber-700 border-amber-100',
  completed:  'bg-sky-50 text-sky-700 border-sky-100',
  failed:     'bg-red-50 text-red-700 border-red-100',
};

const ReportCard = ({ report, onDelete }) => {
  const navigate = useNavigate();
  const [showPreview, setShowPreview] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const fileUrl = report.file_url ? `${API_BASE}${report.file_url}` : null;
  const isPDF = report.mime_type === 'application/pdf';
  const isImage = report.mime_type?.startsWith('image/');
  const statusStyle = statusColors[report.status] || statusColors.uploaded;

  const handleOpenDetail = () => {
    setMenuOpen(false);
    navigate(`/reports/${report.id}`);
  };

  return (
    <>
      <div className="card-hover p-5 group relative animate-fade-in">
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className="w-12 h-12 rounded-xl bg-sky-50 border border-sky-100 flex items-center justify-center flex-shrink-0">
            <FileTypeIcon mime={report.mime_type} className="w-6 h-6 text-sky-600" />
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <p className="text-sm font-semibold text-slate-900 truncate" title={report.original_filename}>
                {report.original_filename}
              </p>
              {FEATURES.OCR && report.ocr_status === 'completed' && (
                <ConfidenceBadge confidence={report.average_confidence || 1.0} showLabel={false} />
              )}
            </div>

            <div className="flex flex-wrap items-center gap-2 mt-1">
              <span className="text-xs text-slate-400">{getMimeLabel(report.mime_type)}</span>
              <span className="text-slate-300">·</span>
              <span className="text-xs text-slate-400">{formatBytes(report.file_size)}</span>
              <span className="text-slate-300">·</span>
              <span className="text-xs text-slate-400">{formatDate(report.uploaded_at)}</span>
            </div>

            <div className="flex flex-wrap items-center gap-2 mt-2">
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold border ${statusStyle}`}>
                {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
              </span>

              {FEATURES.OCR && (
                <button
                  onClick={handleOpenDetail}
                  className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 transition-colors"
                >
                  <ExternalLink className="w-3 h-3 text-indigo-600" />
                  Open Report
                </button>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="relative flex-shrink-0">
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 transition-all"
            >
              <MoreVertical className="w-4 h-4" />
            </button>

            {menuOpen && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
                <div className="absolute right-0 top-8 z-20 w-48 bg-white rounded-xl shadow-xl border border-slate-100 py-1.5 animate-fade-in text-xs">
                  <button
                    onClick={handleOpenDetail}
                    className="w-full flex items-center gap-2.5 px-4 py-2 text-indigo-700 hover:bg-indigo-50 font-medium"
                  >
                    <Sparkles className="w-4 h-4 text-indigo-500" />
                    Open Report Pipeline
                  </button>

                  {fileUrl && (
                    <button
                      onClick={() => { setShowPreview(true); setMenuOpen(false); }}
                      className="w-full flex items-center gap-2.5 px-4 py-2 text-slate-700 hover:bg-slate-50"
                    >
                      <Eye className="w-4 h-4 text-slate-400" />
                      View Original File
                    </button>
                  )}

                  <div className="border-t border-slate-100 my-1" />
                  <button
                    onClick={() => { onDelete(report.id); setMenuOpen(false); }}
                    className="w-full flex items-center gap-2.5 px-4 py-2 text-red-600 hover:bg-red-50 font-medium"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete Report
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Basic File Preview Modal */}
      {showPreview && fileUrl && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/60 backdrop-blur-sm"
          onClick={() => setShowPreview(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl overflow-hidden animate-slide-up"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
              <p className="text-sm font-semibold text-slate-900 truncate">{report.original_filename}</p>
              <button
                onClick={() => setShowPreview(false)}
                className="p-2 rounded-xl text-slate-400 hover:bg-slate-100"
              >
                ✕
              </button>
            </div>
            <div className="bg-slate-950 max-h-[70vh] flex items-center justify-center">
              {isImage && <img src={fileUrl} alt={report.original_filename} className="max-w-full max-h-[70vh] object-contain" />}
              {isPDF && <iframe src={fileUrl} title={report.original_filename} className="w-full h-[70vh]" style={{ border: 'none' }} />}
              {!isImage && !isPDF && (
                <p className="text-slate-400 text-sm p-8">Preview not available for this file type.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ReportCard;

