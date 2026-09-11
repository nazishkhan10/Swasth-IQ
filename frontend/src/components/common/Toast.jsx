import React from 'react';
import { useToast } from '../../hooks/useToast';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

const icons = {
  success: <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />,
  error: <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />,
  warning: <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0" />,
  info: <Info className="w-5 h-5 text-sky-500 flex-shrink-0" />,
};

const styles = {
  success: 'bg-emerald-50 border-emerald-200 text-emerald-900',
  error: 'bg-red-50 border-red-200 text-red-900',
  warning: 'bg-amber-50 border-amber-200 text-amber-900',
  info: 'bg-sky-50 border-sky-200 text-sky-900',
};

export const ToastContainer = () => {
  const { toasts, removeToast } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-3 max-w-sm w-full pointer-events-none px-4 sm:px-0">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto flex items-start p-4 rounded-xl border shadow-lg transition-all transform duration-300 animate-slide-up ${
            styles[toast.type] || styles.info
          }`}
        >
          <div className="mr-3 pt-0.5">{icons[toast.type] || icons.info}</div>
          <div className="flex-1 text-sm font-medium leading-snug">{toast.message}</div>
          <button
            onClick={() => removeToast(toast.id)}
            className="ml-3 text-slate-400 hover:text-slate-600 transition-colors p-0.5 rounded-lg hover:bg-black/5"
            aria-label="Close notification"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ))}
    </div>
  );
};

export default ToastContainer;
