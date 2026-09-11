import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Camera, RefreshCw, X, Check, Video } from 'lucide-react';

/**
 * CameraCapture — uses browser getUserMedia to capture photos.
 * Calls onCapture(File) with the captured image as a File object.
 */
const CameraCapture = ({ onCapture, onClose }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const [error, setError] = useState(null);
  const [captured, setCaptured] = useState(null); // blob URL of preview
  const [capturedBlob, setCapturedBlob] = useState(null);
  const [loading, setLoading] = useState(true);

  const startCamera = useCallback(async () => {
    setError(null);
    setLoading(true);
    setCaptured(null);
    setCapturedBlob(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setLoading(false);
      }
    } catch (err) {
      setError(
        err.name === 'NotAllowedError'
          ? 'Camera permission was denied. Please allow camera access and try again.'
          : err.name === 'NotFoundError'
          ? 'No camera device found on this device.'
          : `Camera error: ${err.message}`
      );
      setLoading(false);
    }
  }, []);

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  }, []);

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, [startCamera, stopCamera]);

  const handleCapture = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    canvas.toBlob((blob) => {
      if (!blob) return;
      const url = URL.createObjectURL(blob);
      setCaptured(url);
      setCapturedBlob(blob);
      stopCamera();
    }, 'image/jpeg', 0.92);
  };

  const handleRetake = () => {
    if (captured) URL.revokeObjectURL(captured);
    setCaptured(null);
    setCapturedBlob(null);
    startCamera();
  };

  const handleAccept = () => {
    if (!capturedBlob) return;
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const file = new File([capturedBlob], `camera_capture_${timestamp}.jpg`, { type: 'image/jpeg' });
    stopCamera();
    onCapture(file);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <Camera className="w-5 h-5 text-sky-600" />
            <h3 className="text-base font-semibold text-slate-900">Camera Capture</h3>
          </div>
          <button
            onClick={() => { stopCamera(); onClose(); }}
            className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Camera View */}
        <div className="relative bg-slate-950 aspect-video flex items-center justify-center">
          {error ? (
            <div className="text-center px-6 py-8">
              <Video className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-sm text-slate-400 max-w-xs leading-relaxed">{error}</p>
              <button
                onClick={startCamera}
                className="mt-4 btn-primary px-4 py-2 text-sm rounded-xl"
              >
                Retry
              </button>
            </div>
          ) : captured ? (
            <img src={captured} alt="Capture preview" className="w-full h-full object-contain" />
          ) : (
            <>
              {loading && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="w-8 h-8 border-2 border-sky-500/30 border-t-sky-500 rounded-full animate-spin" />
                </div>
              )}
              <video
                ref={videoRef}
                playsInline
                muted
                className="w-full h-full object-cover"
                style={{ opacity: loading ? 0 : 1, transition: 'opacity 0.3s' }}
              />
            </>
          )}
          <canvas ref={canvasRef} className="hidden" />
        </div>

        {/* Controls */}
        <div className="flex items-center justify-center gap-4 px-5 py-5">
          {!captured ? (
            <button
              onClick={handleCapture}
              disabled={loading || !!error}
              className="w-16 h-16 rounded-full bg-white border-4 border-sky-500 hover:border-sky-600 flex items-center justify-center shadow-lg transition-all active:scale-95 disabled:opacity-40"
              title="Capture photo"
            >
              <div className="w-10 h-10 rounded-full bg-sky-500 hover:bg-sky-600 transition-colors" />
            </button>
          ) : (
            <>
              <button
                onClick={handleRetake}
                className="flex items-center gap-2 px-5 py-2.5 border border-slate-200 text-slate-700 text-sm font-semibold rounded-xl hover:bg-slate-50 transition-all"
              >
                <RefreshCw className="w-4 h-4" />
                Retake
              </button>
              <button
                onClick={handleAccept}
                className="flex items-center gap-2 px-6 py-2.5 bg-teal-600 hover:bg-teal-700 text-white text-sm font-semibold rounded-xl transition-all shadow-md"
              >
                <Check className="w-4 h-4" />
                Use Photo
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default CameraCapture;
