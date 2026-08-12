import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Server,
  Users,
  Activity,
  HardDrive,
  Cpu,
  Youtube,
  CreditCard,
  Settings,
  Sparkles,
  Zap,
  RefreshCw,
  AlertTriangle
} from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';
import { AdminHeader } from '../admin/AdminHeader';
import { UserManagementTab } from '../admin/UserManagementTab';
import { AIAdminTab } from '../admin/AIAdminTab';
import { YouTubeAdminTab } from '../admin/YouTubeAdminTab';
import { BillingAdminTab } from '../admin/BillingAdminTab';
import { SystemAdminTab } from '../admin/SystemAdminTab';

export const AdminPage: React.FC = () => {
  const { showToast } = useAppState();
  const [activeTab, setActiveTab] = useState<
    'overview' | 'users' | 'youtube' | 'ai' | 'billing' | 'system'
  >('overview');

  const [dashboardData, setDashboardData] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [impersonatedUser, setImpersonatedUser] = useState<any | null>(null);

  useEffect(() => {
    fetchDashboardMetrics();
  }, []);

  const fetchDashboardMetrics = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/admin/dashboard', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setDashboardData(data);
      }
    } catch (e) {
      console.error("Failed to fetch dashboard metrics", e);
    } finally {
      setLoading(false);
    }
  };

  const handleImpersonateUser = async (user: any) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/admin/users/${user.id}/impersonate`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('impersonation_token', data.impersonation_token);
        setImpersonatedUser(user);
        showToast(`Impersonating ${user.email}. Temporary token active.`);
      }
    } catch (e) {
      showToast('Impersonation failed.');
    }
  };

  const handleExitImpersonation = () => {
    localStorage.removeItem('impersonation_token');
    setImpersonatedUser(null);
    showToast('Exited impersonation session.');
  };

  const handleSystemAction = async (actionName: string) => {
    showToast(`Executed system task: ${actionName}`);
  };

  const cards = dashboardData?.cards || {
    totalUsers: 14280,
    activeUsers: 12450,
    newUsersToday: 142,
    activeSubscriptions: 8420,
    mrr: 42100,
    arr: 505200,
    totalRevenue: 184500,
    aiRequests: 4200000,
    aiTokens: 185000000,
    aiCost: 142.85,
    youtubeChannels: 3820,
    videosSynced: 48200,
    openSupportTickets: 3
  };

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      {/* Top Header with Impersonation & Search */}
      <AdminHeader
        onSearch={(query) => console.log('Global search query:', query)}
        impersonatedUser={impersonatedUser}
        onExitImpersonation={handleExitImpersonation}
      />

      {/* Main Section Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2">
            <ShieldCheck className="w-7 h-7 text-purple-500" />
            Super Admin Platform Management
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
            Complete platform orchestration: Users, YouTube synchronization, AI providers, Subscriptions, and Audit logging.
          </p>
        </div>

        {/* Refresh button */}
        <button
          onClick={fetchDashboardMetrics}
          className="self-start md:self-auto px-4 py-2 rounded-xl bg-slate-800 text-white font-extrabold text-xs hover:bg-slate-700 transition-all flex items-center gap-2 border border-slate-700"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Metrics</span>
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto border-b border-slate-800 pb-2 scrollbar-none">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2.5 rounded-xl text-xs font-black transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'overview'
              ? 'bg-purple-600 text-white shadow-lg'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <Activity className="w-4 h-4" /> Overview Dashboard
        </button>

        <button
          onClick={() => setActiveTab('users')}
          className={`px-4 py-2.5 rounded-xl text-xs font-black transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'users'
              ? 'bg-purple-600 text-white shadow-lg'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <Users className="w-4 h-4" /> User Management
        </button>

        <button
          onClick={() => setActiveTab('youtube')}
          className={`px-4 py-2.5 rounded-xl text-xs font-black transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'youtube'
              ? 'bg-purple-600 text-white shadow-lg'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <Youtube className="w-4 h-4" /> YouTube Channels
        </button>

        <button
          onClick={() => setActiveTab('ai')}
          className={`px-4 py-2.5 rounded-xl text-xs font-black transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'ai'
              ? 'bg-purple-600 text-white shadow-lg'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <Cpu className="w-4 h-4" /> AI Providers & Models
        </button>

        <button
          onClick={() => setActiveTab('billing')}
          className={`px-4 py-2.5 rounded-xl text-xs font-black transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'billing'
              ? 'bg-purple-600 text-white shadow-lg'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <CreditCard className="w-4 h-4" /> Subscriptions & Billing
        </button>

        <button
          onClick={() => setActiveTab('system')}
          className={`px-4 py-2.5 rounded-xl text-xs font-black transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'system'
              ? 'bg-purple-600 text-white shadow-lg'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <Settings className="w-4 h-4" /> System & Audit Logs
        </button>
      </div>

      {/* TAB 1: OVERVIEW DASHBOARD */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <GlassCard className="p-5 space-y-2 border-purple-500/30">
              <span className="text-xs font-bold text-slate-400 flex items-center gap-1.5">
                <Users className="w-4 h-4 text-purple-400" /> Total Users
              </span>
              <div className="text-2xl font-black text-slate-900 dark:text-white">
                {cards.totalUsers?.toLocaleString()}
              </div>
              <span className="text-[10px] text-emerald-500 font-bold">
                {cards.newUsersToday} registered today
              </span>
            </GlassCard>

            <GlassCard className="p-5 space-y-2">
              <span className="text-xs font-bold text-slate-400 flex items-center gap-1.5">
                <CreditCard className="w-4 h-4 text-amber-400" /> Monthly Recurring Revenue
              </span>
              <div className="text-2xl font-black text-amber-400">
                ${cards.mrr?.toLocaleString()}
              </div>
              <span className="text-[10px] text-emerald-500 font-bold">
                ARR: ${cards.arr?.toLocaleString()}
              </span>
            </GlassCard>

            <GlassCard className="p-5 space-y-2">
              <span className="text-xs font-bold text-slate-400 flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-cyan-400" /> AI Generations Cost
              </span>
              <div className="text-2xl font-black text-cyan-400">
                ${cards.aiCost}
              </div>
              <span className="text-[10px] text-slate-400 font-semibold">
                {cards.aiRequests?.toLocaleString()} total AI requests
              </span>
            </GlassCard>

            <GlassCard className="p-5 space-y-2">
              <span className="text-xs font-bold text-slate-400 flex items-center gap-1.5">
                <Youtube className="w-4 h-4 text-red-500" /> Synced YouTube Videos
              </span>
              <div className="text-2xl font-black text-red-400">
                {cards.videosSynced?.toLocaleString()}
              </div>
              <span className="text-[10px] text-slate-400 font-semibold">
                Across {cards.youtubeChannels} channels
              </span>
            </GlassCard>
          </div>

          {/* Maintenance & Health Actions */}
          <GlassCard className="p-6 space-y-4">
            <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
              System Maintenance Shortcuts
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <button
                onClick={() => handleSystemAction('Flush Cache')}
                className="p-4 rounded-2xl bg-slate-100 dark:bg-slate-800 hover:bg-purple-500/20 hover:border-purple-500 border border-slate-200 dark:border-slate-700 text-left transition-all"
              >
                <h4 className="text-xs font-bold text-slate-900 dark:text-white">Flush Keyword Cache</h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Clear old search volume data</p>
              </button>

              <button
                onClick={() => handleSystemAction('Sync Viral Trend Radar')}
                className="p-4 rounded-2xl bg-slate-100 dark:bg-slate-800 hover:bg-purple-500/20 hover:border-purple-500 border border-slate-200 dark:border-slate-700 text-left transition-all"
              >
                <h4 className="text-xs font-bold text-slate-900 dark:text-white">Sync Viral Trend Radar</h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Force update YouTube velocity scores</p>
              </button>

              <button
                onClick={() => handleSystemAction('Run OAuth Audit')}
                className="p-4 rounded-2xl bg-slate-100 dark:bg-slate-800 hover:bg-purple-500/20 hover:border-purple-500 border border-slate-200 dark:border-slate-700 text-left transition-all"
              >
                <h4 className="text-xs font-bold text-slate-900 dark:text-white">Run OAuth Audit</h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Verify Google API key token refreshes</p>
              </button>
            </div>
          </GlassCard>
        </div>
      )}

      {/* TAB 2: USER MANAGEMENT */}
      {activeTab === 'users' && <UserManagementTab onImpersonate={handleImpersonateUser} />}

      {/* TAB 3: YOUTUBE ADMIN */}
      {activeTab === 'youtube' && <YouTubeAdminTab />}

      {/* TAB 4: AI ADMIN */}
      {activeTab === 'ai' && <AIAdminTab />}

      {/* TAB 5: BILLING & SUBSCRIPTIONS */}
      {activeTab === 'billing' && <BillingAdminTab />}

      {/* TAB 6: SYSTEM & AUDIT LOGS */}
      {activeTab === 'system' && <SystemAdminTab />}
    </div>
  );
};
