import React, { useState } from 'react';
import { BarChart3, TrendingUp, Eye, Clock, DollarSign, Users, Calendar, Filter } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

export const AnalyticsPage: React.FC = () => {
  const { channelStats } = useAppState();
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '365d'>('30d');

  const monthlyGrowthData = [
    { month: 'Jan', views: 420000, revenue: 2800, subs: 4200 },
    { month: 'Feb', views: 490000, revenue: 3400, subs: 5100 },
    { month: 'Mar', views: 540000, revenue: 3900, subs: 6200 },
    { month: 'Apr', views: 610000, revenue: 4300, subs: 7100 },
    { month: 'May', views: 580000, revenue: 4100, subs: 6800 },
    { month: 'Jun', views: 680000, revenue: 4890, subs: 8400 },
  ];

  const trafficSourceData = [
    { name: 'YouTube Recommendation / Home', value: 58, color: '#EF4444' },
    { name: 'YouTube Search / SEO', value: 24, color: '#F59E0B' },
    { name: 'External / Google Search', value: 10, color: '#3B82F6' },
    { name: 'Direct / Channel Page', value: 8, color: '#10B981' },
  ];

  const demographicsData = [
    { age: '18-24', pct: 28 },
    { age: '25-34', pct: 46 },
    { age: '35-44', pct: 18 },
    { age: '45+', pct: 8 },
  ];

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2">
            <BarChart3 className="w-7 h-7 text-red-500" />
            Deep Channel Analytics
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
            Granular views, subscriber acquisition velocity, traffic origins, and revenue benchmarks.
          </p>
        </div>

        {/* Time Filter */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          {(['7d', '30d', '90d', '365d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                timeRange === range
                  ? 'bg-red-500 text-white shadow-md'
                  : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              {range.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Analytics Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <GlassCard className="p-5">
          <span className="text-xs font-bold text-slate-400">Monthly Views</span>
          <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-1">
            {channelStats.views30Days.toLocaleString()}
          </h3>
          <span className="text-xs text-emerald-500 font-bold mt-2 block">
            +{channelStats.viewsChange}% vs previous month
          </span>
        </GlassCard>

        <GlassCard className="p-5">
          <span className="text-xs font-bold text-slate-400">Subscribers Gained</span>
          <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-1">
            +{channelStats.subscribersChange.toLocaleString()}
          </h3>
          <span className="text-xs text-emerald-500 font-bold mt-2 block">+14.2% velocity</span>
        </GlassCard>

        <GlassCard className="p-5">
          <span className="text-xs font-bold text-slate-400">Avg Click-Through Rate</span>
          <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-1">
            {channelStats.avgCtr}%
          </h3>
          <span className="text-xs text-emerald-500 font-bold mt-2 block">Top 5% in Tech Niche</span>
        </GlassCard>

        <GlassCard className="p-5">
          <span className="text-xs font-bold text-slate-400">CPM Revenue</span>
          <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-1">
            ${channelStats.estimatedRevenue.toLocaleString()}
          </h3>
          <span className="text-xs text-emerald-500 font-bold mt-2 block">Avg RPM: $7.19</span>
        </GlassCard>
      </div>

      {/* Main Revenue & Views Area Chart */}
      <GlassCard className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-base font-bold text-slate-900 dark:text-white">
            Views & Estimated AdSense Revenue Trajectory
          </h3>
          <div className="flex items-center gap-4 text-xs font-bold">
            <span className="flex items-center gap-1.5 text-red-500">
              <span className="w-3 h-3 rounded-full bg-red-500" /> Views
            </span>
            <span className="flex items-center gap-1.5 text-amber-500">
              <span className="w-3 h-3 rounded-full bg-amber-500" /> Revenue ($)
            </span>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={monthlyGrowthData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
              <XAxis dataKey="month" stroke="#94A3B8" fontSize={12} />
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
              <Area type="monotone" dataKey="views" stroke="#EF4444" fill="#EF4444" fillOpacity={0.2} strokeWidth={2} />
              <Area type="monotone" dataKey="revenue" stroke="#F59E0B" fill="#F59E0B" fillOpacity={0.2} strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </GlassCard>

      {/* Traffic Sources & Audience Demographics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <GlassCard className="p-6">
          <h3 className="text-base font-bold text-slate-900 dark:text-white mb-4">
            Traffic Source Breakdown
          </h3>
          <div className="h-60 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={trafficSourceData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={50}
                  paddingAngle={5}
                >
                  {trafficSourceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2 mt-4">
            {trafficSourceData.map((src, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs font-medium">
                <span className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: src.color }} />
                  <span className="text-slate-700 dark:text-slate-300">{src.name}</span>
                </span>
                <span className="font-bold text-slate-900 dark:text-white">{src.value}%</span>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <h3 className="text-base font-bold text-slate-900 dark:text-white mb-4">
            Audience Age Distribution
          </h3>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={demographicsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
                <XAxis dataKey="age" stroke="#94A3B8" fontSize={12} />
                <YAxis stroke="#94A3B8" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F172A',
                    borderColor: '#1E293B',
                    borderRadius: '12px',
                    color: '#FFF',
                  }}
                />
                <Bar dataKey="pct" fill="#EF4444" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
