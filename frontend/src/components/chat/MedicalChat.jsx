import React, { useState, useEffect } from 'react';
import { Bot, RefreshCw, ShieldCheck, Sparkles, AlertCircle, Cpu } from 'lucide-react';
import chatApi from '../../services/chatApi';
import ChatWindow from './ChatWindow';
import ChatInput from './ChatInput';
import SuggestedQuestions from './SuggestedQuestions';
import TransparencyBar from './TransparencyBar';
import RetrievedKnowledgePanel from './RetrievedKnowledgePanel';
import EvidencePanel from './EvidencePanel';

export default function MedicalChat({ reportId }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [citations, setCitations] = useState([]);
  const [starters, setStarters] = useState([]);
  const [metaInfo, setMetaInfo] = useState({
    confidence: 0.95,
    provider: 'OpenAI (gpt-5-nano)',
    isFallback: false,
    latencyMs: 0
  });

  useEffect(() => {
    // Initialize temporary Report-Scoped ChatSession
    initSession();
    fetchStarters();

    // Clean up session on report unmount
    return () => {
      chatApi.closeSession(reportId).catch(() => {});
    };
  }, [reportId]);

  const initSession = async () => {
    try {
      await chatApi.initSession(reportId);
      loadHistory();
    } catch (err) {
      console.error('Session init error:', err);
    }
  };

  const fetchStarters = async () => {
    try {
      const data = await chatApi.getStarters(reportId);
      setStarters(data || []);
    } catch (err) {
      console.error('Failed to load starter prompt chips', err);
    }
  };

  const loadHistory = async () => {
    try {
      const data = await chatApi.getHistory(reportId);
      setMessages(data || []);
    } catch (err) {
      console.error('Failed to load chat history', err);
    }
  };

  const handleSend = async (question) => {
    setLoading(true);
    const userMsg = { role: 'user', content: question, id: Date.now() };
    setMessages((prev) => [...prev, userMsg]);

    const startT = Date.now();
    try {
      const res = await chatApi.sendMessage(reportId, question);
      const elapsed = Date.now() - startT;

      setMessages((prev) => [
        ...prev,
        {
          id: res.message_id,
          role: 'assistant',
          content: res.content,
          intent: res.intent,
          provider_used: res.provider_used || 'OpenAI (gpt-5-nano)'
        }
      ]);

      setCitations(res.citations || []);
      setMetaInfo({
        confidence: res.confidence_score || 0.95,
        provider: res.provider_used || 'OpenAI (gpt-5-nano)',
        isFallback: false,
        latencyMs: res.latency_ms || elapsed
      });
    } catch (err) {
      console.error('Chat error', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'AI Assistant is temporarily unavailable. Your deterministic medical analysis remain available. Please try again shortly.',
          provider_used: 'OpenAI (gpt-5-nano)'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearSession = async () => {
    try {
      await chatApi.closeSession(reportId);
      await initSession();
      setMessages([]);
      setCitations([]);
    } catch (err) {
      console.error('Reset session error', err);
    }
  };

  const guidelineCount = citations.filter((c) => c.type === 'guideline').length;
  const evidenceCount = citations.filter((c) => c.type === 'evidence').length;

  return (
    <div className="flex flex-col gap-4">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white border border-slate-200/80 p-4 rounded-2xl shadow-2xs">
        <div>
          <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
            <Bot className="w-5 h-5 text-emerald-600" />
            AI Assistant — Current Report Only
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Powered by **OpenAI GPT-5 Nano** Explanation Layer · Scoped to active report `#${reportId}`
          </p>
        </div>

        <button
          onClick={handleClearSession}
          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Reset Conversation
        </button>
      </div>

      {/* AI Transparency Bar */}
      <TransparencyBar
        confidence={metaInfo.confidence}
        provider={metaInfo.provider}
        isFallback={false}
        latencyMs={metaInfo.latencyMs}
        evidenceCount={evidenceCount}
        guidelineCount={guidelineCount}
        knowledgeVersion="2026.1"
      />

      {/* Dynamic Starter Chips */}
      {starters.length > 0 && messages.length === 0 && (
        <div className="bg-emerald-50/50 border border-emerald-200/60 p-3.5 rounded-2xl flex flex-col gap-2">
          <div className="text-xs font-bold text-emerald-900 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
            Suggested Questions for this Report:
          </div>
          <div className="flex flex-wrap gap-2">
            {starters.map((chip, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(chip.query)}
                className="px-3 py-1.5 rounded-xl bg-white border border-emerald-200 text-emerald-800 text-xs font-medium hover:bg-emerald-600 hover:text-white transition-all shadow-2xs"
              >
                {chip.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Grid: Left Chat Window / Right Side Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Chat Feed Column */}
        <div className="lg:col-span-2 flex flex-col gap-3">
          <ChatWindow messages={messages} loading={loading} activeProvider={metaInfo.provider} />

          <ChatInput onSend={handleSend} loading={loading} />

          {/* Session Footer Notice */}
          <p className="text-center text-slate-400 text-xs mt-1">
            This conversation belongs only to the currently opened report. It will be cleared when this report is closed.
          </p>
        </div>

        {/* Cited Evidence & RAG Knowledge Side Panel */}
        <div className="flex flex-col gap-4">
          <RetrievedKnowledgePanel citations={citations} />
          <EvidencePanel citations={citations} />
        </div>
      </div>
    </div>
  );
}
