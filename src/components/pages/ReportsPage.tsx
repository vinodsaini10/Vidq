import React from 'react';
import { FileSpreadsheet, Download, Sparkles, TrendingUp, BarChart3, CheckCircle2 } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const ReportsPage: React.FC = () => {
  const { channelStats, showToast } = useAppState();

  const handleDownload = (reportName: string) => {
    showToast(`Generating & downloading ${reportName}...`);
  };

  const reports = [
    {
      title: '30-Day Channel Health & Revenue Audit',
      date: 'May 2025 Audit',
      type: 'PDF Executive Summary',
      size: '2.4 MB',
      description: 'Comprehensive analysis of CTR trends, subscriber conversion rates, and RPM revenue optimizations.',
    },
    {
      title: 'Competitor Gap & Content Velocity Analysis',
      date: 'Weekly Snapshot',
      type: 'CSV Data Export',
      size: '1.1 MB',
      description: 'Breakdown of competitor views per hour, top outlier videos in your niche, and missing target keywords.',
    },
    {
      title: 'Video SEO Scorecard & Optimization Log',
      date: 'Lifetime Archive',
      type: 'PDF Detailed Report',
      size: '4.8 MB',
      description: 'Full list of top 20 published videos with title CTR grades, tag density, and AI title recommendations.',
    },
  ];

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2">
          <FileSpreadsheet className="w-7 h-7 text-emerald-500" />
          PDF Growth & Revenue Reports
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
          Export executive-level YouTube performance audits, revenue breakdown PDFs, and keyword intelligence spreadsheets.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlassCard className="p-6 space-y-2 border-emerald-500/30">
          <span className="text-xs font-bold text-slate-400">Total Revenue Audited</span>
          <div className="text-2xl font-black text-emerald-400">${channelStats.estimatedRevenue.toLocaleString()}</div>
          <p className="text-[11px] text-emerald-500 font-bold flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" /> +18.4% vs last month
          </p>
        </GlassCard>

        <GlassCard className="p-6 space-y-2">
          <span className="text-xs font-bold text-slate-400">Channel Health Score</span>
          <div className="text-2xl font-black text-slate-900 dark:text-white">{channelStats.channelHealthScore}/100</div>
          <p className="text-[11px] text-slate-500 font-semibold">Top 5% in {channelStats.topNiche}</p>
        </GlassCard>

        <GlassCard className="p-6 space-y-2">
          <span className="text-xs font-bold text-slate-400">Monthly Impressions</span>
          <div className="text-2xl font-black text-red-500">1.8M</div>
          <p className="text-[11px] text-slate-500 font-semibold">Avg CTR: {channelStats.avgCtr}%</p>
        </GlassCard>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-extrabold text-slate-900 dark:text-white">Available Growth Reports</h3>

        <div className="space-y-4">
          {reports.map((rep, idx) => (
            <GlassCard key={idx} className="p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="space-y-1 max-w-2xl">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-black uppercase tracking-wider text-emerald-500 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
                    {rep.type}
                  </span>
                  <span className="text-xs text-slate-400 font-bold">{rep.date} • {rep.size}</span>
                </div>
                <h4 className="text-base font-black text-slate-900 dark:text-white">{rep.title}</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">{rep.description}</p>
              </div>

              <button
                onClick={() => handleDownload(rep.title)}
                className="px-5 py-2.5 rounded-xl bg-emerald-500 text-slate-950 font-black text-xs hover:bg-emerald-400 transition-all flex items-center gap-2 shadow-lg shadow-emerald-500/20 self-start md:self-auto"
              >
                <Download className="w-4 h-4" />
                <span>Export Audit PDF</span>
              </button>
            </GlassCard>
          ))}
        </div>
      </div>
    </div>
  );
};
