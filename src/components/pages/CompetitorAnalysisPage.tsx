import React from 'react';
import { Users, Flame, TrendingUp, Sparkles, ArrowUpRight } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const CompetitorAnalysisPage: React.FC = () => {
  const { competitors, showToast } = useAppState();

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2">
          <Users className="w-7 h-7 text-red-500" />
          Competitor Intelligence & Outlier Video Radar
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
          Track rival channel posting velocity, spot 15x view outlier videos, and exploit untapped content gaps.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {competitors.map((comp) => (
          <GlassCard key={comp.id} className="p-6 space-y-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-3 pb-4 border-b border-slate-200 dark:border-slate-800">
                <img
                  src={comp.avatar}
                  alt={comp.name}
                  className="w-12 h-12 rounded-2xl object-cover ring-2 ring-red-500/30"
                />
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">{comp.name}</h3>
                  <span className="text-xs text-red-500 font-semibold">{comp.handle}</span>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    {(comp.subscribers / 1000).toFixed(0)}k Subs · {comp.uploadFrequency}
                  </p>
                </div>
              </div>

              {/* Outlier Video Alert */}
              <div className="my-4 p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 space-y-1">
                <div className="flex items-center justify-between text-[10px] font-bold text-amber-500">
                  <span className="flex items-center gap-1">
                    <Flame className="w-3.5 h-3.5" />
                    Viral Outlier Video
                  </span>
                  <span>{comp.outlierVideo.multiplier}</span>
                </div>
                <h4 className="text-xs font-bold text-slate-900 dark:text-white line-clamp-2">
                  "{comp.outlierVideo.title}"
                </h4>
                <span className="text-[10px] text-slate-400 font-bold block">
                  {comp.outlierVideo.views.toLocaleString()} views
                </span>
              </div>

              <div>
                <span className="text-[10px] font-bold uppercase text-slate-400 block mb-1">
                  Untapped Content Gap:
                </span>
                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-100 dark:bg-slate-900 p-3 rounded-xl border border-slate-200 dark:border-slate-800">
                  {comp.contentGap}
                </p>
              </div>
            </div>

            <button
              onClick={() => showToast(`Creating script response to "${comp.outlierVideo.title.substring(0, 20)}..."`)}
              className="mt-4 w-full py-2.5 rounded-xl bg-red-500/10 text-red-500 font-bold text-xs hover:bg-red-500 hover:text-white transition-all text-center flex items-center justify-center gap-2"
            >
              <span>Create Answer Video</span>
              <ArrowUpRight className="w-4 h-4" />
            </button>
          </GlassCard>
        ))}
      </div>
    </div>
  );
};
