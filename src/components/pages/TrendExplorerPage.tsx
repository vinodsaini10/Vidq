import React from 'react';
import { Flame, Sparkles, TrendingUp, ArrowRight, Zap } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const TrendExplorerPage: React.FC = () => {
  const { trends, navigateTo, showToast } = useAppState();

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2">
          <Flame className="w-7 h-7 text-amber-500 animate-pulse" />
          Breakout Viral Trend Radar
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
          Detect explosive breakout search topics 48 hours early with real-time velocity scores and search volume spikes.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {trends.map((t) => (
          <GlassCard key={t.id} className="p-6 space-y-4 hover:border-amber-500/50 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-xs font-extrabold uppercase tracking-wider text-amber-500 bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20">
                {t.niche}
              </span>
              <span className="text-xs font-black text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full">
                {t.searchVolumeGrowth}
              </span>
            </div>

            <div>
              <h3 className="text-xl font-black text-slate-900 dark:text-white">{t.topic}</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Top viral example: "{t.topVideoExample}"
              </p>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-slate-200 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-400">Velocity Score:</span>
                <span className="text-sm font-black text-red-500">{t.velocityScore}/100</span>
              </div>

              <button
                onClick={() => {
                  showToast(`Creating script for trend "${t.topic}"`);
                  navigateTo('ai-script');
                }}
                className="px-4 py-2 rounded-xl bg-amber-500 text-slate-950 font-black text-xs hover:bg-amber-400 transition-all flex items-center gap-1.5 shadow-lg shadow-amber-500/20"
              >
                <span>Jump On Trend</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </GlassCard>
        ))}
      </div>
    </div>
  );
};
