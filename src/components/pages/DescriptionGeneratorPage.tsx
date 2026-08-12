import React, { useState } from 'react';
import { ListFilter, Sparkles, Copy, Clock, Link as LinkIcon } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const DescriptionGeneratorPage: React.FC = () => {
  const { showToast } = useAppState();
  const [topic, setTopic] = useState('How AI Will Replace Web Developers in 2026');
  const [loading, setLoading] = useState(false);
  const [descOutput, setDescOutput] = useState(`🔥 In this video, we test whether AI coding tools like Gemini 3.5 and Cursor IDE can build production-ready fullstack web applications from scratch.

📌 TIMESTAMPS:
00:00 - The Shocking Truth About AI Coding
02:15 - Testing Gemini 3.5 on Fullstack Apps
05:40 - Can AI Write Clean Code?
08:10 - Is Your Software Developer Job Safe?
10:30 - Final Verdict & Free Resources

🔗 RESOURCES & LINKS:
► Try VidPulse AI: https://vidpulse.ai
► Download Free AI Prompt Cheat Sheet: https://vidpulse.ai/cheat-sheet

#AICoding #WebDevelopment #Gemini3 #SoftwareEngineering #TechNews`);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('/api/ai/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: topic, type: 'description' }),
      });
      const data = await res.json();
      showToast('Generated YouTube description template!');
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
          <ListFilter className="w-7 h-7 text-red-500" />
          Smart SEO Description & Timestamp Generator
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
          Generate structured, high-ranking video descriptions with timestamp placeholders, call to action links, and hashtags.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <GlassCard className="p-6 space-y-4">
          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                Video Topic / Title
              </label>
              <textarea
                rows={4}
                required
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-red-500 focus:outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-red-600 to-amber-500 text-white font-bold text-xs shadow-lg shadow-red-500/25 hover:opacity-95 transition-all flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>{loading ? 'Building Description...' : 'Generate Description'}</span>
            </button>
          </form>
        </GlassCard>

        <GlassCard className="lg:col-span-2 p-6 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800 mb-4">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Generated SEO Description Output
              </h3>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(descOutput);
                  showToast('Description copied to clipboard!');
                }}
                className="px-3 py-1.5 rounded-lg bg-red-500/10 text-red-500 font-bold text-xs hover:bg-red-500 hover:text-white transition-all flex items-center gap-1.5"
              >
                <Copy className="w-3.5 h-3.5" />
                <span>Copy Text</span>
              </button>
            </div>

            <textarea
              rows={12}
              value={descOutput}
              onChange={(e) => setDescOutput(e.target.value)}
              className="w-full p-4 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-mono text-slate-800 dark:text-slate-200 leading-relaxed focus:outline-none focus:ring-2 focus:ring-red-500"
            />
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
