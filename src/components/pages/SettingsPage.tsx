import React, { useState } from 'react';
import { Settings, Youtube, Shield, Save, CheckCircle2, Key, BellRing } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const SettingsPage: React.FC = () => {
  const { userProfile, setUserProfile, channelStats, showToast } = useAppState();

  const [name, setName] = useState(userProfile.name);
  const [email, setEmail] = useState(userProfile.email);
  const [youtubeAccount, setYoutubeAccount] = useState(userProfile.connectedYoutubeAccount);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setUserProfile({
      ...userProfile,
      name,
      email,
      connectedYoutubeAccount: youtubeAccount,
    });
    showToast('Channel & Account settings saved!');
  };

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2">
          <Settings className="w-7 h-7 text-red-500" />
          Channel & Profile Settings
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
          Manage connected YouTube Data API keys, custom AI prompt defaults, and profile info.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        <GlassCard className="p-6 space-y-6">
          <h3 className="text-base font-extrabold text-slate-900 dark:text-white flex items-center gap-2">
            <Youtube className="w-5 h-5 text-red-500" />
            YouTube Channel Synchronization
          </h3>

          <div className="p-4 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <img src={channelStats.avatarUrl} alt={channelStats.name} className="w-12 h-12 rounded-2xl object-cover ring-2 ring-red-500/40" />
              <div>
                <h4 className="text-sm font-black text-slate-900 dark:text-white">{channelStats.name}</h4>
                <p className="text-xs text-slate-400">{channelStats.handle} • {channelStats.subscribers.toLocaleString()} subscribers</p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => {
                setYoutubeAccount(!youtubeAccount);
                showToast(youtubeAccount ? 'Disconnected YouTube channel' : 'Connected YouTube channel!');
              }}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                youtubeAccount
                  ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/30'
                  : 'bg-red-500 text-white shadow-lg shadow-red-500/20'
              }`}
            >
              {youtubeAccount ? 'Connected via OAuth 2.0' : 'Connect Channel'}
            </button>
          </div>
        </GlassCard>

        <GlassCard className="p-6 space-y-4">
          <h3 className="text-base font-extrabold text-slate-900 dark:text-white">Profile & Preferences</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">Creator Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-bold focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">Account Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-bold focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
          </div>
        </GlassCard>

        <div className="flex justify-end">
          <button
            type="submit"
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-red-600 to-amber-500 text-white font-black text-xs shadow-xl shadow-red-500/25 hover:opacity-95 transition-all flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            <span>Save Preferences</span>
          </button>
        </div>
      </form>
    </div>
  );
};
