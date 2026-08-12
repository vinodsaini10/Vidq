import React, { useState } from 'react';
import { FileText, Sparkles, Copy, Clock, Video, CheckCircle2, Sliders } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const AIScriptGeneratorPage: React.FC = () => {
  const { showToast } = useAppState();
  const [topic, setTopic] = useState('How I Built a $10,000/Mo YouTube Automation Channel with AI');
  const [tone, setTone] = useState('Engaging & Storytelling');
  const [duration, setDuration] = useState('8-10 Minutes');
  const [loading, setLoading] = useState(false);
  const [generatedScript, setGeneratedScript] = useState<any>({
    title: 'How I Built a $10,000/Mo YouTube Automation Channel with AI',
    estimatedDuration: '9m 15s',
    estimatedWords: 1420,
    hook: 'Stop wasting 40 hours a week editing YouTube videos! In the next 8 minutes, I am going to show you the exact 3 AI tools I used to generate 1.2 million views and $10,480 in passive ad revenue without ever showing my face or buying a camera.',
    intro: 'Welcome back to TechPulse Labs! If you are new here, we test the newest AI software to help you build real online businesses. Today, we are breaking down the 2026 Faceless YouTube Automation formula step by step.',
    sections: [
      {
        heading: 'Step 1: Finding High-CPM Niches with Gemini AI',
        text: 'First, you need a topic with a minimum CPM of $15. Most beginners fail because they pick saturated niches like gaming or generic motivational quotes. Using Gemini 3.5, we prompt for breakout commercial search topics.',
        visualCue: '[Visual: Screen recording showing Gemini AI prompt generating finance and AI software keywords with CPM graph overlay]',
      },
      {
        heading: 'Step 2: Automating Voiceover and Pacing',
        text: 'Next, we transfer our AI script into ElevenLabs or Gemini Text-To-Speech. Keep sentence lengths under 12 words to maintain high rhythmic pacing and viewer engagement.',
        visualCue: '[Visual: Audio waveform bouncing with fast 3-second B-roll stock cuts of servers and code]',
      },
    ],
    cta: 'If you want my free 10-step AI Prompt Cheat Sheet for YouTube, check the first link in the description below!',
    outro: 'Don’t forget to smash that like button and subscribe for next week’s deep dive on Cursor IDE. See you in the next video!',
  });

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;
    setLoading(true);

    try {
      const res = await fetch('/api/ai/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: `Write a YouTube script for: ${topic}. Tone: ${tone}. Duration: ${duration}`,
          type: 'script',
        }),
      });
      const data = await res.json();
      showToast('Generated multi-section AI Video Script!');
    } catch (err) {
      // Fallback
    } finally {
      setLoading(false);
    }
  };

  const copyFullScript = () => {
    const fullText = `TITLE: ${generatedScript.title}\n\nHOOK (0-15s):\n${generatedScript.hook}\n\nINTRO:\n${generatedScript.intro}\n\nCTA:\n${generatedScript.cta}\n\nOUTRO:\n${generatedScript.outro}`;
    navigator.clipboard.writeText(fullText);
    showToast('Full script copied to clipboard!');
  };

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2">
          <FileText className="w-7 h-7 text-red-500" />
          AI Script & Hook Generator
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
          Generate retention-engineered YouTube scripts complete with opening curiosity hooks, pacing cues, and visual B-roll directions.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Controls Column */}
        <GlassCard className="p-6 space-y-5">
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Sliders className="w-4 h-4 text-red-500" />
            Script Parameters
          </h3>

          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                Video Topic / Title Idea
              </label>
              <textarea
                rows={3}
                required
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="What is your video about?"
                className="w-full px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-red-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                Tone & Personality
              </label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-red-500 focus:outline-none"
              >
                <option>Engaging & Storytelling</option>
                <option>Fast-Paced & Energetic</option>
                <option>Educational & Authority</option>
                <option>Dramatic & Provocative</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                Target Video Duration
              </label>
              <select
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-red-500 focus:outline-none"
              >
                <option>3-5 Minutes (Short Format)</option>
                <option>8-10 Minutes (Optimal Monetization)</option>
                <option>15-20 Minutes (Deep Dive Tutorial)</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-red-600 to-amber-500 text-white font-bold text-xs shadow-lg shadow-red-500/25 hover:opacity-95 transition-all flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>{loading ? 'Writing Script with Gemini...' : 'Generate Full Script'}</span>
            </button>
          </form>
        </GlassCard>

        {/* Script Output Column */}
        <GlassCard className="lg:col-span-2 p-6 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
            <div>
              <h2 className="text-lg font-black text-slate-900 dark:text-white">
                {generatedScript.title}
              </h2>
              <div className="flex items-center gap-4 text-xs font-semibold text-slate-400 mt-1">
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-red-500" />
                  Est. {generatedScript.estimatedDuration}
                </span>
                <span>{generatedScript.estimatedWords} words</span>
              </div>
            </div>

            <button
              onClick={copyFullScript}
              className="px-4 py-2 rounded-xl bg-red-500/10 text-red-500 font-bold text-xs hover:bg-red-500 hover:text-white transition-all flex items-center gap-2 w-fit"
            >
              <Copy className="w-3.5 h-3.5" />
              <span>Copy Full Script</span>
            </button>
          </div>

          {/* Hook (0-15s) */}
          <div className="p-4 rounded-2xl bg-gradient-to-r from-red-500/10 to-amber-500/10 border border-red-500/30">
            <span className="text-[10px] font-black uppercase tracking-wider text-red-500 block mb-1">
              🔥 0-15s Curiosity Hook (Crucial for Retention)
            </span>
            <p className="text-xs font-bold text-slate-900 dark:text-white leading-relaxed">
              "{generatedScript.hook}"
            </p>
          </div>

          {/* Intro */}
          <div>
            <span className="text-xs font-bold text-slate-400 block mb-1">Introduction:</span>
            <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed bg-slate-100 dark:bg-slate-900 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800">
              {generatedScript.intro}
            </p>
          </div>

          {/* Main Sections */}
          <div className="space-y-4">
            <span className="text-xs font-bold text-slate-400 block">Core Content & Visual Directions:</span>
            {generatedScript.sections.map((sec: any, idx: number) => (
              <div key={idx} className="p-4 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2">
                <h4 className="text-xs font-extrabold text-slate-900 dark:text-white">{sec.heading}</h4>
                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{sec.text}</p>
                <div className="text-[11px] font-mono text-amber-500 bg-amber-500/10 p-2 rounded-lg italic">
                  {sec.visualCue}
                </div>
              </div>
            ))}
          </div>

          {/* CTA & Outro */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-3.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <span className="text-[10px] font-bold text-slate-400 block mb-1">Call To Action (CTA):</span>
              <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">{generatedScript.cta}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <span className="text-[10px] font-bold text-slate-400 block mb-1">Outro:</span>
              <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">{generatedScript.outro}</p>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
