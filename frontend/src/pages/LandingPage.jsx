import React from 'react';
import { Link } from 'react-router-dom';
import {
  Activity, Upload, ScanLine, Brain, Salad, HeartPulse,
  ArrowRight, CheckCircle2, Sparkles, Shield, Zap, Users
} from 'lucide-react';

const features = [
  {
    icon: Upload,
    title: 'Upload Reports',
    description: 'Securely upload your medical reports in PDF, image, or text format. All files are encrypted and stored safely.',
    color: 'sky',
  },
  {
    icon: ScanLine,
    title: 'OCR Extraction',
    description: 'Advanced optical character recognition extracts all medical values and parameters from your reports automatically.',
    color: 'violet',
  },
  {
    icon: Brain,
    title: 'AI Analysis',
    description: 'Our AI engine analyses your report data against clinical references and generates a clear health summary.',
    color: 'teal',
  },
  {
    icon: Salad,
    title: 'Diet Suggestions',
    description: 'Get personalised diet and nutrition recommendations tailored to your specific lab results and health markers.',
    color: 'emerald',
  },
  {
    icon: HeartPulse,
    title: 'Lifestyle Insights',
    description: 'Receive actionable lifestyle and exercise recommendations to improve your health indicators over time.',
    color: 'rose',
  },
  {
    icon: Shield,
    title: 'Secure & Private',
    description: 'Your medical data is encrypted end-to-end. We follow strict privacy standards to protect your information.',
    color: 'amber',
  },
];

const colorMap = {
  sky:     'bg-sky-50 text-sky-600 border-sky-100',
  violet:  'bg-violet-50 text-violet-600 border-violet-100',
  teal:    'bg-teal-50 text-teal-600 border-teal-100',
  emerald: 'bg-emerald-50 text-emerald-600 border-emerald-100',
  rose:    'bg-rose-50 text-rose-600 border-rose-100',
  amber:   'bg-amber-50 text-amber-600 border-amber-100',
};

const stats = [
  { value: 'AI-Powered', label: 'Medical Analysis' },
  { value: '5+', label: 'Report Formats Supported' },
  { value: '100%', label: 'Private & Encrypted' },
  { value: 'Phase 1', label: 'Live & Running' },
];

const LandingPage = () => {
  return (
    <div className="min-h-screen">
      {/* ── Hero Section ─────────────────────────────────────── */}
      <section className="relative overflow-hidden bg-white">
        {/* Background decoration */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className="absolute -top-40 -right-32 w-[600px] h-[600px] bg-sky-50 rounded-full opacity-60" />
          <div className="absolute -bottom-20 -left-20 w-96 h-96 bg-teal-50 rounded-full opacity-50" />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24 sm:pt-28 sm:pb-32">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-sky-50 border border-sky-100 text-sky-700 text-xs font-semibold px-4 py-1.5 rounded-full mb-8">
              <Sparkles className="w-3.5 h-3.5" />
              AI-Powered Medical Intelligence · Phase 1 Live
            </div>

            {/* Heading */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold text-slate-900 tracking-tight leading-[1.1] mb-6">
              Understand Your{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-600 to-teal-500">
                Medical Reports
              </span>{' '}
              Instantly
            </h1>

            <p className="text-lg sm:text-xl text-slate-500 leading-relaxed max-w-2xl mx-auto mb-10">
              Upload your lab results. Our AI extracts, analyses, and explains every value—giving you personalised
              diet and lifestyle recommendations in plain language.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/register"
                className="btn-primary px-8 py-4 text-base rounded-2xl w-full sm:w-auto"
              >
                Get Started Free
                <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
              <Link
                to="/login"
                className="btn-secondary px-8 py-4 text-base rounded-2xl w-full sm:w-auto"
              >
                Sign In
              </Link>
            </div>

            {/* Trust signals */}
            <div className="flex flex-wrap items-center justify-center gap-5 mt-10 text-sm text-slate-500">
              {['No credit card required', 'Free to use', 'HIPAA-Ready architecture'].map((item) => (
                <div key={item} className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  {item}
                </div>
              ))}
            </div>
          </div>

          {/* Stats row */}
          <div className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-6 max-w-3xl mx-auto">
            {stats.map((s) => (
              <div key={s.label} className="card p-5 text-center">
                <p className="text-2xl font-extrabold text-sky-600 mb-1">{s.value}</p>
                <p className="text-xs text-slate-500 font-medium">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features Section ─────────────────────────────────── */}
      <section className="py-20 sm:py-28 bg-slate-50" id="features">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <span className="section-label mb-4 inline-block">Everything You Need</span>
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
              From Upload to Insights in Minutes
            </h2>
            <p className="text-slate-500 max-w-xl mx-auto text-base leading-relaxed">
              A complete pipeline that takes your raw medical report and transforms it into actionable health guidance.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => {
              const iconStyle = colorMap[feature.color] || colorMap.sky;
              return (
                <div key={feature.title} className="card-hover p-6 group">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center border mb-5 ${iconStyle}`}>
                    <feature.icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-base font-semibold text-slate-900 mb-2">{feature.title}</h3>
                  <p className="text-sm text-slate-500 leading-relaxed">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── How It Works ─────────────────────────────────────── */}
      <section className="py-20 sm:py-28 bg-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <span className="section-label mb-4 inline-block">Simple Process</span>
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">How It Works</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                icon: Upload,
                title: 'Upload Your Report',
                desc: 'Upload your medical report in any supported format — PDF, image, or text file.',
              },
              {
                step: '02',
                icon: ScanLine,
                title: 'AI Processes It',
                desc: 'Our OCR and AI engine extracts all medical parameters and analyses each value.',
              },
              {
                step: '03',
                icon: HeartPulse,
                title: 'Get Your Insights',
                desc: 'Receive a clear summary plus personalised diet and lifestyle recommendations.',
              },
            ].map((step, i) => (
              <div key={step.step} className="relative flex flex-col items-center text-center px-4">
                <div className="w-16 h-16 bg-gradient-to-tr from-sky-600 to-teal-500 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-sky-600/20 mb-5">
                  <step.icon className="w-7 h-7" />
                </div>
                <span className="text-xs font-bold text-sky-500 uppercase tracking-widest mb-2">{step.step}</span>
                <h3 className="text-base font-semibold text-slate-900 mb-2">{step.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{step.desc}</p>
                {i < 2 && (
                  <div className="hidden md:block absolute top-8 left-full w-full h-px border-t-2 border-dashed border-slate-200 -translate-x-1/2" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA Banner ───────────────────────────────────────── */}
      <section className="py-20 bg-gradient-to-r from-sky-600 to-teal-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <Zap className="w-12 h-12 text-sky-200 mx-auto mb-5" />
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Take Control of Your Health Today
          </h2>
          <p className="text-sky-100 text-base max-w-xl mx-auto mb-8">
            Join and start understanding your medical reports with the power of AI — completely free to try.
          </p>
          <Link
            to="/register"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-sky-700 font-bold text-base rounded-2xl hover:bg-sky-50 transition-all shadow-xl"
          >
            Create Free Account
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
