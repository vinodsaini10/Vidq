import React, { useState, useEffect } from 'react';
import { CreditCard, Sparkles, Check, Zap, ShieldCheck, ArrowRight, RefreshCw, FileText, Tag, Receipt, ExternalLink } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const BillingPage: React.FC = () => {
  const { userProfile, setUserProfile, showToast } = useAppState();
  const [provider, setProvider] = useState<'STRIPE' | 'RAZORPAY'>('STRIPE');
  const [billingInterval, setBillingInterval] = useState<'month' | 'year'>('month');
  const [couponCode, setCouponCode] = useState('');
  const [appliedCoupon, setAppliedCoupon] = useState<{ code: string; discountAmount: number } | null>(null);
  const [couponLoading, setCouponLoading] = useState(false);
  const [loadingPlan, setLoadingPlan] = useState<string | null>(null);
  const [portalLoading, setPortalLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'plans' | 'invoices' | 'usage'>('plans');
  const [invoices, setInvoices] = useState<any[]>([]);
  const [usageSummary, setUsageSummary] = useState<any[]>([]);

  useEffect(() => {
    fetchInvoicesAndUsage();
  }, []);

  const fetchInvoicesAndUsage = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const [invRes, useRes] = await Promise.all([
        fetch('/api/v1/billing/invoices', { headers: { Authorization: `Bearer ${token}` } }),
        fetch('/api/v1/billing/usage', { headers: { Authorization: `Bearer ${token}` } })
      ]);

      if (invRes.ok) {
        const invData = await invRes.json();
        setInvoices(invData);
      }
      if (useRes.ok) {
        const useData = await useRes.json();
        setUsageSummary(useData);
      }
    } catch (e) {
      console.error("Error fetching billing details", e);
    }
  };

  const plans = [
    {
      code: 'free',
      name: 'Free Creator',
      priceMonthly: 0,
      priceYearly: 0,
      credits: '50 credits/mo',
      features: ['5 AI Video Scripts / month', '10 AI Title generations', 'Basic SEO Scorecard', '1 Channel Sync'],
    },
    {
      code: 'starter',
      name: 'Starter Creator',
      priceMonthly: 19,
      priceYearly: 190,
      credits: '500 credits/mo',
      features: [
        '500 AI Generation Credits',
        '3 Channel Syncs',
        '25 Video SEO Audits / mo',
        '3 Competitors Tracked',
        'PDF & CSV Export'
      ],
    },
    {
      code: 'pro',
      name: 'Pro Creator',
      priceMonthly: 49,
      priceYearly: 490,
      popular: true,
      credits: '2,000 credits/mo',
      features: [
        '2,000 AI Generation Credits',
        '10 Channel Syncs',
        '100 Video SEO Audits / mo',
        'Bulk AI Script Workflows',
        'Unlimited Historical Analytics',
        '10 Competitors Tracked'
      ],
    },
    {
      code: 'business',
      name: 'Agency Studio',
      priceMonthly: 149,
      priceYearly: 1490,
      credits: '10,000 credits/mo',
      features: [
        '10,000 AI Generation Credits',
        '30 Channel Syncs',
        'Unlimited Video SEO Audits',
        'Priority GPU AI Speed',
        'Team Collaboration (5 seats)',
        'Dedicated API Access'
      ],
    },
  ];

  const handleValidateCoupon = async () => {
    if (!couponCode.trim()) return;
    setCouponLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/billing/coupons/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ code: couponCode, purchase_amount: 49 })
      });
      const data = await res.json();
      if (data.is_valid) {
        setAppliedCoupon({ code: couponCode, discountAmount: data.discount_amount });
        showToast(`Coupon applied! Saved $${data.discount_amount}`);
      } else {
        showToast(data.message || 'Invalid coupon code');
      }
    } catch (e) {
      showToast('Error validating coupon code');
    } finally {
      setCouponLoading(false);
    }
  };

  const handleSelectPlan = async (planCode: string) => {
    setLoadingPlan(planCode);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/billing/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          plan_code: planCode,
          billing_interval: billingInterval,
          provider: provider,
          coupon_code: appliedCoupon ? appliedCoupon.code : undefined,
          success_url: window.location.origin + '/billing?status=success',
          cancel_url: window.location.origin + '/billing?status=cancelled'
        })
      });

      const data = await res.json();
      if (res.ok) {
        if (data.checkout_url) {
          window.location.href = data.checkout_url;
        } else {
          setUserProfile({ ...userProfile, plan: planCode });
          showToast(`Successfully upgraded to ${planCode.toUpperCase()} plan!`);
        }
      } else {
        showToast(data.detail || 'Failed to initiate checkout.');
      }
    } catch (e) {
      showToast('Error connecting to payment gateway.');
    } finally {
      setLoadingPlan(null);
    }
  };

  const handleOpenPortal = async () => {
    setPortalLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/billing/portal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ provider: provider, return_url: window.location.origin + '/billing' })
      });
      const data = await res.json();
      if (data.portal_url) {
        window.location.href = data.portal_url;
      } else {
        showToast('Portal link generated.');
      }
    } catch (e) {
      showToast('Error launching customer portal.');
    } finally {
      setPortalLoading(false);
    }
  };

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2">
            <CreditCard className="w-7 h-7 text-amber-500" />
            Billing & AI Credit Management
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
            Manage plans, top up AI generation credits, and review payment invoices.
          </p>
        </div>

        <button
          onClick={handleOpenPortal}
          disabled={portalLoading}
          className="px-4 py-2.5 rounded-xl bg-slate-800 text-slate-200 hover:bg-slate-700 font-bold text-xs flex items-center gap-2 border border-slate-700 transition-all"
        >
          {portalLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ExternalLink className="w-4 h-4 text-amber-400" />}
          <span>Customer Payment Portal</span>
        </button>
      </div>

      {/* Active Membership Banner */}
      <GlassCard className="p-6 border-amber-500/30 bg-gradient-to-r from-amber-500/10 via-slate-900 to-red-500/10">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-amber-400">Active Membership</span>
            <h2 className="text-2xl font-black text-white mt-0.5">{userProfile.plan || 'Free Creator'}</h2>
            <p className="text-xs text-slate-300 mt-1">
              Used {userProfile.aiCreditsUsed} of {userProfile.aiCreditsMax} AI Generation Credits this billing cycle.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={async () => {
                const token = localStorage.getItem('token');
                const res = await fetch('/api/v1/billing/topup', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                  body: JSON.stringify({ amount: 500 })
                });
                if (res.ok) {
                  setUserProfile({ ...userProfile, aiCreditsMax: userProfile.aiCreditsMax + 500 });
                  showToast('Top-up successful! Added 500 AI credits.');
                }
              }}
              className="px-5 py-2.5 rounded-xl bg-amber-500 text-slate-950 font-black text-xs hover:bg-amber-400 transition-all shadow-lg shadow-amber-500/20 flex items-center gap-2"
            >
              <Zap className="w-4 h-4" />
              <span>Top-up 500 Credits ($10)</span>
            </button>
          </div>
        </div>
      </GlassCard>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('plans')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
            activeTab === 'plans' ? 'bg-amber-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
          }`}
        >
          Subscription Plans
        </button>
        <button
          onClick={() => setActiveTab('invoices')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
            activeTab === 'invoices' ? 'bg-amber-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
          }`}
        >
          Invoices & Payments ({invoices.length})
        </button>
        <button
          onClick={() => setActiveTab('usage')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
            activeTab === 'usage' ? 'bg-amber-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
          }`}
        >
          Usage & Quotas
        </button>
      </div>

      {/* Tab 1: Plans */}
      {activeTab === 'plans' && (
        <div className="space-y-6">
          {/* Controls: Provider Selection & Billing Cycle Toggle */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
            {/* Gateway Provider */}
            <div className="flex items-center gap-2">
              <span className="text-xs font-extrabold text-slate-400 uppercase">Payment Method:</span>
              <button
                onClick={() => setProvider('STRIPE')}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold border transition-all ${
                  provider === 'STRIPE' ? 'bg-indigo-600 border-indigo-400 text-white' : 'bg-slate-800 border-slate-700 text-slate-400'
                }`}
              >
                Stripe (Cards)
              </button>
              <button
                onClick={() => setProvider('RAZORPAY')}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold border transition-all ${
                  provider === 'RAZORPAY' ? 'bg-blue-600 border-blue-400 text-white' : 'bg-slate-800 border-slate-700 text-slate-400'
                }`}
              >
                Razorpay (UPI / Cards / Banking)
              </button>
            </div>

            {/* Billing Interval Toggle */}
            <div className="flex items-center gap-2">
              <span className={`text-xs font-bold ${billingInterval === 'month' ? 'text-white' : 'text-slate-400'}`}>Monthly</span>
              <button
                onClick={() => setBillingInterval(billingInterval === 'month' ? 'year' : 'month')}
                className="w-12 h-6 bg-slate-800 rounded-full p-1 border border-slate-700 relative transition-colors"
              >
                <div className={`w-4 h-4 rounded-full bg-amber-500 transition-transform ${billingInterval === 'year' ? 'translate-x-6' : 'translate-x-0'}`} />
              </button>
              <span className={`text-xs font-bold ${billingInterval === 'year' ? 'text-amber-400' : 'text-slate-400'}`}>
                Yearly <span className="text-[10px] bg-amber-500/20 text-amber-300 px-1.5 py-0.5 rounded ml-1">Save 20%</span>
              </span>
            </div>

            {/* Coupon Box */}
            <div className="flex items-center gap-2">
              <div className="relative">
                <Tag className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                <input
                  type="text"
                  placeholder="Promo Code"
                  value={couponCode}
                  onChange={(e) => setCouponCode(e.target.value)}
                  className="pl-8 pr-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                />
              </div>
              <button
                onClick={handleValidateCoupon}
                disabled={couponLoading}
                className="px-3 py-1.5 rounded-lg bg-slate-800 text-amber-400 font-bold text-xs hover:bg-slate-700 border border-slate-700"
              >
                Apply
              </button>
            </div>
          </div>

          {/* Pricing Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {plans.map((p) => {
              const price = billingInterval === 'year' ? p.priceYearly : p.priceMonthly;
              const isCurrent = userProfile.plan?.toLowerCase() === p.code.toLowerCase();
              return (
                <GlassCard
                  key={p.code}
                  className={`p-6 flex flex-col justify-between space-y-6 ${
                    p.popular ? 'border-amber-500 ring-2 ring-amber-500/30' : ''
                  }`}
                >
                  <div className="space-y-4">
                    {p.popular && (
                      <span className="text-[10px] font-black uppercase tracking-widest text-slate-950 bg-amber-500 px-3 py-1 rounded-full inline-block">
                        Most Popular
                      </span>
                    )}
                    <div>
                      <h3 className="text-xl font-black text-white">{p.name}</h3>
                      <div className="flex items-baseline gap-1 mt-2">
                        <span className="text-3xl font-black text-white">${price}</span>
                        <span className="text-xs font-bold text-slate-400">/{billingInterval}</span>
                      </div>
                      <div className="text-xs font-extrabold text-amber-400 mt-1">{p.credits}</div>
                    </div>

                    <ul className="space-y-2 text-xs text-slate-300">
                      {p.features.map((feat, i) => (
                        <li key={i} className="flex items-center gap-2">
                          <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                          <span>{feat}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <button
                    onClick={() => handleSelectPlan(p.code)}
                    disabled={isCurrent || loadingPlan === p.code}
                    className={`w-full py-3 rounded-xl font-extrabold text-xs transition-all flex items-center justify-center gap-2 ${
                      isCurrent
                        ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                        : 'bg-gradient-to-r from-amber-500 to-red-500 text-slate-950 shadow-lg shadow-amber-500/20 hover:opacity-90'
                    }`}
                  >
                    {loadingPlan === p.code ? <RefreshCw className="w-4 h-4 animate-spin" /> : null}
                    <span>{isCurrent ? 'Current Active Plan' : `Checkout ${p.name}`}</span>
                  </button>
                </GlassCard>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab 2: Invoices */}
      {activeTab === 'invoices' && (
        <GlassCard className="p-6">
          <h3 className="text-lg font-extrabold text-white mb-4 flex items-center gap-2">
            <Receipt className="w-5 h-5 text-amber-500" />
            Billing Invoices & Transaction History
          </h3>
          {invoices.length === 0 ? (
            <p className="text-xs text-slate-400">No payment invoices logged yet.</p>
          ) : (
            <div className="divide-y divide-slate-800">
              {invoices.map((inv) => (
                <div key={inv.id} className="py-3 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-bold text-white">{inv.invoice_number}</span>
                    <p className="text-[11px] text-slate-400">{new Date(inv.paid_at || inv.created_at).toLocaleDateString()}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="font-black text-amber-400">${inv.total_amount} {inv.currency}</span>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-extrabold uppercase text-[10px]">
                      {inv.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </GlassCard>
      )}

      {/* Tab 3: Usage */}
      {activeTab === 'usage' && (
        <GlassCard className="p-6">
          <h3 className="text-lg font-extrabold text-white mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" />
            Usage Quotas & Limits
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {usageSummary.map((u) => (
              <div key={u.metric_key} className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-extrabold text-slate-300 uppercase">{u.metric_key.replace('_', ' ')}</span>
                  <span className="font-black text-amber-400">{u.units_used} / {u.max_limit === -1 ? '∞' : u.max_limit}</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-amber-500 h-full rounded-full transition-all"
                    style={{ width: `${Math.min(100, u.percentage_used || 0)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      )}
    </div>
  );
};
