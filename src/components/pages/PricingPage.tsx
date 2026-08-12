import React, { useState } from 'react';
import { Check, Sparkles, Zap, Shield, HelpCircle } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const PricingPage: React.FC = () => {
  const { navigateTo, showToast } = useAppState();
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('yearly');

  const plans = [
    {
      name: 'Free Creator',
      desc: 'Essential AI toolkits for beginner channels.',
      monthlyPrice: 0,
      yearlyPrice: 0,
      credits: '100 AI Credits/mo',
      popular: false,
      features: [
        '5 AI Title Generations / day',
        'Basic Keyword Volume Lookup',
        '0-100 Video SEO Inspector',
        'Standard Community Support',
        '1 Connected YouTube Channel',
      ],
      cta: 'Get Started Free',
      glow: 'none' as const,
    },
    {
      name: 'Pro Creator',
      desc: 'The complete AI growth engine for serious YouTubers.',
      monthlyPrice: 29,
      yearlyPrice: 22,
      credits: '1,000 AI Credits/mo',
      popular: true,
      features: [
        'Unlimited AI Title & Hook Generator',
        'Full Multi-Section Script Writer',
        'Keyword Explorer & CPM Estimates',
        'Breakout Viral Trend Radar',
        'Midjourney & Flux Thumbnail Prompts',
        '3 Competitor Channels Tracking',
        'Priority AI Processing Speed',
      ],
      cta: 'Start 14-Day Free Trial',
      glow: 'purple' as const,
    },
    {
      name: 'Agency Studio',
      desc: 'Powerhouse analytics and unlimited AI for teams & agencies.',
      monthlyPrice: 79,
      yearlyPrice: 62,
      credits: '5,000 AI Credits/mo',
      popular: false,
      features: [
        'Everything in Pro Creator',
        'Up to 15 Connected YouTube Channels',
        'Unlimited Competitor Intelligence',
        'PDF Executive Growth Reports',
        'Team Member Multi-seat Access',
        'Dedicated Account Manager',
        'Custom API Access',
      ],
      cta: 'Upgrade to Studio',
      glow: 'amber' as const,
    },
  ];

  return (
    <div className="min-h-screen py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="text-center max-w-3xl mx-auto mb-12">
        <h1 className="text-4xl sm:text-6xl font-black text-slate-900 dark:text-white">
          Simple, Transparent <br />
          <span className="bg-gradient-to-r from-red-500 via-rose-400 to-amber-400 bg-clip-text text-transparent">
            Creator-Friendly Pricing
          </span>
        </h1>
        <p className="mt-4 text-slate-600 dark:text-slate-400 font-medium text-base">
          Unlock maximum view growth with zero commitment. Cancel or upgrade anytime.
        </p>

        {/* Monthly / Yearly Toggle */}
        <div className="mt-8 inline-flex items-center gap-3 p-1.5 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <button
            onClick={() => setBillingCycle('monthly')}
            className={`px-5 py-2 rounded-xl text-xs font-bold transition-all ${
              billingCycle === 'monthly'
                ? 'bg-red-500 text-white shadow-md'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Monthly Billing
          </button>
          <button
            onClick={() => setBillingCycle('yearly')}
            className={`px-5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              billingCycle === 'yearly'
                ? 'bg-red-500 text-white shadow-md'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <span>Annual Billing</span>
            <span className="bg-amber-400 text-slate-950 text-[10px] font-black px-1.5 py-0.5 rounded-full uppercase">
              Save 20%
            </span>
          </button>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
        {plans.map((plan, idx) => {
          const price = billingCycle === 'yearly' ? plan.yearlyPrice : plan.monthlyPrice;
          return (
            <GlassCard
              key={idx}
              glow={plan.glow}
              className={`relative flex flex-col justify-between ${
                plan.popular ? 'border-2 border-red-500 shadow-2xl scale-105 z-10' : ''
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-red-600 to-amber-500 text-white text-[11px] font-black uppercase tracking-wider shadow-lg">
                  Most Popular for Creators
                </div>
              )}

              <div>
                <h3 className="text-2xl font-black text-slate-900 dark:text-white">{plan.name}</h3>
                <p className="mt-2 text-xs text-slate-500 dark:text-slate-400 font-medium h-10">
                  {plan.desc}
                </p>

                <div className="my-6 flex items-baseline gap-1">
                  <span className="text-4xl sm:text-5xl font-black text-slate-900 dark:text-white">
                    ${price}
                  </span>
                  <span className="text-xs text-slate-500 font-bold">/ month</span>
                </div>

                <div className="p-3 rounded-xl bg-red-500/10 text-red-500 text-xs font-bold mb-6 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  <span>{plan.credits}</span>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feat, fIdx) => (
                    <li key={fIdx} className="flex items-center gap-3 text-xs font-semibold text-slate-700 dark:text-slate-300">
                      <div className="p-1 rounded-md bg-emerald-500/10 text-emerald-500 flex-shrink-0">
                        <Check className="w-3.5 h-3.5" />
                      </div>
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <button
                onClick={() => {
                  showToast(`Selected ${plan.name} plan! Redirecting to checkout...`);
                  navigateTo('dashboard');
                }}
                className={`w-full py-3.5 rounded-xl text-xs font-black transition-all ${
                  plan.popular
                    ? 'bg-gradient-to-r from-red-600 to-amber-500 text-white shadow-lg shadow-red-500/30 hover:opacity-95'
                    : 'bg-slate-900 dark:bg-slate-800 text-white hover:bg-slate-800'
                }`}
              >
                {plan.cta}
              </button>
            </GlassCard>
          );
        })}
      </div>
    </div>
  );
};
