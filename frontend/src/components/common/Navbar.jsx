import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { 
  Activity, 
  User, 
  LogOut, 
  Menu, 
  X, 
  ChevronDown, 
  FileText, 
  LayoutDashboard 
} from 'lucide-react';

export const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const { showInfo } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);

  const handleLogout = () => {
    logout();
    showInfo('Successfully logged out.');
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-100 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-11 h-11 bg-gradient-to-tr from-sky-600 to-teal-500 rounded-2xl flex items-center justify-center text-white shadow-md shadow-sky-600/20 group-hover:scale-105 transition-transform">
              <Activity className="w-6 h-6" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold text-slate-900 tracking-tight group-hover:text-sky-600 transition-colors">
                Medical Report
              </span>
              <span className="text-xs font-semibold text-sky-600 tracking-wider uppercase -mt-1">
                Analyzer AI
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link
              to="/"
              className={`text-sm font-medium transition-colors ${
                isActive('/') ? 'text-sky-600 font-semibold' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Home
            </Link>
            <a
              href="#features"
              className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
            >
              Features
            </a>
            <a
              href="#about"
              className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
            >
              About
            </a>

            {isAuthenticated && (
              <Link
                to="/dashboard"
                className={`text-sm font-medium transition-colors ${
                  isActive('/dashboard') ? 'text-sky-600 font-semibold' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Dashboard
              </Link>
            )}
          </nav>

          {/* Auth Action Buttons / Profile Dropdown */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                  className="flex items-center space-x-3 bg-slate-50 hover:bg-slate-100 border border-slate-200/80 px-3.5 py-2 rounded-xl transition-all"
                >
                  <div className="w-8 h-8 rounded-lg bg-sky-600 text-white flex items-center justify-center font-bold text-sm">
                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <div className="text-left">
                    <p className="text-xs font-semibold text-slate-900 max-w-[120px] truncate">
                      {user?.name || 'User'}
                    </p>
                    <p className="text-[10px] text-slate-500 max-w-[120px] truncate">
                      {user?.email}
                    </p>
                  </div>
                  <ChevronDown className="w-4 h-4 text-slate-400" />
                </button>

                {/* Profile Dropdown Menu */}
                {profileDropdownOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setProfileDropdownOpen(false)}
                    />
                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-xl border border-slate-100 py-2 z-20 animate-fade-in">
                      <div className="px-4 py-3 border-b border-slate-100">
                        <p className="text-xs text-slate-400 font-medium">Signed in as</p>
                        <p className="text-sm font-semibold text-slate-900 truncate">{user?.email}</p>
                      </div>

                      <Link
                        to="/dashboard"
                        onClick={() => setProfileDropdownOpen(false)}
                        className="flex items-center px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
                      >
                        <LayoutDashboard className="w-4 h-4 mr-3 text-sky-600" />
                        Dashboard
                      </Link>

                      <Link
                        to="/profile"
                        onClick={() => setProfileDropdownOpen(false)}
                        className="flex items-center px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
                      >
                        <User className="w-4 h-4 mr-3 text-slate-400" />
                        Profile Settings
                      </Link>

                      <div className="border-t border-slate-100 my-1"></div>

                      <button
                        onClick={handleLogout}
                        className="w-full text-left flex items-center px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors font-medium"
                      >
                        <LogOut className="w-4 h-4 mr-3 text-red-500" />
                        Sign Out
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link
                  to="/login"
                  className="px-4 py-2.5 text-sm font-semibold text-slate-700 hover:text-sky-600 transition-colors"
                >
                  Log In
                </Link>
                <Link
                  to="/register"
                  className="px-5 py-2.5 text-sm font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-xl transition-all shadow-md shadow-sky-600/20 active:scale-95"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-all"
              aria-label="Toggle Navigation"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-b border-slate-100 px-4 pt-3 pb-6 space-y-3 animate-slide-up">
          <Link
            to="/"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-base font-medium text-slate-700 hover:bg-slate-50"
          >
            Home
          </Link>
          <a
            href="#features"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-base font-medium text-slate-700 hover:bg-slate-50"
          >
            Features
          </a>
          <a
            href="#about"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-base font-medium text-slate-700 hover:bg-slate-50"
          >
            About
          </a>

          {isAuthenticated ? (
            <>
              <Link
                to="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-lg text-base font-medium text-sky-600 bg-sky-50"
              >
                Dashboard
              </Link>
              <Link
                to="/profile"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-lg text-base font-medium text-slate-700 hover:bg-slate-50"
              >
                Profile ({user?.name})
              </Link>
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  handleLogout();
                }}
                className="w-full text-left px-3 py-2 rounded-lg text-base font-medium text-red-600 hover:bg-red-50"
              >
                Sign Out
              </button>
            </>
          ) : (
            <div className="pt-4 border-t border-slate-100 flex flex-col space-y-2">
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2.5 text-base font-semibold text-slate-700 bg-slate-100 rounded-xl"
              >
                Log In
              </Link>
              <Link
                to="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2.5 text-base font-semibold text-white bg-sky-600 rounded-xl shadow-md"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
};

export default Navbar;
