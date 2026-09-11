import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, Heart, Shield, Zap } from 'lucide-react';

export const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-slate-900 text-white" id="about">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">

          {/* Brand Column */}
          <div className="md:col-span-2">
            <Link to="/" className="flex items-center space-x-3 mb-4 group w-fit">
              <div className="w-10 h-10 bg-gradient-to-tr from-sky-500 to-teal-400 rounded-xl flex items-center justify-center shadow-lg">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="text-lg font-bold text-white block leading-tight">Medical Report Analyzer</span>
                <span className="text-xs text-sky-400 font-semibold tracking-wide uppercase">AI-Powered Insights</span>
              </div>
            </Link>
            <p className="text-slate-400 text-sm leading-relaxed max-w-sm">
              A modern AI-powered medical report analysis platform that helps you understand your health data, 
              get personalized diet and lifestyle recommendations, and take control of your wellbeing.
            </p>

            <div className="flex items-center gap-5 mt-6">
              <div className="flex items-center gap-1.5 text-xs text-slate-400">
                <Shield className="w-3.5 h-3.5 text-emerald-400" />
                <span>HIPAA-Ready</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-slate-400">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                <span>AI Powered</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-slate-400">
                <Heart className="w-3.5 h-3.5 text-red-400" />
                <span>Health First</span>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Product</h3>
            <ul className="space-y-2.5">
              {[
                { label: 'Features', href: '#features' },
                { label: 'How It Works', href: '#about' },
                { label: 'Dashboard', href: '/dashboard' },
                { label: 'Register', href: '/register' },
                { label: 'Login', href: '/login' },
              ].map((link) => (
                <li key={link.label}>
                  <Link
                    to={link.href}
                    className="text-sm text-slate-400 hover:text-sky-400 transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Future Features */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Coming Soon</h3>
            <ul className="space-y-2.5">
              {[
                'OCR Report Parsing',
                'AI Analysis Engine',
                'Diet Recommendations',
                'Lifestyle Insights',
                'Report History',
                'PDF Export',
              ].map((feature) => (
                <li key={feature} className="text-sm text-slate-500 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-sky-600/50 flex-shrink-0" />
                  {feature}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-slate-800 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-slate-500">
            © {currentYear} Medical Report Analyzer. Built for health, powered by AI.
          </p>
          <p className="text-xs text-slate-600">
            ⚠️ Not a substitute for professional medical advice. Always consult a licensed physician.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
