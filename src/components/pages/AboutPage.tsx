import React from 'react';
import { Sparkles, Shield, Rocket, Heart, Award, Users } from 'lucide-react';
import { GlassCard } from '../common/GlassCard';

export const AboutPage: React.FC = () => {
  return (
    <div className="min-h-screen py-16 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <h1 className="text-4xl sm:text-6xl font-black text-slate-900 dark:text-white">
          Our Mission: Empowering <br />
          <span className="bg-gradient-to-r from-red-500 via-rose-400 to-amber-400 bg-clip-text text-transparent">
            The Next Generation of Creators
          </span>
        </h1>
        <p className="mt-4 text-slate-600 dark:text-slate-400 font-medium text-base">
          VidPulse AI was engineered to democratize elite YouTube growth algorithms, scriptwriting techniques, and visual CTR psychology for creators worldwide.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
        <GlassCard className="text-center p-8">
          <div className="w-12 h-12 mx-auto rounded-2xl bg-red-500/10 text-red-500 flex items-center justify-center mb-4">
            <Rocket className="w-6 h-6" />
          </div>
          <h3 className="text-3xl font-black text-slate-900 dark:text-white">100M+</h3>
          <p className="text-xs text-slate-500 font-bold mt-1">Monthly Organic Views Generated</p>
        </GlassCard>

        <GlassCard className="text-center p-8">
          <div className="w-12 h-12 mx-auto rounded-2xl bg-amber-500/10 text-amber-500 flex items-center justify-center mb-4">
            <Users className="w-6 h-6" />
          </div>
          <h3 className="text-3xl font-black text-slate-900 dark:text-white">14,200+</h3>
          <p className="text-xs text-slate-500 font-bold mt-1">Active YouTubers & Agencies</p>
        </GlassCard>

        <GlassCard className="text-center p-8">
          <div className="w-12 h-12 mx-auto rounded-2xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center mb-4">
            <Award className="w-6 h-6" />
          </div>
          <h3 className="text-3xl font-black text-slate-900 dark:text-white">98.4%</h3>
          <p className="text-xs text-slate-500 font-bold mt-1">Script & SEO Satisfaction Rate</p>
        </GlassCard>
      </div>

      <GlassCard className="p-8 sm:p-12 mb-12">
        <h2 className="text-2xl font-black text-slate-900 dark:text-white mb-4">
          Why We Built VidPulse AI
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed space-y-4 font-medium">
          Creating high-performing YouTube content used to require a team of full-time researchers, SEO consultants, scriptwriters, and thumbnail designers. Solo creators were left at a huge disadvantage against major media studios.
          <br /><br />
          We combined cutting-edge Gemini 3 AI model capabilities with real-time YouTube recommendation telemetry to build a platform that acts as your 24/7 Chief Growth Officer.
        </p>
      </GlassCard>
    </div>
  );
};
