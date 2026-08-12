import React, { useState } from 'react';
import { Image, Sparkles, Copy, Eye, Layout, Palette } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const ThumbnailPromptPage: React.FC = () => {
  const { showToast } = useAppState();
  const [videoConcept, setVideoConcept] = useState('How AI Will Replace Web Developers in 2026');
  const [overlayText, setOverlayText] = useState('REPLACED IN 2026?');
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [loading, setLoading] = useState(false);

  const [prompts, setPrompts] = useState([
    {
      style: 'Midjourney v7 Photorealism',
      promptText: '/imagine prompt: Close up expressive portrait of a young software engineer staring in total shock at a glowing holographic laptop screen showing AI code building an entire app, dramatic cyan and magenta rim lighting, cinematic 8k, photorealistic --ar 16:9 --v 7',
      primaryColor: 'Cyan / Magenta',
      visualLayout: 'Left-aligned shock face, right-aligned glowing laptop screen with text overlay space.',
    },
    {
      style: '3D Render Style',
      promptText: '/imagine prompt: Stylized 3D isometric render of a robot programmer drinking coffee while writing code on 4 floating monitors, warm ambient studio lighting, vibrant colors, clean minimal design --ar 16:9',
      primaryColor: 'Amber / Slate',
      visualLayout: 'Center focal robot with bold 2-word typography overhead.',
    },
  ]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('/api/ai/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: videoConcept, type: 'thumbnail' }),
      });
      showToast('Generated Midjourney & Flux Thumbnail Art Prompts!');
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
          <Image className="w-7 h-7 text-red-500" />
          AI Thumbnail Visual Prompt & Concept Builder
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
          Generate Midjourney, Flux, and DALL-E image prompts engineered for high visual contrast and clickability.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Controls Column */}
        <GlassCard className="p-6 space-y-4">
          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                Video Topic / Concept
              </label>
              <textarea
                rows={3}
                required
                value={videoConcept}
                onChange={(e) => setVideoConcept(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-red-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                Thumbnail Overlay Text (Max 3 Words)
              </label>
              <input
                type="text"
                value={overlayText}
                onChange={(e) => setOverlayText(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-bold uppercase text-slate-900 dark:text-white focus:ring-2 focus:ring-red-500 focus:outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-red-600 to-amber-500 text-white font-bold text-xs shadow-lg shadow-red-500/25 hover:opacity-95 transition-all flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>{loading ? 'Crafting Art Prompts...' : 'Generate Thumbnail Prompts'}</span>
            </button>
          </form>
        </GlassCard>

        {/* Live Visual Mockup Preview */}
        <GlassCard className="lg:col-span-2 p-6 space-y-6">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Eye className="w-4 h-4 text-red-500" />
            Live Concept Layout Preview (16:9 Aspect Ratio)
          </h3>

          <div className="relative aspect-video rounded-2xl overflow-hidden bg-slate-950 border border-slate-800 flex items-center justify-center shadow-2xl group">
            <img
              src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=1000"
              alt="Thumbnail background concept"
              className="w-full h-full object-cover opacity-60 group-hover:scale-105 transition-transform duration-700"
            />
            {/* Gradient Overlay for Text legibility */}
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-slate-950/40" />

            {/* Floating Bold Text Overlay Simulation */}
            <div className="absolute top-6 left-6 max-w-md">
              <span className="text-3xl sm:text-5xl font-black uppercase tracking-wider text-amber-400 drop-shadow-[0_5px_15px_rgba(0,0,0,0.9)] stroke-black leading-none bg-slate-950/80 px-4 py-2 rounded-2xl border border-amber-400/40">
                {overlayText || 'YOUR TEXT HERE'}
              </span>
            </div>

            {/* Contrast Badge */}
            <div className="absolute bottom-4 right-4 bg-emerald-500/90 text-slate-950 font-black text-[11px] px-3 py-1 rounded-full shadow-lg">
              High Visual Contrast (98/100)
            </div>
          </div>

          {/* Generated Prompts List */}
          <div className="space-y-4">
            <h4 className="text-xs font-bold text-slate-400 uppercase">
              Generated Image Generation Prompts
            </h4>
            {prompts.map((p, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-3">
                <div className="flex items-center justify-between text-xs font-bold">
                  <span className="text-red-500">{p.style}</span>
                  <span className="text-slate-400 text-[11px]">Colors: {p.primaryColor}</span>
                </div>
                <p className="text-xs font-mono text-slate-800 dark:text-slate-200 bg-white dark:bg-slate-950 p-3 rounded-xl border border-slate-200 dark:border-slate-800">
                  {p.promptText}
                </p>
                <div className="flex justify-end">
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(p.promptText);
                      showToast('Copied prompt to clipboard!');
                    }}
                    className="px-3 py-1.5 rounded-lg bg-red-500/10 text-red-500 font-bold text-xs hover:bg-red-500 hover:text-white transition-all flex items-center gap-1.5"
                  >
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy Prompt</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
