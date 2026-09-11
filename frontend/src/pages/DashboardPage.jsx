import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { FEATURES } from '../config/features';
import ProgressWidget from '../components/dashboard/ProgressWidget';
import {
  FileUp, Image, ScanText, FileText, Activity,
  HardDrive, Calendar, Upload, ArrowRight, Loader2,
  Lock, Trash2
} from 'lucide-react';
import { getFiles, getFileStats, deleteFile } from '../services/filesApi';
import { useToast } from '../hooks/useToast';
import ConfirmDialog from '../components/common/ConfirmDialog';

const formatBytes = (bytes) => {
  if (!bytes) return '0 B';
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

const formatRelative = (dateStr) => {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  const now = new Date();
  const diff = Math.floor((now - d) / 1000);
  if (diff < 60) return 'Just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
};

const getMimeLabel = (mime) => {
  if (!mime) return 'FILE';
  if (mime === 'application/pdf') return 'PDF';
  if (mime.startsWith('image/')) return mime.split('/')[1].toUpperCase();
  if (mime === 'text/plain') return 'TXT';
  return 'FILE';
};

const quickActions = [
  { icon: FileUp, title: 'Upload PDF', description: 'Lab report or diagnostic document', color: 'sky', enabled: FEATURES.UPLOAD },
  { icon: Image, title: 'Upload Image', description: 'JPG or PNG scan of your report', color: 'teal', enabled: FEATURES.UPLOAD },
  { icon: ScanText, title: 'Scan Report', description: 'Use your camera to capture', color: 'violet', enabled: FEATURES.CAMERA },
  { icon: FileText, title: 'Upload TXT', description: 'Plain text report data', color: 'amber', enabled: FEATURES.UPLOAD },
];

const colorMap = {
  sky: 'bg-sky-50 text-sky-600 border-sky-100 group-hover:bg-sky-100',
  teal: 'bg-teal-50 text-teal-600 border-teal-100 group-hover:bg-teal-100',
  violet: 'bg-violet-50 text-violet-600 border-violet-100 group-hover:bg-violet-100',
  amber: 'bg-amber-50 text-amber-600 border-amber-100 group-hover:bg-amber-100',
};

const DashboardPage = () => {
  const { user } = useAuth();
  const { showSuccess, showError } = useToast();
  const firstName = user?.name?.split(' ')[0] || 'there';

  const [reports, setReports] = useState([]);
  const [stats, setStats] = useState(null);
  const [loadingReports, setLoadingReports] = useState(true);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoadingReports(true);
      try {
        const [r, s] = await Promise.all([getFiles({ limit: 5 }), getFileStats()]);
        setReports(r);
        setStats(s);
      } catch {
        // silently fail — non-critical
      } finally {
        setLoadingReports(false);
      }
    };
    fetchData();
  }, []);

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await deleteFile(deleteTarget);
      setReports((prev) => prev.filter((r) => r.id !== deleteTarget));
      setStats((s) => s ? { ...s, total_reports: Math.max(0, s.total_reports - 1) } : s);
      showSuccess('Report deleted.');
    } catch {
      showError('Could not delete report.');
    } finally {
      setDeleting(false);
      setDeleteTarget(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto animate-fade-in">
      {/* ── Welcome ───────────────────────────────────────── */}
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">
          Welcome back, {firstName} 👋
        </h1>
        <p className="text-slate-500 mt-1 text-sm">
          Here's an overview of your medical reports and account activity.
        </p>
      </div>

      {/* ── Stats Row + Progress Widget ───────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            {
              icon: FileText,
              label: 'Total Reports',
              value: loadingReports ? '—' : String(stats?.total_reports ?? 0),
              sub: 'uploaded files',
              color: 'bg-sky-50 text-sky-600',
            },
            {
              icon: HardDrive,
              label: 'Storage Used',
              value: loadingReports ? '—' : formatBytes(stats?.total_size_bytes),
              sub: 'of 20 MB quota',
              color: 'bg-teal-50 text-teal-600',
            },
            {
              icon: Calendar,
              label: 'Last Upload',
              value: loadingReports ? '—' : (stats?.last_uploaded_at ? formatRelative(stats.last_uploaded_at) : 'Never'),
              sub: 'most recent activity',
              color: 'bg-emerald-50 text-emerald-600',
            },
          ].map((stat) => (
            <div key={stat.label} className="card p-5">
              <div className={`w-9 h-9 rounded-lg flex items-center justify-center mb-3 ${stat.color}`}>
                <stat.icon className="w-5 h-5" />
              </div>
              <p className="text-2xl font-bold text-slate-900">{stat.value}</p>
              <p className="text-xs font-semibold text-slate-700 mt-0.5">{stat.label}</p>
              <p className="text-xs text-slate-400 mt-0.5">{stat.sub}</p>
            </div>
          ))}
        </div>

        <div className="lg:col-span-1">
          <ProgressWidget />
        </div>
      </div>

      {/* ── Quick Actions ──────────────────────────────────── */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900">Quick Actions</h2>
          <Link to="/upload" className="text-xs font-semibold text-sky-600 hover:text-sky-700 flex items-center gap-1">
            Go to Upload
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action) => (
            action.enabled ? (
              <Link
                key={action.title}
                to="/upload"
                className="flex flex-col bg-white border border-slate-100 hover:border-sky-200 hover:shadow-md rounded-2xl p-5 group transition-all"
              >
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center border mb-4 transition-all ${colorMap[action.color] || colorMap.sky}`}>
                  <action.icon className="w-6 h-6" />
                </div>
                <h4 className="text-sm font-semibold text-slate-800 mb-1">{action.title}</h4>
                <p className="text-xs text-slate-500 leading-relaxed">{action.description}</p>
                <div className="mt-3 text-xs font-semibold text-sky-600 flex items-center gap-1">
                  Open Upload <ArrowRight className="w-3 h-3" />
                </div>
              </Link>
            ) : (
              <div key={action.title} className="relative flex flex-col bg-white border border-slate-100 rounded-2xl p-5 opacity-60 cursor-not-allowed">
                <div className="absolute top-3 right-3 flex items-center gap-1 bg-slate-100 text-slate-400 text-[10px] font-semibold px-2 py-0.5 rounded-full">
                  <Lock className="w-2.5 h-2.5" />
                  Phase 3
                </div>
                <div className="w-12 h-12 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center mb-4">
                  <action.icon className="w-6 h-6 text-slate-400" />
                </div>
                <h4 className="text-sm font-semibold text-slate-700 mb-1">{action.title}</h4>
                <p className="text-xs text-slate-400 leading-relaxed">{action.description}</p>
              </div>
            )
          ))}
        </div>
      </div>

      {/* ── Recent Reports ─────────────────────────────────── */}
      <div className="card">
        <div className="flex items-center justify-between p-5 sm:p-6 border-b border-slate-100">
          <h2 className="text-lg font-semibold text-slate-900">Recent Reports</h2>
          <Link to="/my-reports" className="text-xs font-semibold text-sky-600 hover:text-sky-700 flex items-center gap-1">
            View All
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loadingReports && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 text-sky-500 animate-spin" />
          </div>
        )}

        {!loadingReports && reports.length === 0 && (
          <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
            <div className="w-14 h-14 bg-slate-50 rounded-full flex items-center justify-center border-2 border-dashed border-slate-200 mb-4">
              <FileText className="w-6 h-6 text-slate-300" />
            </div>
            <p className="text-sm font-medium text-slate-600 mb-1">No reports uploaded yet</p>
            <p className="text-xs text-slate-400 mb-5">Upload your first medical report to get started.</p>
            <Link to="/upload" className="btn-primary px-5 py-2.5 text-sm rounded-xl">
              <Upload className="w-4 h-4 mr-2" />
              Upload First Report
            </Link>
          </div>
        )}

        {!loadingReports && reports.length > 0 && (
          <div className="divide-y divide-slate-50">
            {reports.map((report) => (
              <div key={report.id} className="flex items-center gap-4 px-5 sm:px-6 py-4 hover:bg-slate-50/50 transition-all group">
                <div className="w-9 h-9 rounded-lg bg-sky-50 border border-sky-100 flex items-center justify-center flex-shrink-0">
                  <FileText className="w-4 h-4 text-sky-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-slate-900 truncate">{report.original_filename}</p>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {getMimeLabel(report.mime_type)} · {formatBytes(report.file_size)} · {formatRelative(report.uploaded_at)}
                  </p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-100">
                    Uploaded
                  </span>
                  <button
                    onClick={() => setDeleteTarget(report.id)}
                    className="p-1.5 rounded-lg text-slate-300 hover:text-red-500 hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-all"
                    title="Delete report"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Confirm Delete */}
      <ConfirmDialog
        isOpen={!!deleteTarget}
        title="Delete Report?"
        message="This will permanently remove the file from your account."
        confirmLabel="Delete"
        confirmVariant="danger"
        loading={deleting}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
};

export default DashboardPage;
