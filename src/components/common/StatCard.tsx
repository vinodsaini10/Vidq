import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';
import { GlassCard } from './GlassCard';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon: LucideIcon;
  iconBg?: string;
  glow?: 'purple' | 'emerald' | 'amber' | 'blue' | 'none';
  subtitle?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  changeLabel = 'vs last 30d',
  icon: Icon,
  iconBg = 'bg-red-500/10 text-red-500',
  glow = 'none',
  subtitle,
}) => {
  const isPositive = change !== undefined && change >= 0;

  return (
    <GlassCard glow={glow} className="relative overflow-hidden group">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</span>
        <div className={`p-2.5 rounded-xl ${iconBg} transition-transform group-hover:scale-110 duration-300`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-4 flex items-baseline justify-between">
        <h3 className="text-2xl lg:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
          {value}
        </h3>

        {change !== undefined && (
          <div
            className={`flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full ${
              isPositive
                ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20'
            }`}
          >
            {isPositive ? (
              <TrendingUp className="w-3.5 h-3.5" />
            ) : (
              <TrendingDown className="w-3.5 h-3.5" />
            )}
            <span>
              {isPositive ? '+' : ''}
              {change}%
            </span>
          </div>
        )}
      </div>

      {(changeLabel || subtitle) && (
        <p className="mt-2 text-xs text-slate-500 dark:text-slate-400 font-medium">
          {subtitle || changeLabel}
        </p>
      )}
    </GlassCard>
  );
};
