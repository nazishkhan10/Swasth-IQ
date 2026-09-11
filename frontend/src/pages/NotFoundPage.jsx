import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Activity, Home, LayoutDashboard, ArrowLeft } from 'lucide-react';

const NotFoundPage = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="max-w-lg w-full text-center animate-slide-up">
        {/* Large 404 */}
        <div className="relative mb-8">
          <p className="text-[140px] sm:text-[180px] font-extrabold text-slate-100 leading-none select-none">
            404
          </p>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-20 h-20 bg-gradient-to-tr from-sky-600 to-teal-500 rounded-3xl flex items-center justify-center shadow-xl shadow-sky-600/25">
              <Activity className="w-10 h-10 text-white" />
            </div>
          </div>
        </div>

        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-3">Page Not Found</h1>
        <p className="text-slate-500 text-sm leading-relaxed mb-8 max-w-sm mx-auto">
          The page you're looking for doesn't exist or has been moved. 
          Let's get you back on track.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={() => navigate(-1)}
            className="btn-secondary px-6 py-3 rounded-xl"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Go Back
          </button>

          <Link to="/" className="btn-secondary px-6 py-3 rounded-xl">
            <Home className="w-4 h-4 mr-2" />
            Home
          </Link>

          {isAuthenticated && (
            <Link to="/dashboard" className="btn-primary px-6 py-3 rounded-xl">
              <LayoutDashboard className="w-4 h-4 mr-2" />
              Dashboard
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
