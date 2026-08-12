import React from 'react';
import { Bell, Check, Trash2, Sparkles, AlertTriangle, TrendingUp, CheckCircle2 } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const NotificationsPage: React.FC = () => {
  const { notifications, markNotificationRead, clearAllNotifications, showToast } = useAppState();

  const handleMarkAllRead = () => {
    notifications.forEach((n) => markNotificationRead(n.id));
    showToast('All notifications marked as read');
  };

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2">
            <Bell className="w-7 h-7 text-red-500" />
            Channel Alerts & AI Intelligence Feed
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
            Real-time subscriber milestones, sudden CTR drops, breakout keyword alerts, and system notices.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleMarkAllRead}
            className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-bold text-xs transition-all flex items-center gap-1.5"
          >
            <Check className="w-4 h-4" />
            <span>Mark All Read</span>
          </button>
          <button
            onClick={clearAllNotifications}
            className="px-4 py-2 rounded-xl bg-rose-500/10 text-rose-500 hover:bg-rose-500 hover:text-white font-bold text-xs transition-all flex items-center gap-1.5"
          >
            <Trash2 className="w-4 h-4" />
            <span>Clear Feed</span>
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {notifications.length === 0 ? (
          <GlassCard className="p-12 text-center space-y-3">
            <Bell className="w-12 h-12 text-slate-300 dark:text-slate-700 mx-auto" />
            <h3 className="text-lg font-bold text-slate-700 dark:text-slate-300">Your feed is clean</h3>
            <p className="text-xs text-slate-400">No new alerts or warnings detected for your channel.</p>
          </GlassCard>
        ) : (
          notifications.map((notif) => (
            <GlassCard
              key={notif.id}
              onClick={() => markNotificationRead(notif.id)}
              className={`p-5 flex items-start gap-4 transition-all cursor-pointer ${
                notif.read ? 'opacity-60 border-slate-200/50 dark:border-slate-800/50' : 'border-red-500/40 bg-red-500/5'
              }`}
            >
              <div className="p-2.5 rounded-xl bg-red-500/10 text-red-500 flex-shrink-0 mt-0.5">
                {notif.type === 'milestone' && <TrendingUp className="w-5 h-5" />}
                {notif.type === 'alert' && <AlertTriangle className="w-5 h-5 text-amber-500" />}
                {notif.type === 'ai' && <Sparkles className="w-5 h-5 text-purple-500" />}
                {notif.type === 'system' && <CheckCircle2 className="w-5 h-5 text-emerald-500" />}
              </div>

              <div className="flex-1 space-y-1">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-black text-slate-900 dark:text-white">{notif.title}</h4>
                  <span className="text-[11px] font-semibold text-slate-400">{notif.time}</span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{notif.message}</p>
              </div>
            </GlassCard>
          ))
        )}
      </div>
    </div>
  );
};
