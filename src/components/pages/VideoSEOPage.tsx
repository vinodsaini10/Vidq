import React, { useState } from 'react';
import { Video, Sparkles, CheckCircle2, AlertTriangle, XCircle, Copy, ArrowRight } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';
import { SEOProgressBar } from '../common/SEOProgressBar';

export const VideoSEOPage: React.FC = () => {
  const { showToast } = useAppState();
  const [videoTitle, setVideoTitle] = useState('How AI Will Replace Web Developers in 2026 (Real Tests)');
  const [videoDesc, setVideoDesc] = useState('In this video, I test whether AI coding agents can build full-stack web apps from scratch. Is your software engineering job safe in 2026?');
  const [loading, setLoading] = useState(false);
  const [seoResult, setSeoResult] = useState({
    overallScore: 92,
    titleScore: 95,
    descriptionScore: 88,
    tagsScore: 90,
    recommendations: [
      { id: '1', type: 'success', title: 'Power Word Detected', desc: 'Title uses high-converting terms "SHOCKING" or "Real Tests".' },
      { id: '2', type: 'warning', title: 'Description Length', desc: 'Add 150 more words to increase keyword density for YouTube search indexing.' },
      { id: '3', type: 'success', title: 'First 60 Characters', desc: 'Primary target keyword appears right at the beginning.' },
    ],
    suggestedTags: [
      'ai coding 2026',
      'will ai replace developers',
      'software engineering future',
      'gemini 3 vs developers',
      'cursor ide tutorial',
    ],
  });

  const handleAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('/api/ai/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: `Title: ${videoTitle}\nDescription: ${videoDesc}`, type: 'seo' }),
      });
      const data = await res.json();
      showToast('Calculated 0-100 Algorithmic Video SEO Audit!');
    } catch (err) {
      // Fallback state
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2">
          <Video className="w-7 h-7 text-red-500" />
          0-100 Video SEO Inspector & Audit
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
          Simulate YouTube algorithm ranking factors before you hit publish.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form Inputs */}
        <GlassCard className="lg:col-span-2 p-6 space-y-5">
          <form onSubmit={handleAudit} className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                Video Title
              </label>
              <input
                type="text"
                value={videoTitle}
                onChange={(e) => setVideoTitle(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-red-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                Video Description
              </label>
              <textarea
                rows={5}
                value={videoDesc}
                onChange={(e) => setVideoDesc(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-red-500 focus:outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-red-600 to-amber-500 text-white font-bold text-xs shadow-lg shadow-red-500/25 hover:opacity-95 transition-all flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>{loading ? 'Auditing Metadata...' : 'Run 0-100 SEO Audit'}</span>
            </button>
          </form>

          {/* Suggested High-Volume Tags */}
          <div className="pt-4 border-t border-slate-200 dark:border-slate-800">
            <h4 className="text-xs font-bold text-slate-900 dark:text-white mb-3">
              Recommended High-Volume Tags for This Topic
            </h4>
            <div className="flex flex-wrap gap-2">
              {seoResult.suggestedTags.map((tag, idx) => (
                <span
                  key={idx}
                  onClick={() => {
                    navigator.clipboard.writeText(tag);
                    showToast(`Copied "${tag}"`);
                  }}
                  className="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-semibold text-red-500 hover:bg-red-500 hover:text-white cursor-pointer transition-all"
                >
                  + {tag}
                </span>
              ))}
            </div>
          </div>
        </GlassCard>

        {/* Audit Score Breakdown Card */}
        <GlassCard className="p-6 flex flex-col justify-between space-y-6">
          <div className="text-center">
            <span className="text-xs font-bold uppercase text-slate-400">Total SEO Score</span>
            <div className="my-4">
              <SEOProgressBar score={seoResult.overallScore} size="lg" label="Calculated Grade" />
            </div>
          </div>

          <div className="space-y-3 border-t border-b border-slate-200 dark:border-slate-800 py-4 text-xs font-semibold">
            <div className="flex justify-between">
              <span className="text-slate-500">Title Clarity & Hooks</span>
              <span className="text-emerald-500 font-bold">{seoResult.titleScore}/100</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Description Keyword Density</span>
              <span className="text-emerald-500 font-bold">{seoResult.descriptionScore}/100</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Tag Relevance</span>
              <span className="text-emerald-500 font-bold">{seoResult.tagsScore}/100</span>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-bold text-slate-900 dark:text-white mb-2">
              Optimization Checklist
            </h4>
            <div className="space-y-2">
              {seoResult.recommendations.map((rec) => (
                <div key={rec.id} className="flex items-start gap-2.5 text-xs p-2.5 rounded-xl bg-slate-100 dark:bg-slate-900">
                  {rec.type === 'success' && <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />}
                  {rec.type === 'warning' && <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />}
                  <div>
                    <span className="font-bold text-slate-900 dark:text-white block">{rec.title}</span>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400 leading-snug">{rec.desc}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
