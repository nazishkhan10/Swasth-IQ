import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { User, Mail, Calendar, Shield, FileText, HardDrive, ArrowLeft, Loader2 } from 'lucide-react';
import { getFileStats } from '../services/filesApi';

const formatBytes = (bytes) => {
  if (!bytes) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

const ProfilePage = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(true);

  useEffect(() => {
    getFileStats()
      .then(setStats)
      .catch(() => setStats({ total_reports: 0, total_size_bytes: 0 }))
      .finally(() => setLoadingStats(false));
  }, []);

  const joinDate = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('en-IN', {
        year: 'numeric', month: 'long', day: 'numeric',
      })
    : '—';

  return (
    <div className="max-w-2xl mx-auto animate-fade-in">
      <div className="flex items-center gap-3 mb-8">
        <Link to="/dashboard" className="p-2 rounded-xl hover:bg-slate-100 transition-all text-slate-500">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Profile</h1>
          <p className="text-sm text-slate-500">Your account and usage information</p>
        </div>
      </div>

      {/* Main Card */}
      <div className="card shadow-sm overflow-hidden mb-5">
        <div className="h-24 bg-gradient-to-r from-sky-600 to-teal-500" />
        <div className="px-6 pb-6">
          <div className="-mt-12 mb-5 flex items-end gap-4">
            <div className="w-20 h-20 rounded-2xl bg-sky-600 border-4 border-white shadow-lg flex items-center justify-center text-white text-3xl font-extrabold">
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="pb-1">
              <p className="text-xl font-bold text-slate-900">{user?.name}</p>
              <p className="text-sm text-slate-500">{user?.email}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              { icon: User, label: 'Full Name', value: user?.name || '—' },
              { icon: Mail, label: 'Email Address', value: user?.email || '—' },
              { icon: Calendar, label: 'Member Since', value: joinDate },
              { icon: Shield, label: 'Account Status', value: 'Active & Verified' },
            ].map((item) => (
              <div key={item.label} className="bg-slate-50 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-1.5">
                  <item.icon className="w-4 h-4 text-slate-400" />
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{item.label}</p>
                </div>
                <p className="text-sm font-semibold text-slate-900 break-all">{item.value}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Storage Stats Card */}
      <div className="card shadow-sm p-5 mb-5">
        <h3 className="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2">
          <HardDrive className="w-4 h-4 text-sky-500" />
          Storage & Usage
        </h3>

        {loadingStats ? (
          <div className="flex items-center gap-2 text-slate-400 text-sm py-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            Loading stats...
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-sky-50 rounded-xl p-4 border border-sky-100">
              <div className="flex items-center gap-2 mb-1">
                <FileText className="w-4 h-4 text-sky-500" />
                <p className="text-xs font-semibold text-sky-700 uppercase tracking-wider">Reports</p>
              </div>
              <p className="text-2xl font-extrabold text-sky-700">{stats?.total_reports ?? 0}</p>
              <p className="text-xs text-sky-500/70 mt-0.5">files uploaded</p>
            </div>
            <div className="bg-teal-50 rounded-xl p-4 border border-teal-100">
              <div className="flex items-center gap-2 mb-1">
                <HardDrive className="w-4 h-4 text-teal-500" />
                <p className="text-xs font-semibold text-teal-700 uppercase tracking-wider">Storage</p>
              </div>
              <p className="text-2xl font-extrabold text-teal-700">
                {formatBytes(stats?.total_size_bytes)}
              </p>
              <p className="text-xs text-teal-500/70 mt-0.5">of 20 MB limit</p>
            </div>
          </div>
        )}
      </div>

      {/* Coming Soon */}
      <div className="p-4 bg-sky-50 border border-sky-100 rounded-xl text-sm text-sky-700">
        <p className="font-semibold mb-0.5">Profile editing coming in Phase 2.1</p>
        <p className="text-sky-600/80 text-xs">Update name, password, and notification preferences.</p>
      </div>
    </div>
  );
};

export default ProfilePage;
