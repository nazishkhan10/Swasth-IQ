import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Upload, FileText, Loader2, AlertCircle } from 'lucide-react';
import { useToast } from '../hooks/useToast';
import ReportCard from '../components/reports/ReportCard';
import ConfirmDialog from '../components/common/ConfirmDialog';
import { getFiles, deleteFile } from '../services/filesApi';

const MyReportsPage = () => {
  const { showSuccess, showError } = useToast();

  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const fetchReports = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getFiles();
      setReports(data);
    } catch {
      setError('Failed to load reports. Please refresh.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  const handleDeleteRequest = (id) => setDeleteTarget(id);

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await deleteFile(deleteTarget);
      setReports((prev) => prev.filter((r) => r.id !== deleteTarget));
      showSuccess('Report deleted successfully.');
    } catch {
      showError('Failed to delete report. Please try again.');
    } finally {
      setDeleting(false);
      setDeleteTarget(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <Link to="/dashboard" className="p-2 rounded-xl hover:bg-slate-100 transition-all text-slate-500">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-900">My Reports</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {loading ? 'Loading...' : `${reports.length} report${reports.length !== 1 ? 's' : ''} uploaded`}
          </p>
        </div>
        <Link
          to="/upload"
          className="btn-primary px-4 py-2.5 text-sm rounded-xl hidden sm:flex"
        >
          <Upload className="w-4 h-4 mr-2" />
          Upload New
        </Link>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-sky-500 animate-spin mb-3" />
          <p className="text-sm text-slate-500">Loading your reports...</p>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="card p-8 text-center">
          <AlertCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
          <p className="text-sm text-slate-600 mb-4">{error}</p>
          <button onClick={fetchReports} className="btn-primary px-5 py-2.5 text-sm rounded-xl">
            Retry
          </button>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && reports.length === 0 && (
        <div className="card p-12 text-center shadow-sm">
          <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-5 border-2 border-dashed border-slate-200">
            <FileText className="w-9 h-9 text-slate-300" />
          </div>
          <h2 className="text-xl font-semibold text-slate-800 mb-2">No reports yet</h2>
          <p className="text-sm text-slate-500 max-w-xs mx-auto mb-6">
            Upload your first medical report to get started. Supports PDF, images, and text files.
          </p>
          <Link to="/upload" className="btn-primary px-6 py-3 rounded-xl text-sm">
            <Upload className="w-4 h-4 mr-2" />
            Upload First Report
          </Link>
        </div>
      )}

      {/* Reports List */}
      {!loading && !error && reports.length > 0 && (
        <>
          {/* Mobile Upload Button */}
          <div className="mb-4 sm:hidden">
            <Link to="/upload" className="btn-primary w-full py-3 text-sm rounded-xl">
              <Upload className="w-4 h-4 mr-2" />
              Upload New Report
            </Link>
          </div>

          <div className="space-y-3">
            {reports.map((report) => (
              <ReportCard
                key={report.id}
                report={report}
                onDelete={handleDeleteRequest}
              />
            ))}
          </div>

          <p className="mt-6 text-center text-xs text-slate-400">
            Phase 3 OCR & Document Intelligence active. Click "Run OCR Pipeline" on any report to extract structure, blocks, and tables.
          </p>
        </>
      )}

      {/* Confirm Delete Dialog */}
      <ConfirmDialog
        isOpen={!!deleteTarget}
        title="Delete Report?"
        message="This will permanently remove the file from your account. This action cannot be undone."
        confirmLabel="Delete Report"
        confirmVariant="danger"
        loading={deleting}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
};

export default MyReportsPage;
