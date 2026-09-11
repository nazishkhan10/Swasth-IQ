import React from 'react';
import { HelpCircle } from 'lucide-react';

export default function SuggestedQuestions({ onSelectQuestion }) {
  const questions = [
    "Explain my report overall.",
    "Why is my HbA1c elevated?",
    "What does my eGFR score of 54 mean?",
    "Why did the AI detect CKD?",
    "What foods should I eat & avoid?",
    "Which doctor should I consult?"
  ];

  return (
    <div className="flex flex-col gap-2 my-2">
      <div className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
        <HelpCircle className="w-3.5 h-3.5 text-indigo-400" />
        Suggested Clinical Questions:
      </div>
      <div className="flex flex-wrap gap-2">
        {questions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => onSelectQuestion(q)}
            className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-indigo-200 border border-slate-700 hover:border-indigo-500 transition-all text-left"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
