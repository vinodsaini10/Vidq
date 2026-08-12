import React from 'react';
import { Sparkles, Video, Key, Flame, Users, FileText, Image, BarChart3, ArrowRight } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const FeaturesPage: React.FC = () => {
  const { navigateTo } = useAppState();

  const featureList = [
    {
      id: 'ai-script',
      title: 'AI Script Generator',
      icon: FileText,
      desc: 'Generates multi-section scripts with retention-optimized opening hooks, visual cues, and strong CTAs.',
      page: 'ai-script' as const,
    },
    {
      id: 'video-seo',
      title: '0-100 Video SEO Inspector',
      icon: Video,
      desc: 'Calculates real-time algorithmic SEO scores and gives targeted advice to improve title and description ranking.',
      page: 'video-seo' as const,
    },
    {
      id: 'ai-title',
      title: 'AI Viral Title Generator',
      icon: Sparkles,
      desc: 'Produces high-CTR titles categorized by psychological triggers (Curiosity, Urgency, Storytelling).',
      page: 'ai-title' as const,
    },
    {
      id: 'thumbnail-prompts',
      title: 'Thumbnail Visual Prompts',
      icon: Image,
      desc: 'Outputs custom visual prompts for Midjourney, Flux, and DALL-E with typography contrast layouts.',
      page: 'thumbnail-prompts' as const,
    },
    {
      id: 'keyword-research',
      title: 'Keyword Explorer 2.0',
      icon: Key,
      desc: 'Discovers high search volume, low competition tags with estimated CPM and keyword difficulty scores.',
      page: 'keyword-research' as const,
    },
    {
      id: 'trends',
      title: 'Breakout Trend Radar',
      icon: Flame,
      desc: 'Detects trending topics in your niche 48 hours early before they get saturated by competitors.',
      page: 'trends' as const,
    },
    {
      id: 'competitors',
      title: 'Competitor Intelligence',
      icon: Users,
      desc: 'Track rival upload rates, analyze outlier viral videos, and steal untapped content gaps.',
      page: 'competitors' as const,
    },
    {
      id: 'analytics',
      title: 'Deep Channel Analytics',
      icon: BarChart3,
      desc: 'Realtime subscriber velocity charts, view breakdowns, and estimated revenue forecasts.',
      page: 'analytics' as const,
    },
  ];

  return (
    <div className="min-h-screen py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <h1 className="text-4xl sm:text-6xl font-black text-slate-900 dark:text-white">
          The Complete AI Suite for <br />
          <span className="bg-gradient-to-r from-red-500 via-rose-400 to-amber-400 bg-clip-text text-transparent">
            YouTube Content Creation
          </span>
        </h1>
        <p className="mt-4 text-slate-600 dark:text-slate-400 font-medium text-base">
          Explore our full ecosystem of AI tools designed to automate research, scripting, and optimization.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {featureList.map((f) => {
          const Icon = f.icon;
          return (
            <GlassCard key={f.id} className="flex flex-col justify-between group">
              <div>
                <div className="p-3 rounded-xl bg-red-500/10 text-red-500 w-fit mb-4 group-hover:scale-110 transition-transform">
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">{f.title}</h3>
                <p className="mt-2 text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-medium">
                  {f.desc}
                </p>
              </div>

              <button
                onClick={() => navigateTo(f.page)}
                className="mt-6 flex items-center gap-2 text-xs font-bold text-red-500 hover:text-red-600 transition-colors"
              >
                <span>Try Tool Now</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </GlassCard>
          );
        })}
      </div>
    </div>
  );
};
