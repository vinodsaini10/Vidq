import React, { useState } from 'react';
import { Key, Search, Sparkles, TrendingUp, DollarSign, Award, ArrowRight, Copy } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';
import { SEOProgressBar } from '../common/SEOProgressBar';

export const KeywordResearchPage: React.FC = () => {
  const { keywords, showToast } = useAppState();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedKeyword, setSelectedKeyword] = useState(keywords[0]);
  const [searching, setSearching] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;
    setSearching(true);
    setTimeout(() => {
      setSearching(false);
      showToast(`Analyzed keyword "${searchTerm}"`);
    }, 800);
  };

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2">
          <Key className="w-7 h-7 text-amber-500" />
          Keyword Research & Opportunity Inspector
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
          Discover high-CPM, low-competition tags, search intent breakdown, and competitor SERP ranking difficulty.
        </p>
      </div>

      {/* Search Input Bar */}
      <GlassCard className="p-4 sm:p-6">
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Enter seed keyword e.g. 'faceless youtube automation' or 'gemini 3.5 coding'"
              className="w-full pl-12 pr-4 py-3.5 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-sm font-medium focus:ring-2 focus:ring-amber-500 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={searching}
            className="px-8 py-3.5 rounded-2xl bg-gradient-to-r from-amber-500 to-orange-600 text-slate-950 font-black text-sm shadow-xl shadow-amber-500/20 hover:opacity-95 transition-all flex items-center justify-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            <span>{searching ? 'Analyzing...' : 'Search Volume & CPM'}</span>
          </button>
        </form>
      </GlassCard>

      {/* Selected Keyword Details Grid */}
      {selectedKeyword && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <GlassCard className="p-6 flex flex-col items-center text-center justify-between">
            <div>
              <span className="text-xs font-extrabold uppercase text-amber-500 tracking-wider">
                Overall Keyword Score
              </span>
              <h2 className="text-xl font-black text-slate-900 dark:text-white mt-1">
                "{selectedKeyword.keyword}"
              </h2>
              <div className="my-6">
                <SEOProgressBar score={selectedKeyword.overallScore} size="lg" label="Opportunity Score" />
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                Higher scores indicate high search interest combined with low competitor video saturation.
              </p>
            </div>

            <button
              onClick={() => {
                navigator.clipboard.writeText(selectedKeyword.keyword);
                showToast(`Copied "${selectedKeyword.keyword}" to clipboard!`);
              }}
              className="mt-6 w-full py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white font-bold text-xs flex items-center justify-center gap-2"
            >
              <Copy className="w-4 h-4" />
              <span>Copy Keyword</span>
            </button>
          </GlassCard>

          <GlassCard className="lg:col-span-2 p-6 space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-4 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="text-[10px] font-bold uppercase text-slate-400 block">Search Volume</span>
                <span className="text-lg font-black text-slate-900 dark:text-white mt-1 block">
                  {selectedKeyword.searchVolume.toLocaleString()}/mo
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="text-[10px] font-bold uppercase text-slate-400 block">Competition</span>
                <span className="text-lg font-black text-amber-500 mt-1 block">
                  {selectedKeyword.competition}
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="text-[10px] font-bold uppercase text-slate-400 block">Est. CPM</span>
                <span className="text-lg font-black text-emerald-500 mt-1 block">
                  {selectedKeyword.cpmEstimate}
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="text-[10px] font-bold uppercase text-slate-400 block">Trend Growth</span>
                <span className="text-lg font-black text-red-500 mt-1 block">
                  +{selectedKeyword.trendPercentage}%
                </span>
              </div>
            </div>

            <div>
              <h4 className="text-xs font-bold uppercase text-slate-400 mb-3">
                Related Low-Competition Keywords
              </h4>
              <div className="flex flex-wrap gap-2">
                {selectedKeyword.relatedKeywords.map((rel, idx) => (
                  <span
                    key={idx}
                    onClick={() => showToast(`Copied tag "${rel}"`)}
                    className="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:border-amber-500 cursor-pointer transition-colors"
                  >
                    + {rel}
                  </span>
                ))}
              </div>
            </div>
          </GlassCard>
        </div>
      )}

      {/* Keywords Table */}
      <GlassCard className="p-6">
        <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">
          Trending Niche Seed Keywords
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 font-bold uppercase text-[10px]">
                <th className="pb-3 px-2">Keyword Phrase</th>
                <th className="pb-3 px-2">Search Volume</th>
                <th className="pb-3 px-2">Competition</th>
                <th className="pb-3 px-2">Est. CPM</th>
                <th className="pb-3 px-2 text-center">Score</th>
                <th className="pb-3 px-2 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/60 dark:divide-slate-800/60 font-semibold text-slate-700 dark:text-slate-300">
              {keywords.map((kw, idx) => (
                <tr key={idx} className="hover:bg-slate-100/50 dark:hover:bg-slate-900/50 transition-colors">
                  <td className="py-3 px-2 font-bold text-slate-900 dark:text-white">{kw.keyword}</td>
                  <td className="py-3 px-2">{kw.searchVolume.toLocaleString()}/mo</td>
                  <td className="py-3 px-2 text-amber-500">{kw.competition}</td>
                  <td className="py-3 px-2 text-emerald-500 font-bold">{kw.cpmEstimate}</td>
                  <td className="py-3 px-2 text-center">
                    <SEOProgressBar score={kw.overallScore} size="sm" showLabel={false} />
                  </td>
                  <td className="py-3 px-2 text-right">
                    <button
                      onClick={() => setSelectedKeyword(kw)}
                      className="px-3 py-1.5 rounded-lg bg-amber-500/10 text-amber-500 font-bold hover:bg-amber-500 hover:text-slate-950 transition-all text-[11px]"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
};
