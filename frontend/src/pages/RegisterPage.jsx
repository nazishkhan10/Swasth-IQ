import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../hooks/useToast';
import { Activity, Eye, EyeOff, Mail, Lock, User, ArrowRight, Loader2, CheckCircle2 } from 'lucide-react';

const PASSWORD_MIN = 6;

const RegisterPage = () => {
  const { register } = useAuth();
  const { showSuccess, showError } = useToast();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    confirm_password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!form.name.trim() || form.name.trim().length < 2)
      errs.name = 'Full name must be at least 2 characters';
    if (!form.email.trim())
      errs.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email))
      errs.email = 'Enter a valid email address';
    if (!form.password || form.password.length < PASSWORD_MIN)
      errs.password = `Password must be at least ${PASSWORD_MIN} characters`;
    if (!form.confirm_password)
      errs.confirm_password = 'Please confirm your password';
    else if (form.password !== form.confirm_password)
      errs.confirm_password = 'Passwords do not match';
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
      await register({
        name: form.name.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        confirm_password: form.confirm_password,
      });
      setSuccess(true);
      showSuccess('Account created! Redirecting to login...');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      const detail = err?.response?.data?.detail || 'Registration failed. Please try again.';
      showError(detail);
      setErrors({ general: detail });
    } finally {
      setLoading(false);
    }
  };

  // Password strength
  const strength = (() => {
    const p = form.password;
    if (!p) return null;
    let score = 0;
    if (p.length >= 6) score++;
    if (p.length >= 10) score++;
    if (/[A-Z]/.test(p)) score++;
    if (/[0-9]/.test(p)) score++;
    if (/[^A-Za-z0-9]/.test(p)) score++;
    return score;
  })();

  const strengthLabel = strength === null ? null
    : strength <= 1 ? { text: 'Weak', color: 'bg-red-400' }
    : strength <= 2 ? { text: 'Fair', color: 'bg-amber-400' }
    : strength <= 3 ? { text: 'Good', color: 'bg-sky-400' }
    : { text: 'Strong', color: 'bg-emerald-400' };

  if (success) {
    return (
      <div className="min-h-[calc(100vh-80px)] bg-slate-50 flex items-center justify-center py-12 px-4">
        <div className="card p-10 max-w-sm w-full text-center animate-slide-up shadow-xl">
          <div className="w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-emerald-200">
            <CheckCircle2 className="w-8 h-8 text-emerald-500" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Account Created!</h2>
          <p className="text-sm text-slate-500">Redirecting you to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-80px)] bg-slate-50 flex items-center justify-center py-12 px-4 sm:px-6">
      <div className="w-full max-w-md animate-slide-up">
        <div className="card p-8 sm:p-10 shadow-xl">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-14 h-14 bg-gradient-to-tr from-sky-600 to-teal-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-sky-600/25">
              <Activity className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900">Create your account</h1>
            <p className="text-sm text-slate-500 mt-1">Start understanding your health today</p>
          </div>

          {/* General Error */}
          {errors.general && (
            <div className="mb-5 px-4 py-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl">
              {errors.general}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate className="space-y-5">
            {/* Full Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                <input
                  id="name"
                  name="name"
                  type="text"
                  autoComplete="name"
                  value={form.name}
                  onChange={handleChange}
                  placeholder="Jane Smith"
                  className={`input-base pl-11 ${errors.name ? 'input-error' : ''}`}
                />
              </div>
              {errors.name && <p className="mt-1.5 text-xs text-red-600">{errors.name}</p>}
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
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
              <label htmlFor="password" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="Min. 6 characters"
                  className={`input-base pl-11 pr-12 ${errors.password ? 'input-error' : ''}`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="mt-1.5 text-xs text-red-600">{errors.password}</p>}
              {/* Strength bar */}
              {strengthLabel && (
                <div className="mt-2">
                  <div className="flex gap-1 mb-1">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <div
                        key={i}
                        className={`h-1 flex-1 rounded-full transition-all ${
                          i <= strength ? strengthLabel.color : 'bg-slate-200'
                        }`}
                      />
                    ))}
                  </div>
                  <p className="text-xs text-slate-500">
                    Password strength: <span className="font-semibold">{strengthLabel.text}</span>
                  </p>
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="confirm_password" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                <input
                  id="confirm_password"
                  name="confirm_password"
                  type={showConfirm ? 'text' : 'password'}
                  autoComplete="new-password"
                  value={form.confirm_password}
                  onChange={handleChange}
                  placeholder="Repeat your password"
                  className={`input-base pl-11 pr-12 ${errors.confirm_password ? 'input-error' : ''}`}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirm(!showConfirm)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  aria-label="Toggle confirm password visibility"
                >
                  {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.confirm_password && (
                <p className="mt-1.5 text-xs text-red-600">{errors.confirm_password}</p>
              )}
              {form.confirm_password && !errors.confirm_password && form.password === form.confirm_password && (
                <p className="mt-1.5 text-xs text-emerald-600 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Passwords match
                </p>
              )}
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
                  Creating account...
                </>
              ) : (
                <>
                  Create Account
                  <ArrowRight className="w-5 h-5 ml-2" />
                </>
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500">
            Already have an account?{' '}
            <Link to="/login" className="text-sky-600 hover:text-sky-700 font-semibold transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
