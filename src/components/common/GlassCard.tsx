import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  glow?: 'purple' | 'emerald' | 'amber' | 'blue' | 'none';
  hoverEffect?: boolean;
  onClick?: () => void;
  id?: string;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  glow = 'none',
  hoverEffect = true,
  onClick,
  id,
}) => {
  const glowStyles = {
    purple: 'shadow-[0_0_25px_rgba(168,85,247,0.15)] border-purple-500/20 dark:border-purple-500/30',
    emerald: 'shadow-[0_0_25px_rgba(16,185,129,0.15)] border-emerald-500/20 dark:border-emerald-500/30',
    amber: 'shadow-[0_0_25px_rgba(245,158,11,0.15)] border-amber-500/20 dark:border-amber-500/30',
    blue: 'shadow-[0_0_25px_rgba(59,130,246,0.15)] border-blue-500/20 dark:border-blue-500/30',
    none: 'border-slate-200/80 dark:border-slate-800/80',
  };

  return (
    <div
      id={id}
      onClick={onClick}
      className={`
        relative rounded-2xl p-6 backdrop-blur-xl transition-all duration-300
        bg-white/80 dark:bg-slate-900/80
        text-slate-900 dark:text-slate-100
        border ${glowStyles[glow]}
        ${hoverEffect ? 'hover:-translate-y-1 hover:shadow-xl hover:border-red-500/40 dark:hover:border-red-500/40' : ''}
        ${onClick ? 'cursor-pointer' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
};
