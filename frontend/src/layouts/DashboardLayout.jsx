import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../hooks/useToast';
import {
  Activity, LayoutDashboard, FileText, Upload,
  User, LogOut, Menu, X, ChevronDown
} from 'lucide-react';
import { ROUTES } from '../config/constants';
import InstallPWAButton from '../components/common/InstallPWAButton';
import MobileBottomBar from '../components/layout/MobileBottomBar';

const navItems = [
  { label: 'Dashboard', href: ROUTES.DASHBOARD, icon: LayoutDashboard },
  { label: 'My Reports', href: ROUTES.MY_REPORTS, icon: FileText },
  { label: 'Upload Report', href: ROUTES.UPLOAD, icon: Upload },
];

const DashboardLayout = () => {
  const { user, logout } = useAuth();
  const { showInfo } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    showInfo('You have been signed out.');
    navigate(ROUTES.LOGIN);
  };

  const isActive = (path) => location.pathname === path;

  const NavLink = ({ item }) => (
    <Link
      to={item.href}
      onClick={() => setSidebarOpen(false)}
      className={`flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-semibold transition-all active:scale-95 ${
        isActive(item.href)
          ? 'bg-sky-600 text-white shadow-md shadow-sky-600/20'
          : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
      }`}
    >
      <item.icon className="w-5 h-5 flex-shrink-0" />
      {item.label}
    </Link>
  );

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col lg:flex-row pb-16 lg:pb-0">
      {/* Sidebar — Desktop */}
      <aside className="hidden lg:flex flex-col w-64 bg-white border-r border-slate-200/80 fixed inset-y-0 left-0 z-30 shadow-2xs">
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-100">
          <div className="w-10 h-10 bg-gradient-to-tr from-sky-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-md">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-sm font-extrabold text-slate-900 leading-tight">Swasth-IQ</p>
            <p className="text-[10px] font-bold text-sky-600 uppercase tracking-wider">Medical Web App</p>
          </div>
        </div>

        {/* Nav items */}
        <nav className="flex-1 px-4 py-6 space-y-1.5">
          {navItems.map((item) => <NavLink key={item.href} item={item} />)}
        </nav>

        {/* PWA Download Banner in Sidebar */}
        <div className="px-4 py-3 border-t border-slate-100">
          <InstallPWAButton variant="sidebar" />
        </div>

        {/* Profile section at bottom */}
        <div className="border-t border-slate-100 p-4">
          <Link
            to={ROUTES.PROFILE}
            className="flex items-center gap-3 px-3 py-2.5 rounded-2xl hover:bg-slate-50 transition-all group"
          >
            <div className="w-9 h-9 rounded-xl bg-sky-600 text-white flex items-center justify-center font-bold text-sm shrink-0">
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-slate-900 truncate">{user?.name}</p>
              <p className="text-xs text-slate-500 truncate">{user?.email}</p>
            </div>
          </Link>
          <button
            onClick={handleLogout}
            className="w-full mt-1 flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-bold text-rose-600 hover:bg-rose-50 transition-all"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Mobile Sidebar Drawer */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-72 bg-white border-r border-slate-200/80 transform transition-transform duration-300 lg:hidden shadow-2xl ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-tr from-sky-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-md">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <p className="text-sm font-extrabold text-slate-900">Swasth-IQ</p>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 rounded-xl text-slate-400 hover:bg-slate-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <nav className="px-4 py-5 space-y-1.5">
          {navItems.map((item) => <NavLink key={item.href} item={item} />)}
        </nav>
        <div className="px-4 py-3 border-t border-slate-100">
          <InstallPWAButton variant="sidebar" />
        </div>
        <div className="border-t border-slate-100 p-4">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-bold text-rose-600 hover:bg-rose-50 transition-all"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 lg:pl-64 flex flex-col min-h-screen">
        {/* Top Bar */}
        <header className="sticky top-0 z-30 bg-white/90 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Mobile hamburger & title */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-xl text-slate-600 hover:bg-slate-100 transition-all active:scale-95"
                aria-label="Open sidebar"
              >
                <Menu className="w-6 h-6" />
              </button>
              <div className="flex items-center gap-2 lg:hidden">
                <Activity className="w-5 h-5 text-sky-600" />
                <span className="font-extrabold text-sm text-slate-900">Swasth-IQ</span>
              </div>
            </div>

            {/* Right Controls: Install Web App & Profile */}
            <div className="flex items-center gap-2.5 ml-auto">
              <div className="hidden sm:block">
                <InstallPWAButton />
              </div>

              <div className="relative">
                <button
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-2 bg-slate-100/80 hover:bg-slate-200/80 border border-slate-200 px-3 py-1.5 rounded-xl transition-all"
                >
                  <div className="w-7 h-7 rounded-lg bg-sky-600 text-white flex items-center justify-center font-bold text-xs shrink-0">
                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <span className="hidden sm:block text-xs font-bold text-slate-900 max-w-[100px] truncate">
                    {user?.name}
                  </span>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
                </button>

                {profileOpen && (
                  <>
                    <div className="fixed inset-0 z-10" onClick={() => setProfileOpen(false)} />
                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-xl border border-slate-200/80 py-2 z-20 animate-fade-in">
                      <div className="px-4 py-3 border-b border-slate-100">
                        <p className="text-xs text-slate-400">Signed in as</p>
                        <p className="text-sm font-bold text-slate-900 truncate">{user?.email}</p>
                      </div>
                      <Link
                        to={ROUTES.PROFILE}
                        onClick={() => setProfileOpen(false)}
                        className="flex items-center px-4 py-2.5 text-xs font-bold text-slate-700 hover:bg-slate-50"
                      >
                        <User className="w-4 h-4 mr-3 text-slate-400" />
                        Profile Settings
                      </Link>
                      <div className="border-t border-slate-100 my-1" />
                      <button
                        onClick={handleLogout}
                        className="w-full text-left flex items-center px-4 py-2.5 text-xs font-bold text-rose-600 hover:bg-rose-50"
                      >
                        <LogOut className="w-4 h-4 mr-3" />
                        Sign Out
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-3 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>

        {/* Mobile Fixed Bottom Navigation Bar */}
        <MobileBottomBar />
      </div>
    </div>
  );
};

export default DashboardLayout;

