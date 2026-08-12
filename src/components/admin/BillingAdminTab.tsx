import React, { useState, useEffect } from 'react';
import { CreditCard, DollarSign, Tag, RefreshCw, AlertCircle, ArrowUpRight } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const BillingAdminTab: React.FC = () => {
  const { showToast } = useAppState();
  const [revenue, setRevenue] = useState<any | null>(null);
  const [subscriptions, setSubscriptions] = useState<any[]>([]);
  const [coupons, setCoupons] = useState<any[]>([]);
  const [activeSubTab, setActiveSubTab] = useState<'revenue' | 'subscriptions' | 'coupons'>('revenue');

  // Coupon create form
  const [newCouponCode, setNewCouponCode] = useState('');
  const [newDiscountPercent, setNewDiscountPercent] = useState(20);

  useEffect(() => {
    fetchBillingData();
  }, []);

  const fetchBillingData = async () => {
    try {
      const token = localStorage.getItem('token');
      const [revRes, subRes, cpnRes] = await Promise.all([
        fetch('/api/v1/admin/billing/revenue', { headers: { Authorization: `Bearer ${token}` } }),
        fetch('/api/v1/admin/billing/subscriptions', { headers: { Authorization: `Bearer ${token}` } }),
        fetch('/api/v1/admin/coupons', { headers: { Authorization: `Bearer ${token}` } })
      ]);

      if (revRes.ok) {
        const rData = await revRes.json();
        setRevenue(rData);
      }
      if (subRes.ok) {
        const sData = await subRes.json();
        setSubscriptions(sData.subscriptions || []);
      }
      if (cpnRes.ok) {
        const cData = await cpnRes.json();
        setCoupons(cData || []);
      }
    } catch (e) {
      console.error("Error loading admin billing data", e);
    }
  };

  const handleCreateCoupon = async () => {
    if (!newCouponCode.trim()) return;
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/admin/coupons', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          code: newCouponCode,
          name: `${newCouponCode} Promo`,
          discount_type: 'PERCENTAGE',
          discount_percent: newDiscountPercent
        })
      });

      if (res.ok) {
        showToast(`Created promo coupon ${newCouponCode}`);
        setNewCouponCode('');
        fetchBillingData();
      }
    } catch (e) {
      showToast('Error creating coupon.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Sub-tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveSubTab('revenue')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
            activeSubTab === 'revenue' ? 'bg-amber-500 text-slate-950 shadow' : 'text-slate-400 hover:text-white'
          }`}
        >
          Revenue Analytics
        </button>
        <button
          onClick={() => setActiveSubTab('subscriptions')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
            activeSubTab === 'subscriptions' ? 'bg-amber-500 text-slate-950 shadow' : 'text-slate-400 hover:text-white'
          }`}
        >
          Subscriptions List
        </button>
        <button
          onClick={() => setActiveSubTab('coupons')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
            activeSubTab === 'coupons' ? 'bg-amber-500 text-slate-950 shadow' : 'text-slate-400 hover:text-white'
          }`}
        >
          Promotional Coupons
        </button>
      </div>

      {/* Tab 1: Revenue Cards */}
      {activeSubTab === 'revenue' && revenue && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <GlassCard className="p-5 border-amber-500/30 space-y-1">
            <span className="text-xs font-bold text-slate-400">Monthly Recurring Revenue (MRR)</span>
            <div className="text-2xl font-black text-amber-400">${revenue.mrr?.toLocaleString()}</div>
            <span className="text-[10px] text-emerald-400 font-bold">Predictable Revenue</span>
          </GlassCard>

          <GlassCard className="p-5 space-y-1">
            <span className="text-xs font-bold text-slate-400">Annual Run Rate (ARR)</span>
            <div className="text-2xl font-black text-white">${revenue.arr?.toLocaleString()}</div>
            <span className="text-[10px] text-slate-400">12x MRR projection</span>
          </GlassCard>

          <GlassCard className="p-5 space-y-1">
            <span className="text-xs font-bold text-slate-400">Total Volume Processed</span>
            <div className="text-2xl font-black text-emerald-400">${revenue.total_revenue?.toLocaleString()}</div>
            <span className="text-[10px] text-emerald-400">All-time lifetime value</span>
          </GlassCard>

          <GlassCard className="p-5 space-y-1">
            <span className="text-xs font-bold text-slate-400">Active Paid Subscribers</span>
            <div className="text-2xl font-black text-purple-400">{revenue.active_paid_subscribers}</div>
            <span className="text-[10px] text-slate-400">Paid tier memberships</span>
          </GlassCard>
        </div>
      )}

      {/* Tab 2: Subscriptions Table */}
      {activeSubTab === 'subscriptions' && (
        <GlassCard className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase font-black">
                  <th className="pb-3">User ID</th>
                  <th className="pb-3">Plan</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Price</th>
                  <th className="pb-3">Gateway Provider</th>
                  <th className="pb-3">Period End</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {subscriptions.map((s) => (
                  <tr key={s.id}>
                    <td className="py-3 font-mono text-slate-400 text-[11px]">{s.user_id}</td>
                    <td className="py-3 font-extrabold text-white">{s.plan_name} ({s.plan_code})</td>
                    <td className="py-3">
                      <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">
                        {s.status}
                      </span>
                    </td>
                    <td className="py-3 text-amber-400 font-black">${s.price}</td>
                    <td className="py-3 text-purple-400 font-bold">{s.provider}</td>
                    <td className="py-3 text-slate-400">
                      {s.current_period_end ? new Date(s.current_period_end).toLocaleDateString() : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}

      {/* Tab 3: Coupons */}
      {activeSubTab === 'coupons' && (
        <div className="space-y-6">
          <GlassCard className="p-6 space-y-4">
            <h3 className="text-sm font-extrabold text-white">Create New Promotional Coupon</h3>
            <div className="flex flex-col sm:flex-row items-center gap-3">
              <input
                type="text"
                placeholder="Code (e.g. SUMMER20)"
                value={newCouponCode}
                onChange={(e) => setNewCouponCode(e.target.value.toUpperCase())}
                className="px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-white font-mono"
              />
              <input
                type="number"
                placeholder="Discount %"
                value={newDiscountPercent}
                onChange={(e) => setNewDiscountPercent(Number(e.target.value))}
                className="px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-xl text-white font-bold w-24"
              />
              <button
                onClick={handleCreateCoupon}
                className="px-4 py-2 rounded-xl bg-amber-500 text-slate-950 font-black text-xs hover:bg-amber-400 transition-all"
              >
                Create Coupon
              </button>
            </div>
          </GlassCard>

          <GlassCard className="p-6">
            <h3 className="text-sm font-extrabold text-white mb-4">Active Coupons</h3>
            <div className="divide-y divide-slate-800">
              {coupons.map((c) => (
                <div key={c.id} className="py-3 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-mono font-black text-amber-400">{c.code}</span>
                    <p className="text-[11px] text-slate-400">{c.name}</p>
                  </div>
                  <div className="font-extrabold text-emerald-400">
                    {c.discount_percent}% OFF
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
};
