import React from 'react';
import {
  LayoutDashboard,
  BarChart3,
  Video,
  Sparkles,
  FileText,
  Type,
  ListFilter,
  Tags,
  Image,
  Key,
  Compass,
  Users,
  Flame,
  Calendar,
  FileSpreadsheet,
  Settings,
  CreditCard,
  Bell,
  HelpCircle,
  ShieldCheck,
  ChevronRight,
  TrendingUp,
} from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { PageId } from '../../types';

interface SidebarNavGroup {
  groupName: string;
  items: {
    id: PageId;
    label: string;
    icon: any;
    badge?: string;
  }[];
}

export const Sidebar: React.FC = () => {
  const { currentPage, navigateTo, sidebarOpen, channelStats, userProfile } = useAppState();

  const navigationGroups: SidebarNavGroup[] = [
    {
      groupName: 'Main Platform',
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'analytics', label: 'Deep Analytics', icon: BarChart3 },
        { id: 'channel-overview', label: 'Channel Audit', icon: TrendingUp },
        { id: 'video-performance', label: 'Video Performance', icon: Video },
      ],
    },
    {
      groupName: 'AI Creation Suite',
      items: [
        { id: 'video-seo', label: 'Video SEO Inspector', icon: Sparkles, badge: 'AI 0-100' },
        { id: 'ai-script', label: 'AI Script Generator', icon: FileText, badge: 'Pro' },
        { id: 'ai-title', label: 'AI Title Generator', icon: Type },
        { id: 'description-generator', label: 'Description Generator', icon: ListFilter },
        { id: 'tags-generator', label: 'Tags Generator', icon: Tags },
        { id: 'thumbnail-prompts', label: 'Thumbnail Prompts', icon: Image, badge: 'Midjourney' },
      ],
    },
    {
      groupName: 'Growth & Intelligence',
      items: [
        { id: 'keyword-research', label: 'Keyword Research', icon: Key },
        { id: 'keyword-explorer', label: 'Keyword Explorer', icon: Compass },
        { id: 'competitors', label: 'Competitor Analysis', icon: Users },
        { id: 'trends', label: 'Trend Explorer', icon: Flame, badge: 'Viral' },
        { id: 'content-calendar', label: 'Content Calendar', icon: Calendar },
      ],
    },
    {
      groupName: 'Management & Admin',
      items: [
        { id: 'reports', label: 'PDF Growth Reports', icon: FileSpreadsheet },
        { id: 'billing', label: 'Billing & AI Credits', icon: CreditCard },
        { id: 'notifications', label: 'Notifications', icon: Bell },
        { id: 'settings', label: 'Channel & Settings', icon: Settings },
        { id: 'support', label: 'Support & Help Desk', icon: HelpCircle },
        { id: 'admin', label: 'Admin Control', icon: ShieldCheck, badge: 'Super' },
      ],
    },
  ];

  if (!sidebarOpen) {
    return null;
  }

  return (
    <aside className="w-64 flex-shrink-0 h-[calc(100vh-4rem)] sticky top-16 border-r border-slate-200/80 dark:border-slate-800/80 bg-white/50 dark:bg-slate-950/50 backdrop-blur-xl overflow-y-auto p-4 transition-all duration-300 z-30">
      {/* Channel Header Widget */}
      <div className="p-3 mb-4 rounded-2xl bg-gradient-to-br from-red-500/10 via-slate-100 to-amber-500/10 dark:from-red-500/20 dark:via-slate-900 dark:to-amber-500/20 border border-red-500/20 flex items-center justify-between">
        <div className="flex items-center gap-2.5 overflow-hidden">
          <img
            src={channelStats.avatarUrl}
            alt={channelStats.name}
            className="w-9 h-9 rounded-xl object-cover ring-2 ring-red-500/40"
          />
          <div className="truncate">
            <h4 className="text-xs font-black text-slate-900 dark:text-white truncate">
              {channelStats.name}
            </h4>
            <span className="text-[10px] font-semibold text-red-500">
              {(channelStats.subscribers / 1000).toFixed(1)}k Subscribers
            </span>
          </div>
        </div>
        <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-4 ring-emerald-500/20 animate-pulse" />
      </div>

      {/* AI Credit Usage Meter */}
      <div className="mb-6 p-3 rounded-xl bg-slate-100/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800">
        <div className="flex justify-between items-center text-[11px] font-semibold text-slate-600 dark:text-slate-300">
          <span className="flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-red-500" />
            AI Credits
          </span>
          <span className="text-red-500 font-bold">
            {userProfile.aiCreditsUsed} / {userProfile.aiCreditsMax}
          </span>
        </div>
        <div className="w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
          <div
            className="bg-gradient-to-r from-red-500 to-amber-500 h-full rounded-full transition-all duration-500"
            style={{ width: `${(userProfile.aiCreditsUsed / userProfile.aiCreditsMax) * 100}%` }}
          />
        </div>
      </div>

      {/* Navigation Groups */}
      <div className="space-y-6">
        {navigationGroups.map((group, idx) => (
          <div key={idx}>
            <h5 className="px-3 mb-2 text-[10px] font-bold uppercase tracking-widest text-slate-400">
              {group.groupName}
            </h5>
            <div className="space-y-1">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = currentPage === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => navigateTo(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-bold transition-all duration-200 ${
                      isActive
                        ? 'bg-gradient-to-r from-red-500 to-rose-600 text-white shadow-lg shadow-red-500/20'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-900'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 truncate">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                      <span className="truncate">{item.label}</span>
                    </div>

                    {item.badge && (
                      <span
                        className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full ${
                          isActive
                            ? 'bg-white/20 text-white'
                            : 'bg-red-500/10 text-red-500 dark:bg-red-500/20'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
};
