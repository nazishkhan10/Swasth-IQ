import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../hooks/useToast';
import { Activity, Eye, EyeOff, Mail, Lock, ArrowRight, Loader2 } from 'lucide-react';

const LoginPage = () => {
  const { login } = useAuth();
  const { showSuccess, showError } = useToast();
  const navigate = useNavigate();

  const [form, setForm] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!form.email.trim()) errs.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errs.email = 'Enter a valid email';
    if (!form.password) errs.password = 'Password is required';
    return errs;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: '' }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }

    setLoading(true);
    try {
      await login({ email: form.email.trim(), password: form.password });
      showSuccess('Welcome back! Login successful.');
      navigate('/dashboard');
    } catch (err) {
      const detail = err?.response?.data?.detail || 'Login failed. Please try again.';
      showError(detail);
      setErrors({ general: detail });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-80px)] bg-slate-50 flex items-center justify-center py-12 px-4 sm:px-6">
      <div className="w-full max-w-md animate-slide-up">
        {/* Card */}
        <div className="card p-8 sm:p-10 shadow-xl">
          {/* Logo / Header */}
          <div className="text-center mb-8">
            <div className="w-14 h-14 bg-gradient-to-tr from-sky-600 to-teal-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-sky-600/25">
              <Activity className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900">Welcome back</h1>
            <p className="text-sm text-slate-500 mt-1">Sign in to your account to continue</p>
          </div>

          {/* General Error */}
          {errors.general && (
            <div className="mb-5 px-4 py-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl">
              {errors.general}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate className="space-y-5">
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 w-4 h-4 text-slate-400 pointer-events-none" />
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="you@example.com"
                  className={`input-base pl-11 ${errors.email ? 'input-error' : ''}`}
                />
              </div>
              {errors.email && <p className="mt-1.5 text-xs text-red-600">{errors.email}</p>}
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label htmlFor="password" className="block text-sm font-semibold text-slate-700">
                  Password
                </label>
                <button
                  type="button"
                  className="text-xs text-sky-600 hover:text-sky-700 font-medium transition-colors"
                  onClick={() => showError('Password reset is not yet available. Coming soon.')}
                >
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="Your password"
                  className={`input-base pl-11 pr-12 ${errors.password ? 'input-error' : ''}`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <EyeOff className="w-4.5 h-4.5 w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="mt-1.5 text-xs text-red-600">{errors.password}</p>}
            </div>

            {/* Remember Me & Demo Login */}
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <input
                  id="remember-me"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-300 text-sky-600 focus:ring-sky-500 cursor-pointer"
                />
                <label htmlFor="remember-me" className="text-sm text-slate-600 cursor-pointer select-none">
                  Remember me
                </label>
              </div>
              <button
                type="button"
                onClick={() => setForm({ email: 'demo@cliniclens.ai', password: 'password123' })}
                className="text-xs bg-sky-50 text-sky-700 hover:bg-sky-100 font-semibold px-2.5 py-1 rounded-lg transition-all border border-sky-200"
              >
                🔑 Auto Fill Demo
              </button>
            </div>


            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-3.5 text-base rounded-xl mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  Sign In
                  <ArrowRight className="w-5 h-5 ml-2" />
                </>
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500">
            Don't have an account?{' '}
            <Link to="/register" className="text-sky-600 hover:text-sky-700 font-semibold transition-colors">
              Create one free
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
