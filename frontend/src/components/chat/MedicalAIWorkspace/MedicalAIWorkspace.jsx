import React, { useState, useEffect } from 'react';
import { 
  Bot, RefreshCw, Send, Paperclip, Sparkles, Activity, FileText, 
  ChevronRight, Menu, X, ShieldCheck 
} from 'lucide-react';

import chatApi from '../../../services/chatApi';
import LeftClinicalDashboard from './LeftClinicalDashboard';
import RightIntelligencePanel from './RightIntelligencePanel';
import LandingDashboard from './LandingDashboard';
import ThinkingSkeleton from './ThinkingSkeleton';
import StructuredResponseView from './StructuredResponseView';

export default function MedicalAIWorkspace({ reportId, report, analysisData }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [inputQuery, setInputQuery] = useState('');
  const [starters, setStarters] = useState([]);
  const [insights, setInsights] = useState(null);
  const [citations, setCitations] = useState([]);

  // Mobile Bottom Sheet States
  const [showLeftMobile, setShowLeftMobile] = useState(false);
  const [showRightMobile, setShowRightMobile] = useState(false);

  useEffect(() => {
    initWorkspace();
    return () => {
      chatApi.closeSession(reportId).catch(() => {});
    };
  }, [reportId]);

  const initWorkspace = async () => {
    try {
      await chatApi.initSession(reportId);
      loadStarters();
      loadInsights();
      loadHistory();
    } catch (err) {
      console.error('Workspace init error:', err);
    }
  };

  const loadStarters = async () => {
    try {
      const data = await chatApi.getStarters(reportId);
      setStarters(data || []);
    } catch (err) {
      console.error('Failed to load starters', err);
    }
  };

  const loadInsights = async () => {
    try {
      const data = await chatApi.getInsights(reportId);
      setInsights(data);
    } catch (err) {
      console.error('Failed to load insights', err);
    }
  };

  const loadHistory = async () => {
    try {
      const data = await chatApi.getHistory(reportId);
      setMessages(data || []);
    } catch (err) {
      console.error('Failed to load history', err);
    }
  };

  const handleSend = async (question) => {
    const q = question || inputQuery;
    if (!q.trim()) return;

    setInputQuery('');
    setLoading(true);

    const userMsg = { role: 'user', content: q, id: Date.now() };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await chatApi.sendMessage(reportId, q);
      setMessages((prev) => [
        ...prev,
        {
          id: res.message_id,
          role: 'assistant',
          content: res.content,
          content_json: res.content_json,
          intent: res.intent,
          provider_used: res.provider_used || 'OpenAI (gpt-5-nano)'
        }
      ]);
      setCitations(res.citations || []);
    } catch (err) {
      console.error('Send error:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'AI Assistant is temporarily unavailable. Your deterministic clinical results remain unaffected.',
          provider_used: 'OpenAI (gpt-5-nano)'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      await chatApi.closeSession(reportId);
      await initWorkspace();
      setMessages([]);
      setCitations([]);
    } catch (err) {
      console.error('Reset error:', err);
    }
  };

  return (
    <div className="flex flex-col gap-3 min-h-[calc(100vh-120px)] text-slate-800">
      {/* Executive Workstation Header */}
      <div className="flex items-center justify-between gap-3 bg-white border border-slate-200/80 p-3.5 rounded-2xl shadow-2xs">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-slate-900 text-emerald-400 flex items-center justify-center font-bold">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              Medical AI Clinical Workstation
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                Freeze v8.2 Active
              </span>
            </h2>
            <p className="text-[11px] text-slate-500 font-medium">
              GPT-5 Nano Narrator · Report-Scoped Session `#${reportId}`
            </p>
          </div>
        </div>

        {/* Mobile Sidebar Toggle Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowLeftMobile(!showLeftMobile)}
            className="lg:hidden p-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 text-xs font-bold flex items-center gap-1"
          >
            <Activity className="w-4 h-4" /> Clinical
          </button>
          <button
            onClick={() => setShowRightMobile(!showRightMobile)}
            className="lg:hidden p-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 text-xs font-bold flex items-center gap-1"
          >
            <FileText className="w-4 h-4" /> Evidence
          </button>
          <button
            onClick={handleReset}
            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Reset Chat
          </button>
        </div>
      </div>

      {/* 3-Column Workstation Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-1 items-start">
        {/* Left Column (Clinical Dashboard) */}
        <div className="hidden lg:block lg:col-span-3">
          <LeftClinicalDashboard report={report} analysisData={analysisData} organScores={insights?.organ_scores} insights={insights} />
        </div>

        {/* Center Column (Chat Workspace Feed & Input) */}
        <div className="lg:col-span-6 flex flex-col gap-3 h-full">
          {/* Main Feed */}
          <div className="flex-1 overflow-y-auto min-h-[420px] max-h-[620px] pr-1 flex flex-col gap-3">
            {messages.length === 0 ? (
              <LandingDashboard
                patientSummary={insights?.patient_summary}
                starters={starters}
                onSelectQuestion={handleSend}
              />
            ) : (
              messages.map((m, idx) => (
                <div key={m.id || idx} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                  {m.role === 'user' ? (
                    <div className="bg-indigo-600 text-white px-4 py-2.5 rounded-2xl rounded-tr-xs text-xs font-medium max-w-[85%] shadow-2xs">
                      {m.content}
                    </div>
                  ) : (
                    <StructuredResponseView
                      message={m}
                      onSelectQuestion={handleSend}
                      onAction={(action) => handleSend(`${action.toUpperCase()} explanation for my report`)}
                    />
                  )}
                </div>
              ))
            )}

            {loading && <ThinkingSkeleton />}
          </div>

          {/* Clean Expanding Input Bar (NO voice microphone) */}
          <div className="flex items-center gap-2 bg-white border border-slate-200 p-2 rounded-2xl shadow-2xs">
            <button className="p-2 rounded-xl bg-slate-100 text-slate-500 hover:text-slate-800 hover:bg-slate-200 transition-all">
              <Paperclip className="w-4 h-4" />
            </button>
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask anything about your lab report parameters, findings, or lifestyle guidance..."
              className="flex-1 text-xs text-slate-800 outline-hidden bg-transparent px-1 font-medium"
            />
            <button
              onClick={() => handleSend()}
              disabled={loading || !inputQuery.trim()}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-xs transition-all flex items-center gap-1 shadow-2xs"
            >
              <Send className="w-3.5 h-3.5" />
              Send
            </button>
          </div>
        </div>

        {/* Right Column (Tabbed Intelligence Panel) */}
        <div className="hidden lg:block lg:col-span-3 h-full">
          <RightIntelligencePanel citations={citations} analysisData={analysisData} />
        </div>
      </div>

      {/* Mobile Bottom Sheets */}
      {showLeftMobile && (
        <div className="fixed inset-0 bg-slate-900/50 z-50 flex flex-col justify-end lg:hidden">
          <div className="bg-white p-4 rounded-t-3xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center pb-2 mb-2 border-b border-slate-100">
              <h3 className="font-bold text-sm">Clinical Dashboard</h3>
              <button onClick={() => setShowLeftMobile(false)}><X className="w-5 h-5" /></button>
            </div>
            <LeftClinicalDashboard report={report} analysisData={analysisData} organScores={insights?.organ_scores} insights={insights} />
          </div>
        </div>
      )}

      {showRightMobile && (
        <div className="fixed inset-0 bg-slate-900/50 z-50 flex flex-col justify-end lg:hidden">
          <div className="bg-white p-4 rounded-t-3xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center pb-2 mb-2 border-b border-slate-100">
              <h3 className="font-bold text-sm">Intelligence Panel</h3>
              <button onClick={() => setShowRightMobile(false)}><X className="w-5 h-5" /></button>
            </div>
            <RightIntelligencePanel citations={citations} analysisData={analysisData} />
          </div>
        </div>
      )}
    </div>
  );
}
