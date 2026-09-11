import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, FileText, Upload, User, Download } from 'lucide-react';
import { ROUTES } from '../../config/constants';
import InstallPWAButton from '../common/InstallPWAButton';

export default function MobileBottomBar() {
  const location = useLocation();

  const items = [
    { label: 'Home', href: ROUTES.DASHBOARD, icon: LayoutDashboard },
    { label: 'Reports', href: ROUTES.MY_REPORTS, icon: FileText },
    { label: 'Upload', href: ROUTES.UPLOAD, icon: Upload },
    { label: 'Profile', href: ROUTES.PROFILE, icon: User },
  ];

  return (
    <div className="fixed bottom-0 inset-x-0 z-40 bg-white/95 backdrop-blur-lg border-t border-slate-200 lg:hidden px-2 py-1.5 shadow-lg">
      <div className="flex items-center justify-around">
        {items.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.href}
              to={item.href}
              className={`flex flex-col items-center gap-1 py-1 px-3 rounded-2xl transition-all ${
                isActive ? 'text-sky-600 font-bold' : 'text-slate-500 hover:text-slate-800 font-medium'
              }`}
            >
              <item.icon className={`w-5 h-5 transition-transform ${isActive ? 'scale-110' : ''}`} />
              <span className="text-[10px]">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
