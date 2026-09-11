import React, { useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle2 } from 'lucide-react';
import { useToast } from '../hooks/useToast';

import DropZone from '../components/upload/DropZone';
import FilePreview from '../components/upload/FilePreview';
import UploadProgress from '../components/upload/UploadProgress';
import CameraCapture from '../components/upload/CameraCapture';
import { uploadFile } from '../services/uploadApi';

const ALLOWED_EXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg', '.txt'];
const MAX_SIZE_BYTES = 20 * 1024 * 1024;

const UploadPage = () => {
  const { showSuccess, showError, showWarning } = useToast();
  const navigate = useNavigate();

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadSource, setUploadSource] = useState('upload');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [uploadedReport, setUploadedReport] = useState(null);
  const [cameraOpen, setCameraOpen] = useState(false);
  const [error, setError] = useState(null);

  // ── Validation ──────────────────────────────────────────────────────────
  const validateFile = (file) => {
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return `File type "${ext}" is not supported. Please upload PDF, PNG, JPG, or TXT.`;
    }
    if (file.size > MAX_SIZE_BYTES) {
      return `File is too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Maximum size is 20 MB.`;
    }
    if (file.size === 0) {
      return 'The selected file is empty. Please choose a valid file.';
    }
    return null;
  };

  // ── File Selection ───────────────────────────────────────────────────────
  const handleFileSelected = useCallback((file, source = 'upload') => {
    const err = validateFile(file);
    if (err) {
      showError(err);
      setError(err);
      return;
    }
    setError(null);
    setSelectedFile(file);
    setUploadSource(source);
    setUploadedReport(null);
    setProgress(0);
  }, [showError]);

  const handleCameraCapture = useCallback((file) => {
    setCameraOpen(false);
    handleFileSelected(file, 'camera');
  }, [handleFileSelected]);

  const handleReplace = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf,.png,.jpg,.jpeg,.txt';
    input.onchange = (e) => {
      const file = e.target.files?.[0];
      if (file) handleFileSelected(file, 'upload');
    };
    input.click();
  }, [handleFileSelected]);

  const handleRemove = useCallback(() => {
    setSelectedFile(null);
    setError(null);
    setProgress(0);
    setUploadedReport(null);
  }, []);

  // ── Upload ───────────────────────────────────────────────────────────────
  const handleUpload = useCallback(async () => {
    if (!selectedFile || uploading) return;

    setUploading(true);
    setProgress(0);
    setError(null);

    try {
      const report = await uploadFile(selectedFile, uploadSource, (pct) => setProgress(pct));
      setUploadedReport(report);
      setSelectedFile(null);
      showSuccess(`"${report.original_filename}" uploaded successfully!`);
    } catch (err) {
      const detail =
        err?.response?.data?.detail || 'Upload failed. Please try again.';
      setError(detail);
      showError(detail);
      setProgress(0);
    } finally {
      setUploading(false);
    }
  }, [selectedFile, uploadSource, uploading, showSuccess, showError]);

  // ── Success Screen ───────────────────────────────────────────────────────
  if (uploadedReport) {
    return (
      <div className="max-w-xl mx-auto animate-fade-in">
        <div className="card p-10 text-center shadow-sm">
          <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-5 border-2 border-emerald-200">
            <CheckCircle2 className="w-10 h-10 text-emerald-500" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Upload Successful!</h2>
          <p className="text-slate-500 text-sm mb-1">
            <span className="font-semibold text-slate-700">{uploadedReport.original_filename}</span>
          </p>
          <p className="text-slate-400 text-xs mb-8">
            {uploadedReport.mime_type} · {((uploadedReport.file_size || 0) / 1024).toFixed(1)} KB
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={() => { setUploadedReport(null); setProgress(0); }}
              className="btn-secondary px-6 py-3 rounded-xl text-sm"
            >
              Upload Another
            </button>
            <Link to="/my-reports" className="btn-primary px-6 py-3 rounded-xl text-sm">
              View My Reports
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto animate-fade-in">
      {/* Page Header */}
      <div className="flex items-center gap-3 mb-8">
        <Link to="/dashboard" className="p-2 rounded-xl hover:bg-slate-100 transition-all text-slate-500">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Upload Report</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Upload your medical report for AI analysis in Phase 3
          </p>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mb-5 px-4 py-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl flex items-center gap-2">
          <span className="flex-shrink-0">⚠</span>
          {error}
        </div>
      )}

      {/* Upload Progress */}
      {uploading && (
        <div className="mb-5">
          <UploadProgress progress={progress} />
        </div>
      )}

      {/* File Preview or Drop Zone */}
      {selectedFile && !uploading ? (
        <FilePreview
          file={selectedFile}
          onReplace={handleReplace}
          onRemove={handleRemove}
          onUpload={handleUpload}
          uploading={uploading}
        />
      ) : !uploading ? (
        <DropZone
          onFileSelected={handleFileSelected}
          onCameraOpen={() => setCameraOpen(true)}
        />
      ) : null}

      {/* Camera Modal */}
      {cameraOpen && (
        <CameraCapture
          onCapture={handleCameraCapture}
          onClose={() => setCameraOpen(false)}
        />
      )}

      {/* Info Footer */}
      <div className="mt-6 p-4 bg-slate-50 border border-slate-100 rounded-xl">
        <p className="text-xs text-slate-500 text-center">
          🔒 Files are stored securely on your account. OCR & AI analysis available in Phase 3.
        </p>
      </div>
    </div>
  );
};

export default UploadPage;
