import React, { useState, useEffect } from 'react';
import { Youtube, RefreshCw, CheckCircle2, AlertCircle, ExternalLink } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const YouTubeAdminTab: React.FC = () => {
  const { showToast } = useAppState();
  const [channels, setChannels] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [syncingId, setSyncingId] = useState<string | null>(null);

  useEffect(() => {
    fetchChannels();
  }, []);

  const fetchChannels = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/admin/youtube', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setChannels(data.channels || []);
      }
    } catch (e) {
      console.error("Error fetching YouTube channels", e);
    } finally {
      setLoading(false);
    }
  };

  const handleForceSync = async (channelId: string, title: string) => {
    setSyncingId(channelId);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/admin/youtube/channels/${channelId}/sync`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        showToast(`Sync forced for channel '${title}'`);
        fetchChannels();
      }
    } catch (e) {
      showToast('Error syncing channel.');
    } finally {
      setSyncingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-black text-white flex items-center gap-2">
          <Youtube className="w-6 h-6 text-red-500" />
          Connected YouTube Channel Monitor ({channels.length})
        </h3>
        <button
          onClick={fetchChannels}
          className="p-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white border border-slate-700"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <GlassCard className="p-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase font-black">
                <th className="pb-3">Channel Title</th>
                <th className="pb-3">Channel ID</th>
                <th className="pb-3">Subscribers</th>
                <th className="pb-3">Videos</th>
                <th className="pb-3">Last Synced</th>
                <th className="pb-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {channels.map((c) => (
                <tr key={c.id}>
                  <td className="py-3 font-bold text-white">{c.title}</td>
                  <td className="py-3 text-slate-400 font-mono text-[11px]">{c.channelId}</td>
                  <td className="py-3 text-amber-400 font-extrabold">{c.subscriberCount?.toLocaleString()}</td>
                  <td className="py-3 text-slate-300">{c.videoCount}</td>
                  <td className="py-3 text-slate-400">
                    {c.lastSyncedAt ? new Date(c.lastSyncedAt).toLocaleString() : 'Never'}
                  </td>
                  <td className="py-3 text-right">
                    <button
                      onClick={() => handleForceSync(c.id, c.title)}
                      disabled={syncingId === c.id}
                      className="px-3 py-1.5 rounded-lg bg-red-600 text-white font-extrabold text-[11px] hover:bg-red-500 transition-all flex items-center gap-1.5 ml-auto"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${syncingId === c.id ? 'animate-spin' : ''}`} />
                      <span>Force Sync</span>
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
