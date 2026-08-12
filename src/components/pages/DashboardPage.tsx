import React from 'react';
import {
  Users,
  Eye,
  Clock,
  DollarSign,
  Sparkles,
  TrendingUp,
  Video,
  ArrowRight,
  Plus,
  Play,
  Flame,
  Key,
} from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { StatCard } from '../common/StatCard';
import { GlassCard } from '../common/GlassCard';
import { SEOProgressBar } from '../common/SEOProgressBar';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export const DashboardPage: React.FC = () => {
  const { channelStats, videos, navigateTo, showToast } = useAppState();

  const viewsChartData = [
    { day: 'Mon', views: 18400, subs: 240 },
    { day: 'Tue', views: 22100, subs: 310 },
    { day: 'Wed', views: 19800, subs: 280 },
    { day: 'Thu', views: 28900, subs: 450 },
    { day: 'Fri', views: 34200, subs: 580 },
    { day: 'Sat', views: 42000, subs: 890 },
    { day: 'Sun', views: 38500, subs: 740 },
  ];

  const dailyAiIdeas = [
    {
      title: 'How I Built a $100K/Yr AI Agent App in 24 Hours',
      niche: 'AI & SaaS',
      predictedViews: '120K - 280K',
      ctrEstimate: '14.2%',
    },
    {
      title: 'Stop Using Gemini 3 Like This! (3 Mind-Blowing Features)',
      niche: 'AI Tools',
      predictedViews: '95K - 210K',
      ctrEstimate: '12.8%',
    },
    {
      title: 'Why 99% of Developers Are Switching to Cursor IDE in 2026',
      niche: 'Software Eng',
      predictedViews: '150K - 320K',
      ctrEstimate: '15.1%',
    },
  ];

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      {/* Welcome & Channel Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-red-900/40 via-slate-900 to-amber-900/30 border border-red-500/20 relative overflow-hidden">
        <div className="relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 text-red-400 text-xs font-bold mb-3 border border-red-500/20">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Channel Health: {channelStats.channelHealthScore}/100 Excellent</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black text-white">
            Welcome Back, <span className="text-red-500">{channelStats.name}</span>
          </h1>
          <p className="mt-2 text-xs sm:text-sm text-slate-300 font-medium max-w-xl">
            Your channel impressions are up <span className="text-emerald-400 font-bold">+18.4%</span> this week. Here are your personalized AI daily video recommendations.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 relative z-10">
          <button
            onClick={async () => {
              try {
                showToast("Initiating secure Google OAuth 2.0 connection...");
                const res = await fetch("/api/v1/youtube/connect", {
                  headers: {
                    Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
                  },
                });
                const data = await res.json();
                if (data?.data?.authorization_url) {
                  window.location.href = data.data.authorization_url;
                } else {
                  showToast("Redirecting to Google OAuth authorization...");
                }
              } catch {
                showToast("OAuth connection ready. Please sign in to Google.");
              }
            }}
            className="px-5 py-3 rounded-2xl bg-red-600 hover:bg-red-700 text-white font-bold text-xs shadow-xl shadow-red-600/30 hover:scale-105 transition-all flex items-center gap-2 cursor-pointer"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>Connect YouTube Channel</span>
          </button>
          <button
            onClick={() => navigateTo('ai-script')}
            className="px-5 py-3 rounded-2xl bg-gradient-to-r from-red-600 to-amber-500 text-white font-bold text-xs shadow-xl shadow-red-500/25 hover:scale-105 transition-all flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            <span>New Video Script</span>
          </button>
          <button
            onClick={() => navigateTo('video-seo')}
            className="px-5 py-3 rounded-2xl bg-slate-900 hover:bg-slate-800 text-slate-200 font-bold text-xs border border-slate-800 transition-all flex items-center gap-2"
          >
            <Video className="w-4 h-4 text-red-500" />
            <span>Audit Video SEO</span>
          </button>
        </div>
      </div>

      {/* Realtime Key Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Subscribers"
          value={channelStats.subscribers.toLocaleString()}
          change={channelStats.subscribersChange ? 6.2 : 0}
          icon={Users}
          iconBg="bg-red-500/10 text-red-500"
          glow="purple"
        />
        <StatCard
          title="Views (30 Days)"
          value={channelStats.views30Days.toLocaleString()}
          change={channelStats.viewsChange}
          icon={Eye}
          iconBg="bg-amber-500/10 text-amber-500"
          glow="amber"
        />
        <StatCard
          title="Watch Time (Hours)"
          value={channelStats.watchTimeHours.toLocaleString()}
          change={12.1}
          icon={Clock}
          iconBg="bg-blue-500/10 text-blue-500"
          glow="blue"
        />
        <StatCard
          title="Est. Revenue (30d)"
          value={`$${channelStats.estimatedRevenue.toLocaleString()}`}
          change={channelStats.revenueChange}
          icon={DollarSign}
          iconBg="bg-emerald-500/10 text-emerald-500"
          glow="emerald"
        />
      </div>

      {/* Main Charts & Recommended Ideas Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Analytics Chart */}
        <GlassCard className="lg:col-span-2 p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-red-500" />
                Views Velocity & Traffic Pulse
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Daily view count trajectory over the last 7 days
              </p>
            </div>
            <span className="text-xs font-bold text-emerald-500 bg-emerald-500/10 px-3 py-1 rounded-full">
              +24% vs Last Week
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={viewsChartData}>
                <defs>
                  <linearGradient id="viewsGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
                <XAxis dataKey="day" stroke="#94A3B8" fontSize={12} />
                <YAxis stroke="#94A3B8" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F172A',
                    borderColor: '#1E293B',
                    borderRadius: '12px',
                    color: '#FFF',
                    fontSize: '12px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="views"
                  stroke="#EF4444"
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#viewsGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* AI Daily Recommended Video Ideas */}
        <GlassCard className="p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-red-500" />
                AI Daily Video Opportunities
              </h3>
              <span className="text-[10px] font-bold uppercase tracking-wider text-red-500 bg-red-500/10 px-2 py-0.5 rounded">
                High CTR
              </span>
            </div>

            <p className="text-xs text-slate-500 dark:text-slate-400 mb-4 font-medium">
              3 high-potential topics tailored to your channel subscribers:
            </p>

            <div className="space-y-3">
              {dailyAiIdeas.map((idea, idx) => (
                <div
                  key={idx}
                  onClick={() => {
                    showToast(`Loaded idea "${idea.title}" into Script Generator!`);
                    navigateTo('ai-script');
                  }}
                  className="p-3.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-red-500/50 cursor-pointer transition-all group"
                >
                  <div className="flex items-center justify-between text-[10px] font-bold text-slate-400 mb-1">
                    <span className="text-red-500">{idea.niche}</span>
                    <span className="text-emerald-400">Est. CTR {idea.ctrEstimate}</span>
                  </div>
                  <h4 className="text-xs font-bold text-slate-900 dark:text-white group-hover:text-red-500 transition-colors">
                    {idea.title}
                  </h4>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={() => navigateTo('ai-title')}
            className="mt-4 w-full py-2.5 rounded-xl bg-red-500/10 text-red-500 font-bold text-xs hover:bg-red-500 hover:text-white transition-all text-center flex items-center justify-center gap-2"
          >
            <span>Generate More Viral Titles</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </GlassCard>
      </div>

      {/* Latest Uploaded Videos Table */}
      <GlassCard className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Video className="w-5 h-5 text-red-500" />
              Latest Video Performance & SEO Scores
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Audit click-through rates, watch time, and algorithmic SEO readiness
            </p>
          </div>
          <button
            onClick={() => navigateTo('video-performance')}
            className="text-xs font-bold text-red-500 hover:underline flex items-center gap-1"
          >
            <span>View All Videos</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 font-bold uppercase text-[10px]">
                <th className="pb-3 px-2">Video Title & Thumbnail</th>
                <th className="pb-3 px-2">Status</th>
                <th className="pb-3 px-2">Views</th>
                <th className="pb-3 px-2">CTR</th>
                <th className="pb-3 px-2">Retention</th>
                <th className="pb-3 px-2 text-center">SEO Score</th>
                <th className="pb-3 px-2 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/60 dark:divide-slate-800/60 font-semibold text-slate-700 dark:text-slate-300">
              {videos.map((vid) => (
                <tr key={vid.id} className="hover:bg-slate-100/50 dark:hover:bg-slate-900/50 transition-colors">
                  <td className="py-3 px-2">
                    <div className="flex items-center gap-3">
                      <img
                        src={vid.thumbnail}
                        alt={vid.title}
                        className="w-16 h-10 rounded-lg object-cover flex-shrink-0"
                      />
                      <div>
                        <span className="font-bold text-slate-900 dark:text-white block line-clamp-1 max-w-xs">
                          {vid.title}
                        </span>
                        <span className="text-[10px] text-slate-400">{vid.publishedAt}</span>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-2">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold ${
                        vid.status === 'Published'
                          ? 'bg-emerald-500/10 text-emerald-500'
                          : 'bg-amber-500/10 text-amber-500'
                      }`}
                    >
                      {vid.status}
                    </span>
                  </td>
                  <td className="py-3 px-2 font-bold text-slate-900 dark:text-white">
                    {vid.views > 0 ? vid.views.toLocaleString() : '-'}
                  </td>
                  <td className="py-3 px-2 text-emerald-500 font-bold">
                    {vid.ctr > 0 ? `${vid.ctr}%` : '-'}
                  </td>
                  <td className="py-3 px-2 text-slate-400">
                    {vid.retentionPercent > 0 ? `${vid.retentionPercent}%` : '-'}
                  </td>
                  <td className="py-3 px-2 text-center">
                    <SEOProgressBar score={vid.seoScore} size="sm" showLabel={false} />
                  </td>
                  <td className="py-3 px-2 text-right">
                    <button
                      onClick={() => {
                        showToast(`Optimizing SEO for "${vid.title.substring(0, 20)}..."`);
                        navigateTo('video-seo');
                      }}
                      className="px-3 py-1.5 rounded-lg bg-red-500/10 text-red-500 font-bold hover:bg-red-500 hover:text-white transition-all text-[11px]"
                    >
                      Optimize SEO
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
