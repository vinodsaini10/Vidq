import React, { useState, useEffect } from 'react';
import { Search, UserCheck, UserX, Shield, Zap, Eye, RefreshCw, AlertCircle, PlusCircle, CheckCircle2, User } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

interface UserManagementTabProps {
  onImpersonate: (user: any) => void;
}

export const UserManagementTab: React.FC<UserManagementTabProps> = ({ onImpersonate }) => {
  const { showToast } = useAppState();
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [selectedUser, setSelectedUser] = useState<any | null>(null);
  const [creditAmount, setCreditAmount] = useState(500);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [userDetail, setUserDetail] = useState<any | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, [search, roleFilter]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      let url = '/api/v1/admin/users?page=1&limit=50';
      if (search) url += `&search=${encodeURIComponent(search)}`;
      if (roleFilter) url += `&role=${encodeURIComponent(roleFilter)}`;

      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUsers(data.items || []);
      }
    } catch (e) {
      console.error("Error fetching users", e);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleSuspend = async (user: any) => {
    try {
      const token = localStorage.getItem('token');
      const endpoint = user.isActive
        ? `/api/v1/admin/users/${user.id}/suspend`
        : `/api/v1/admin/users/${user.id}/unsuspend`;

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        showToast(`User ${user.email} ${user.isActive ? 'suspended' : 'reactivated'}.`);
        fetchUsers();
      }
    } catch (e) {
      showToast('Action failed.');
    }
  };

  const handleGrantCredits = async (userId: string) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/admin/users/${userId}/credits`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ amount: creditAmount, reason: 'Admin panel grant' })
      });
      if (res.ok) {
        showToast(`Granted ${creditAmount} credits to user.`);
        fetchUsers();
      }
    } catch (e) {
      showToast('Failed to grant credits.');
    }
  };

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/admin/users/${userId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ role: newRole })
      });
      if (res.ok) {
        showToast(`Updated user role to ${newRole}`);
        fetchUsers();
      }
    } catch (e) {
      showToast('Failed to update role.');
    }
  };

  const handleViewDetails = async (userId: string) => {
    setDetailModalOpen(true);
    setDetailLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/admin/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUserDetail(data);
      }
    } catch (e) {
      showToast('Error loading user detail.');
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search & Filter Header */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search email or name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
          />
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-purple-500"
          >
            <option value="">All Roles</option>
            <option value="FREE_USER">FREE_USER</option>
            <option value="PREMIUM_USER">PREMIUM_USER</option>
            <option value="SUPPORT">SUPPORT</option>
            <option value="MANAGER">MANAGER</option>
            <option value="ADMIN">ADMIN</option>
            <option value="SUPER_ADMIN">SUPER_ADMIN</option>
          </select>

          <button
            onClick={fetchUsers}
            className="p-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white border border-slate-700"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Users Table */}
      <GlassCard className="p-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase font-black">
                <th className="pb-3">User Profile</th>
                <th className="pb-3">Role</th>
                <th className="pb-3">Status</th>
                <th className="pb-3">AI Credits</th>
                <th className="pb-3">YouTube</th>
                <th className="pb-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3">
                    <div className="font-bold text-white">{u.fullName}</div>
                    <div className="text-[11px] text-slate-400">{u.email}</div>
                  </td>
                  <td className="py-3">
                    <select
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      className="px-2 py-1 bg-slate-950 border border-slate-800 rounded text-[11px] text-purple-400 font-extrabold"
                    >
                      <option value="FREE_USER">FREE_USER</option>
                      <option value="PREMIUM_USER">PREMIUM_USER</option>
                      <option value="SUPPORT">SUPPORT</option>
                      <option value="MANAGER">MANAGER</option>
                      <option value="ADMIN">ADMIN</option>
                      <option value="SUPER_ADMIN">SUPER_ADMIN</option>
                    </select>
                  </td>
                  <td className="py-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-black uppercase ${
                        u.isActive ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
                      }`}
                    >
                      {u.isActive ? 'Active' : 'Suspended'}
                    </span>
                  </td>
                  <td className="py-3">
                    <div className="text-slate-200 font-extrabold">{u.creditsUsed} / {u.creditsMax}</div>
                  </td>
                  <td className="py-3 text-slate-400">
                    {u.youtubeChannelTitle || 'None'}
                  </td>
                  <td className="py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleViewDetails(u.id)}
                        className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white"
                        title="View Details"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>

                      <button
                        onClick={() => handleGrantCredits(u.id)}
                        className="p-1.5 rounded-lg bg-amber-500/20 text-amber-400 hover:bg-amber-500/30"
                        title="Grant +500 Credits"
                      >
                        <Zap className="w-3.5 h-3.5" />
                      </button>

                      <button
                        onClick={() => onImpersonate(u)}
                        className="p-1.5 rounded-lg bg-purple-500/20 text-purple-400 hover:bg-purple-500/30"
                        title="Impersonate User"
                      >
                        <User className="w-3.5 h-3.5" />
                      </button>

                      <button
                        onClick={() => handleToggleSuspend(u)}
                        className={`p-1.5 rounded-lg ${
                          u.isActive
                            ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                            : 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30'
                        }`}
                        title={u.isActive ? 'Suspend User' : 'Reactivate User'}
                      >
                        {u.isActive ? <UserX className="w-3.5 h-3.5" /> : <UserCheck className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>

      {/* User Detail Modal */}
      {detailModalOpen && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-black text-white">User Audit Details</h3>
              <button
                onClick={() => setDetailModalOpen(false)}
                className="text-slate-400 hover:text-white font-bold"
              >
                ✕
              </button>
            </div>

            {detailLoading || !userDetail ? (
              <div className="py-8 text-center text-xs text-slate-400">Loading user profile breakdown...</div>
            ) : (
              <div className="space-y-4 text-xs">
                <div className="grid grid-cols-2 gap-4 bg-slate-950 p-4 rounded-xl">
                  <div>
                    <span className="text-slate-500 uppercase font-bold text-[10px]">Email</span>
                    <p className="text-white font-bold">{userDetail.user.email}</p>
                  </div>
                  <div>
                    <span className="text-slate-500 uppercase font-bold text-[10px]">Role</span>
                    <p className="text-purple-400 font-black">{userDetail.user.role}</p>
                  </div>
                  <div>
                    <span className="text-slate-500 uppercase font-bold text-[10px]">AI Credit Usage</span>
                    <p className="text-amber-400 font-extrabold">{userDetail.user.creditsUsed} / {userDetail.user.creditsMax}</p>
                  </div>
                  <div>
                    <span className="text-slate-500 uppercase font-bold text-[10px]">Subscription Plan</span>
                    <p className="text-emerald-400 font-extrabold">{userDetail.subscription?.planCode || 'Free'}</p>
                  </div>
                </div>

                {userDetail.youtubeChannel && (
                  <div className="bg-slate-950 p-4 rounded-xl space-y-1">
                    <span className="text-slate-500 uppercase font-bold text-[10px]">Connected YouTube Channel</span>
                    <p className="text-white font-bold">{userDetail.youtubeChannel.title} ({userDetail.youtubeChannel.subscriberCount} Subscribers)</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
