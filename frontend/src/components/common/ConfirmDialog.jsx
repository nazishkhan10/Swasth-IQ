import React from 'react';
import { X, CheckCircle2, AlertCircle } from 'lucide-react';

/**
 * ConfirmDialog — modal confirmation overlay.
 * Props: isOpen, title, message, confirmLabel, confirmVariant ('danger'|'primary'), onConfirm, onCancel, loading
 */
const ConfirmDialog = ({
  isOpen,
  title = 'Are you sure?',
  message = '',
  confirmLabel = 'Confirm',
  confirmVariant = 'danger',
  onConfirm,
  onCancel,
  loading = false,
}) => {
  if (!isOpen) return null;

  const confirmColors =
    confirmVariant === 'danger'
      ? 'bg-red-600 hover:bg-red-700 text-white shadow-red-600/20'
      : 'bg-sky-600 hover:bg-sky-700 text-white shadow-sky-600/20';

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center px-4"
      role="dialog"
      aria-modal="true"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm animate-fade-in"
        onClick={!loading ? onCancel : undefined}
      />

      {/* Panel */}
      <div className="relative bg-white rounded-2xl shadow-2xl p-6 w-full max-w-sm animate-slide-up">
        <button
          onClick={onCancel}
          disabled={loading}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 transition-all disabled:opacity-50"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-start gap-4">
          <div
            className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
              confirmVariant === 'danger' ? 'bg-red-50' : 'bg-sky-50'
            }`}
          >
            <AlertCircle
              className={`w-5 h-5 ${confirmVariant === 'danger' ? 'text-red-500' : 'text-sky-500'}`}
            />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-900 mb-1">{title}</h3>
            {message && <p className="text-sm text-slate-500 leading-relaxed">{message}</p>}
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={onCancel}
            disabled={loading}
            className="flex-1 btn-secondary py-2.5 text-sm rounded-xl"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className={`flex-1 inline-flex items-center justify-center py-2.5 text-sm font-semibold rounded-xl shadow-md transition-all active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed ${confirmColors}`}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Deleting...
              </span>
            ) : (
              confirmLabel
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDialog;
