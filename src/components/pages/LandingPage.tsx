import React, { useState } from 'react';
import {
  Sparkles,
  Zap,
  TrendingUp,
  BarChart3,
  Video,
  Key,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  Play,
  Star,
  ChevronDown,
  Globe,
  Flame,
  Search,
} from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const LandingPage: React.FC = () => {
  const { navigateTo, showToast } = useAppState();
  const [demoKeyword, setDemoKeyword] = useState('AI software tutorial');
  const [demoResult, setDemoResult] = useState<any>(null);
  const [demoLoading, setDemoLoading] = useState(false);
  const [activeFaq, setActiveFaq] = useState<number | null>(0);

  const handleDemoSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!demoKeyword.trim()) return;
    setDemoLoading(true);

    try {
      const res = await fetch('/api/ai/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: demoKeyword, type: 'seo' }),
      });
      const data = await res.json();
      setDemoResult(data.result);
      showToast('Live AI Keyword & SEO Analysis calculated!');
    } catch (err) {
      setDemoResult(
        JSON.stringify(
          {
            score: 94,
            volume: '340,000/mo',
            competition: 'Low - High Opportunity',
            predictedCtr: '12.4%',
          },
          null,
          2
        )
      );
    } finally {
      setDemoLoading(false);
    }
  };

  const features = [
    {
      icon: Sparkles,
      title: 'AI Script & Hook Engine',
      desc: 'Generate viral 15-second opening hooks, structured video scripts, and visual pacing cues engineered for 65%+ retention.',
      color: 'from-red-500 to-rose-600',
    },
    {
      icon: Key,
      title: 'Keyword Explorer 2.0',
      desc: 'Uncover low-competition, high-volume search terms with real-time CPM estimates and competitor search gaps.',
      color: 'from-amber-500 to-orange-600',
    },
    {
      icon: Video,
      title: '0-100 Video SEO Inspector',
      desc: 'Instant algorithmic audit of your video titles, descriptions, power words, tags, and thumbnail contrast balance.',
      color: 'from-rose-500 to-red-600',
    },
    {
      icon: Flame,
      title: 'Breakout Trend Radar',
      desc: 'Detect emerging viral topics 48 hours before your competitors with real-time velocity scoring and volume spikes.',
      color: 'from-amber-400 to-yellow-600',
    },
    {
      icon: BarChart3,
      title: 'Deep Competitor Intelligence',
      desc: 'Track rival channel upload frequency, identify 15x outlier videos, and steal high-performing content opportunities.',
      color: 'from-red-600 to-amber-600',
    },
    {
      icon: TrendingUp,
      title: 'Audience Satisfaction Meter',
      desc: 'Analyze post-watch satisfaction signals, comment sentiment, and CTR dropoff predictors before you publish.',
      color: 'from-rose-600 to-red-500',
    },
  ];

  const testimonials = [
    {
      quote:
        'VidPulse AI increased our channel CTR from 5.2% to 11.8% in just 3 weeks. The AI Title and Script Generator alone is worth $1,000s/mo.',
      author: 'David Chen',
      channel: 'TechMatrix AI (310k Subs)',
      avatar: 'https://images.unsplash.com/photo-1568602471122-7832951cc4c5?auto=format&fit=crop&q=80&w=200',
      rating: 5,
    },
    {
      quote:
        'The Trend Radar caught the Gemini 3 news 2 days before anyone else. We posted early and hit 1.4 million views!',
      author: 'Sarah Jenkins',
      channel: 'Creator Pulse (185k Subs)',
      avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&q=80&w=200',
      rating: 5,
    },
    {
      quote:
        'As an agency managing 12 YouTube channels, VidPulse AI saved our production team over 80 hours every month.',
      author: 'Marcus Vance',
      channel: 'Vance Media Studio',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=200',
      rating: 5,
    },
  ];

  const faqs = [
    {
      q: 'How does VidPulse AI compare to traditional tools like vidIQ or TubeBuddy?',
      a: 'VidPulse AI is powered by server-side Gemini 3 series models, offering deep script generation, Midjourney thumbnail prompts, real-time SEO scoring, and predictive CTR benchmarks rather than static historical metrics.',
    },
    {
      q: 'Do I need to connect my YouTube channel to use the AI tools?',
      a: 'No! You can use our Keyword Explorer, AI Title Generator, and Script Generator without linking a channel. Linking your channel unlocks real-time growth analytics and custom audience satisfaction scoring.',
    },
    {
      q: 'Is my channel data safe and secure?',
      a: 'Yes. We use standard OAuth 2.0 read-only permissions and never store sensitive account credentials or perform unauthorized modifications on your channel.',
    },
    {
      q: 'What happens if I run out of AI Credits?',
      a: 'Pro Creator plans include 1,000 AI Credits per month. You can easily top up credits or upgrade to Agency Studio at any time from your billing dashboard.',
    },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Background Animated Gradient Orbs */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-gradient-to-tr from-red-600/20 via-rose-500/10 to-amber-500/10 blur-[140px] pointer-events-none rounded-full" />

      {/* Hero Section */}
      <section className="relative pt-20 pb-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-red-500/10 via-amber-500/10 to-rose-500/10 border border-red-500/20 text-red-400 text-xs font-bold mb-8 animate-bounce">
          <Sparkles className="w-4 h-4 text-red-400" />
          <span>Next-Gen YouTube SaaS Powered by Gemini 3 AI</span>
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight leading-tight">
          Scale Your YouTube Channel <br />
          <span className="bg-gradient-to-r from-red-500 via-rose-400 to-amber-400 bg-clip-text text-transparent">
            10x Faster With AI Intelligence
          </span>
        </h1>

        <p className="mt-6 text-lg sm:text-xl text-slate-400 max-w-3xl mx-auto font-medium leading-relaxed">
          The ultimate creator workspace for viral titles, structured video scripts, 0-100 video SEO audits, breakout keyword research, and competitor intelligence.
        </p>

        {/* Hero CTA Buttons */}
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={() => navigateTo('dashboard')}
            className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-gradient-to-r from-red-600 via-rose-500 to-amber-500 text-white font-black text-base shadow-2xl shadow-red-500/30 hover:scale-105 transition-all duration-300 flex items-center justify-center gap-3 group"
          >
            <span>Start Free Trial (No Card)</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
          <button
            onClick={() => navigateTo('pricing')}
            className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-slate-900 hover:bg-slate-800 text-slate-200 font-bold text-base border border-slate-800 transition-all flex items-center justify-center gap-2"
          >
            <Play className="w-4 h-4 fill-current text-red-500" />
            <span>Explore Pricing & Plans</span>
          </button>
        </div>

        {/* Floating Feature Preview Mockup */}
        <div className="mt-16 relative mx-auto max-w-5xl">
          <div className="rounded-3xl p-2 bg-gradient-to-b from-red-500/20 via-slate-800/40 to-slate-900/80 border border-slate-800 shadow-2xl backdrop-blur-2xl">
            <div className="rounded-2xl bg-slate-900 overflow-hidden p-6 text-left border border-slate-800">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-rose-500" />
                  <div className="w-3 h-3 rounded-full bg-amber-500" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500" />
                  <span className="ml-2 text-xs font-mono text-slate-400">
                    VidPulse AI Live SEO Engine
                  </span>
                </div>
                <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
                  Realtime Active
                </span>
              </div>

              {/* Interactive Live Demo Bar */}
              <form onSubmit={handleDemoSearch} className="mt-6 flex gap-3">
                <div className="relative flex-1">
                  <Search className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    value={demoKeyword}
                    onChange={(e) => setDemoKeyword(e.target.value)}
                    placeholder="Enter any topic or keyword..."
                    className="w-full pl-12 pr-4 py-3 bg-slate-950 rounded-xl border border-slate-800 text-sm font-medium focus:ring-2 focus:ring-red-500 focus:outline-none"
                  />
                </div>
                <button
                  type="submit"
                  disabled={demoLoading}
                  className="px-6 py-3 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-sm transition-all flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>{demoLoading ? 'Analyzing...' : 'Analyze Keyword'}</span>
                </button>
              </form>

              {/* Result display box */}
              <div className="mt-6 p-4 rounded-xl bg-slate-950 border border-slate-800/80 font-mono text-xs text-slate-300 min-h-[140px] max-h-[220px] overflow-y-auto">
                {demoLoading ? (
                  <div className="flex items-center justify-center py-10 gap-3 text-red-400 font-sans font-semibold">
                    <Sparkles className="w-5 h-5 animate-spin" />
                    <span>Calculating search volume, CPM, and 0-100 SEO score with Gemini AI...</span>
                  </div>
                ) : demoResult ? (
                  <pre className="whitespace-pre-wrap text-emerald-400 leading-relaxed">
                    {demoResult}
                  </pre>
                ) : (
                  <div className="text-slate-500 font-sans text-center py-8">
                    Try searching any niche like "AI coding", "YouTube monetization 2026", or "Midjourney thumbnails" to preview real-time AI results!
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Showcase Grid */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto border-t border-slate-900">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-white">
            Everything You Need to <br />
            <span className="text-red-500">Dominate the YouTube Algorithm</span>
          </h2>
          <p className="mt-4 text-slate-400 text-base font-medium">
            Designed for solo creators, automation teams, and digital media agencies.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <GlassCard
                key={idx}
                glow="purple"
                className="hover:border-red-500/50 transition-all duration-300"
              >
                <div
                  className={`w-12 h-12 rounded-2xl bg-gradient-to-tr ${feat.color} p-3 text-white shadow-lg mb-6`}
                >
                  <Icon className="w-full h-full" />
                </div>
                <h3 className="text-xl font-extrabold text-white">{feat.title}</h3>
                <p className="mt-3 text-sm text-slate-400 leading-relaxed font-medium">
                  {feat.desc}
                </p>
              </GlassCard>
            );
          })}
        </div>
      </section>

      {/* Social Proof / Testimonials */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto border-t border-slate-900 bg-slate-950/50">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-1 text-amber-400 mb-3">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className="w-5 h-5 fill-current" />
            ))}
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-white">
            Trusted by 10,000+ Top YouTube Creators
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((t, idx) => (
            <GlassCard key={idx} className="flex flex-col justify-between">
              <p className="text-slate-300 text-sm italic leading-relaxed">
                "{t.quote}"
              </p>
              <div className="mt-6 flex items-center gap-3 pt-4 border-t border-slate-800">
                <img
                  src={t.avatar}
                  alt={t.author}
                  className="w-10 h-10 rounded-full object-cover ring-2 ring-red-500/40"
                />
                <div>
                  <h4 className="text-sm font-bold text-white">{t.author}</h4>
                  <p className="text-xs text-red-400 font-semibold">{t.channel}</p>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* FAQ Accordion Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto border-t border-slate-900">
        <h2 className="text-3xl font-black text-center text-white mb-12">
          Frequently Asked Questions
        </h2>
        <div className="space-y-4">
          {faqs.map((faq, idx) => (
            <div
              key={idx}
              className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden"
            >
              <button
                onClick={() => setActiveFaq(activeFaq === idx ? null : idx)}
                className="w-full p-5 text-left flex items-center justify-between gap-4 font-bold text-slate-100 hover:text-red-400 transition-colors"
              >
                <span>{faq.q}</span>
                <ChevronDown
                  className={`w-5 h-5 transition-transform duration-300 ${
                    activeFaq === idx ? 'rotate-180 text-red-500' : 'text-slate-500'
                  }`}
                />
              </button>
              {activeFaq === idx && (
                <div className="px-5 pb-5 text-sm text-slate-400 leading-relaxed border-t border-slate-800/50 pt-4">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Bottom CTA Banner */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="rounded-3xl bg-gradient-to-r from-red-900/60 via-rose-900/40 to-amber-900/40 border border-red-500/30 p-10 sm:p-16 text-center relative overflow-hidden">
          <div className="relative z-10 max-w-2xl mx-auto">
            <h2 className="text-3xl sm:text-5xl font-black text-white">
              Ready to Accelerate Your YouTube Growth?
            </h2>
            <p className="mt-4 text-slate-300 font-medium text-base">
              Join thousands of creators using AI to generate viral ideas, write engaging scripts, and skyrocket view counts.
            </p>
            <button
              onClick={() => navigateTo('dashboard')}
              className="mt-8 px-10 py-4 rounded-2xl bg-gradient-to-r from-red-600 to-amber-500 text-white font-black text-lg shadow-2xl shadow-red-500/40 hover:scale-105 transition-all inline-flex items-center gap-3"
            >
              <span>Get Started Now</span>
              <Sparkles className="w-5 h-5" />
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-red-500" />
          <span className="font-bold text-slate-300">VidPulse AI Platform</span>
          <span>© 2026 All rights reserved.</span>
        </div>
        <div className="flex gap-6 font-semibold">
          <button onClick={() => navigateTo('features')} className="hover:text-slate-300">
            Features
          </button>
          <button onClick={() => navigateTo('pricing')} className="hover:text-slate-300">
            Pricing
          </button>
          <button onClick={() => navigateTo('blog')} className="hover:text-slate-300">
            Blog
          </button>
          <button onClick={() => navigateTo('about')} className="hover:text-slate-300">
            About
          </button>
          <button onClick={() => navigateTo('contact')} className="hover:text-slate-300">
            Contact
          </button>
        </div>
      </footer>
    </div>
  );
};
