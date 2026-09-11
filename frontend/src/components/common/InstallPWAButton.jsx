import React, { useState } from 'react';
import { Download, Smartphone, Check, Share, X } from 'lucide-react';
import { usePWAInstall } from '../../hooks/usePWAInstall';

export default function InstallPWAButton({ variant = 'default' }) {
  const { isInstallable, isInstalled, installPWA } = usePWAInstall();
  const [showIOSModal, setShowIOSModal] = useState(false);
  const [installSuccess, setInstallSuccess] = useState(false);

  const handleInstallClick = async () => {
    // Check if iOS Safari
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;

    if (isIOS) {
      setShowIOSModal(true);
      return;
    }

    const success = await installPWA();
    if (success) {
      setInstallSuccess(true);
    } else if (!isInstallable) {
      setShowIOSModal(true);
    }
  };

  if (isInstalled || installSuccess) {
    return (
      <div className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl text-xs font-bold">
        <Check className="w-4 h-4 text-emerald-600" />
        App Installed
      </div>
    );
  }

  return (
    <>
      <button
        onClick={handleInstallClick}
        className={`flex items-center gap-2 font-bold transition-all shadow-sm active:scale-95 ${
          variant === 'sidebar'
            ? 'w-full px-4 py-2.5 bg-gradient-to-r from-sky-600 to-indigo-600 text-white rounded-xl text-xs justify-center hover:from-sky-700 hover:to-indigo-700'
            : 'px-3.5 py-1.5 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs border border-sky-500'
        }`}
      >
        <Download className="w-4 h-4 animate-bounce" />
        <span>Install Web App</span>
      </button>

      {/* iOS & Manual Installation Help Modal */}
      {showIOSModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-3xl p-6 max-w-sm w-full border border-slate-200 shadow-2xl relative space-y-4">
            <button
              onClick={() => setShowIOSModal(false)}
              className="absolute top-4 right-4 p-1.5 rounded-full text-slate-400 hover:bg-slate-100"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="w-12 h-12 bg-sky-100 text-sky-600 rounded-2xl flex items-center justify-center mx-auto">
              <Smartphone className="w-6 h-6" />
            </div>

            <div className="text-center space-y-1">
              <h3 className="text-base font-bold text-slate-900">Install Swasth-IQ Web App</h3>
              <p className="text-xs text-slate-500">
                Download this web app to your mobile home screen for fast, native access!
              </p>
            </div>

            <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-4 text-xs text-slate-700 space-y-2.5">
              <div className="flex items-start gap-2.5">
                <span className="w-5 h-5 bg-sky-600 text-white rounded-full text-[11px] font-bold flex items-center justify-center shrink-0">1</span>
                <p>Tap the <strong className="text-slate-900">Share</strong> button <Share className="w-3.5 h-3.5 inline text-sky-600 mx-0.5" /> in your browser menu.</p>
              </div>
              <div className="flex items-start gap-2.5">
                <span className="w-5 h-5 bg-sky-600 text-white rounded-full text-[11px] font-bold flex items-center justify-center shrink-0">2</span>
                <p>Scroll down and select <strong className="text-slate-900">"Add to Home Screen"</strong>.</p>
              </div>
              <div className="flex items-start gap-2.5">
                <span className="w-5 h-5 bg-sky-600 text-white rounded-full text-[11px] font-bold flex items-center justify-center shrink-0">3</span>
                <p>Tap <strong className="text-slate-900">"Add"</strong> in the top-right corner to finish!</p>
              </div>
            </div>

            <button
              onClick={() => setShowIOSModal(false)}
              className="w-full py-2.5 bg-slate-900 text-white font-bold rounded-xl text-xs hover:bg-slate-800 transition"
            >
              Got It
            </button>
          </div>
        </div>
      )}
    </>
  );
}
