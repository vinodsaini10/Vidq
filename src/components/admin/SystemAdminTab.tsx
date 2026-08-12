import React, { useState, useEffect } from 'react';
import { ToggleLeft, ToggleRight, Settings, AlertOctagon, Megaphone, HelpCircle, FileText, RefreshCw, CheckCircle2 } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const SystemAdminTab: React.FC = () => {
  const { showToast } = useAppState();
  const [featureFlags, setFeatureFlags] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [tickets, setTickets] = useState<any[]>([]);
  const [announcementTitle, setAnnouncementTitle] = useState('');
  const [announcementMsg, setAnnouncementMsg] = useState('');
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [subTab, setSubTab] = useState<'flags' | 'settings' | 'audit' | 'support' | 'broadcast'>('flags');

  useEffect(() => {
    fetchSystemData();
  }, []);

  const fetchSystemData = async () => {
    try {
      const token = localStorage.getItem('token');
      const [flagRes, auditRes, tickRes] = await Promise.all([
        fetch('/api/v1/admin/feature-flags', { headers: { Authorization: `Bearer ${token}` } }),
        fetch('/api/v1/admin/audit-logs', { headers: { Authorization: `Bearer ${token}` } }),
        fetch('/api/v1/admin/support/tickets', { headers: { Authorization: `Bearer ${token}` } })
      ]);

      if (flagRes.ok) {
        const fData = await flagRes.json();
        setFeatureFlags(fData.flags || []);
      }
      if (auditRes.ok) {
        const aData = await auditRes.json();
        setAuditLogs(aData.auditLogs || []);
      }
      if (tickRes.ok) {
        const tData = await tickRes.json();
        setTickets(tData.tickets || []);
      }
    } catch (e) {
      console.error("Error loading system data", e);
    }
  };

  const handleToggleFlag = async (flagId: string, currentStatus: boolean) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/admin/feature-flags/${flagId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ is_enabled: !currentStatus })
      });
      if (res.ok) {
        showToast('Feature flag status updated.');
        fetchSystemData();
      }
    } catch (e) {
      showToast('Failed to toggle flag.');
    }
  };

  const handleBroadcastAnnouncement = async () => {
    if (!announcementTitle || !announcementMsg) return;
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/admin/announcements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ title: announcementTitle, message: announcementMsg, audience: 'ALL' })
      });
      if (res.ok) {
        showToast('Platform announcement broadcasted successfully!');
        setAnnouncementTitle('');
        setAnnouncementMsg('');
      }
    } catch (e) {
      showToast('Failed to post announcement.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Navigation Sub-bar */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setSubTab('flags')}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold ${subTab === 'flags' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'}`}
        >
          Feature Flags
        </button>
        <button
          onClick={() => setSubTab('settings')}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold ${subTab === 'settings' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'}`}
        >
          Platform Settings
        </button>
        <button
          onClick={() => setSubTab('audit')}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold ${subTab === 'audit' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'}`}
        >
          Admin Audit Logs
        </button>
        <button
          onClick={() => setSubTab('support')}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold ${subTab === 'support' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'}`}
        >
          Support Tickets
        </button>
        <button
          onClick={() => setSubTab('broadcast')}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold ${subTab === 'broadcast' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'}`}
        >
          Broadcast Announcement
        </button>
      </div>

      {/* Subtab 1: Feature Flags */}
      {subTab === 'flags' && (
        <GlassCard className="p-6 space-y-4">
          <h3 className="text-base font-extrabold text-white">Dynamic Platform Feature Flags</h3>
          <div className="divide-y divide-slate-800">
            {featureFlags.map((flag) => (
              <div key={flag.id} className="py-3 flex items-center justify-between">
                <div>
                  <span className="font-bold text-white text-xs">{flag.name}</span>
                  <p className="text-[11px] text-slate-500 font-mono">{flag.key}</p>
                </div>
                <button
                  onClick={() => handleToggleFlag(flag.id, flag.is_enabled)}
                  className={`p-1 rounded-lg text-xs font-bold flex items-center gap-1.5 ${
                    flag.is_enabled ? 'text-emerald-400' : 'text-slate-500'
                  }`}
                >
                  {flag.is_enabled ? <ToggleRight className="w-8 h-8" /> : <ToggleLeft className="w-8 h-8" />}
                </button>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {/* Subtab 2: Settings & Maintenance */}
      {subTab === 'settings' && (
        <GlassCard className="p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h4 className="text-sm font-extrabold text-white">Maintenance Mode Override</h4>
              <p className="text-xs text-slate-400 mt-0.5">Redirect non-admin users to maintenance page.</p>
            </div>
            <button
              onClick={() => setMaintenanceMode(!maintenanceMode)}
              className={`px-4 py-2 rounded-xl font-bold text-xs ${
                maintenanceMode ? 'bg-red-600 text-white' : 'bg-slate-800 text-slate-300'
              }`}
            >
              {maintenanceMode ? 'MAINTENANCE ACTIVE' : 'Enable Maintenance'}
            </button>
          </div>
        </GlassCard>
      )}

      {/* Subtab 3: Audit Logs */}
      {subTab === 'audit' && (
        <GlassCard className="p-6">
          <h3 className="text-base font-extrabold text-white mb-4">Admin Action Audit Trail</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase font-black">
                  <th className="pb-3">Timestamp</th>
                  <th className="pb-3">Action</th>
                  <th className="pb-3">Target Resource</th>
                  <th className="pb-3">Admin User ID</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {auditLogs.map((log) => (
                  <tr key={log.id}>
                    <td className="py-3 text-slate-400">{log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A'}</td>
                    <td className="py-3 font-mono text-purple-400 font-bold">{log.action}</td>
                    <td className="py-3 text-white font-bold">{log.targetResource}</td>
                    <td className="py-3 text-slate-500 font-mono text-[11px]">{log.adminUserId || 'SYSTEM'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}

      {/* Subtab 4: Support */}
      {subTab === 'support' && (
        <GlassCard className="p-6">
          <h3 className="text-base font-extrabold text-white mb-4">Support Queue</h3>
          <div className="divide-y divide-slate-800">
            {tickets.map((t) => (
              <div key={t.id} className="py-3 flex items-center justify-between text-xs">
                <div>
                  <span className="font-bold text-white">{t.subject}</span>
                  <p className="text-[11px] text-slate-500">Ticket #{t.ticketNumber} • Priority: {t.priority}</p>
                </div>
                <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 text-[10px] font-bold">
                  {t.status}
                </span>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {/* Subtab 5: Broadcast Announcement */}
      {subTab === 'broadcast' && (
        <GlassCard className="p-6 space-y-4">
          <h3 className="text-base font-extrabold text-white flex items-center gap-2">
            <Megaphone className="w-5 h-5 text-purple-400" /> Broadcast System Announcement
          </h3>
          <input
            type="text"
            placeholder="Announcement Title"
            value={announcementTitle}
            onChange={(e) => setAnnouncementTitle(e.target.value)}
            className="w-full px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-white font-bold"
          />
          <textarea
            rows={3}
            placeholder="Announcement Message content..."
            value={announcementMsg}
            onChange={(e) => setAnnouncementMsg(e.target.value)}
            className="w-full p-3 text-xs bg-slate-950 border border-slate-800 rounded-xl text-white font-mono"
          />
          <button
            onClick={handleBroadcastAnnouncement}
            className="px-5 py-2.5 rounded-xl bg-purple-600 text-white font-extrabold text-xs hover:bg-purple-500 transition-all"
          >
            Broadcast to All Active Users
          </button>
        </GlassCard>
      )}
    </div>
  );
};
