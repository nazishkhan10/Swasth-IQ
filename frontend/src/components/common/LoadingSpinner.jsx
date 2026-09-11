import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ size = 'medium', fullPage = false, message = 'Loading...' }) => {
  const sizeClasses = {
    small: 'w-5 h-5',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  };

  const content = (
    <div className="flex flex-col items-center justify-center space-y-3">
      <Loader2 className={`${sizeClasses[size] || sizeClasses.medium} text-sky-600 animate-spin`} />
      {message && <p className="text-sm font-medium text-slate-500">{message}</p>}
    </div>
  );

  if (fullPage) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        {content}
      </div>
    );
  }

  return content;
};

export default LoadingSpinner;
