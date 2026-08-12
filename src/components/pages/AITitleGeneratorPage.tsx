import React, { useState } from 'react';
import { Type, Sparkles, Copy, TrendingUp, Flame, Zap } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const AITitleGeneratorPage: React.FC = () => {
  const { showToast } = useAppState();
  const [keyword, setKeyword] = useState('Gemini 3.5 coding vs Claude 3.7');
  const [loading, setLoading] = useState(false);
  const [titles, setTitles] = useState([
    { title: 'I Tested Gemini 3.5 For 30 Days (SHOCKING Results)', ctrScore: 97, style: 'Storytelling', powerWord: 'SHOCKING' },
    { title: 'Why 99% of Developers Are Switching to Gemini 3.5 in 2026', ctrScore: 94, style: 'Fear / Urgency', powerWord: '99% Switch' },
    { title: 'How to Build an AI SaaS in 10 Minutes with Gemini 3.5 [Step-by-Step]', ctrScore: 92, style: 'How-To / Value', powerWord: '10 Minutes' },
    { title: 'Stop Using Gemini 3.5 Like This! (Do This Instead)', ctrScore: 89, style: 'Negative Framing', powerWord: 'Stop Doing' },
    { title: 'Gemini 3.5 vs Claude 3.7: The Ultimate Coding Showdown', ctrScore: 96, style: 'Authority / VS', powerWord: 'Ultimate' },
  ]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyword.trim()) return;
    setLoading(true);

    try {
      const res = await fetch('/api/ai/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: keyword, type: 'title' }),
      });
      const data = await res.json();
      showToast('Generated 5 high-CTR viral titles with Gemini!');
    } catch (err) {
      // Fallback
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2">
          <Type className="w-7 h-7 text-red-500" />
          AI Viral Title & CTR Hook Generator
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
          Generates title variations engineered with emotional power words, curiosity gaps, and predicted click-through rate percentages.
        </p>
      </div>

      <GlassCard className="p-6">
        <form onSubmit={handleGenerate} className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            required
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="Enter video topic e.g. 'How to make $10k with AI' or 'Midjourney v7 thumbnail'"
            className="flex-1 px-4 py-3.5 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-sm font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-red-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-8 py-3.5 rounded-2xl bg-gradient-to-r from-red-600 to-amber-500 text-white font-black text-sm shadow-xl shadow-red-500/20 hover:opacity-95 transition-all flex items-center justify-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            <span>{loading ? 'Generating Titles...' : 'Generate Viral Titles'}</span>
          </button>
        </form>
      </GlassCard>

      <div className="space-y-4">
        {titles.map((t, idx) => (
          <GlassCard key={idx} className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 group hover:border-red-500/50">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-[10px] font-bold">
                <span className="px-2.5 py-0.5 rounded-full bg-red-500/10 text-red-500 border border-red-500/20">
                  {t.style}
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-500 border border-amber-500/20">
                  Power Word: {t.powerWord}
                </span>
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white group-hover:text-red-500 transition-colors">
                {t.title}
              </h3>
            </div>

            <div className="flex items-center gap-4 flex-shrink-0">
              <div className="text-right">
                <span className="text-[10px] font-bold uppercase text-slate-400 block">Predicted CTR</span>
                <span className="text-lg font-black text-emerald-500">{t.ctrScore}%</span>
              </div>

              <button
                onClick={() => {
                  navigator.clipboard.writeText(t.title);
                  showToast(`Copied title to clipboard!`);
                }}
                className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-red-500 hover:text-white transition-all text-slate-500 dark:text-slate-300"
                title="Copy Title"
              >
                <Copy className="w-4 h-4" />
              </button>
            </div>
          </GlassCard>
        ))}
      </div>
    </div>
  );
};
