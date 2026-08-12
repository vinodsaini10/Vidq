import React from 'react';

interface SEOProgressBarProps {
  score: number; // 0 to 100
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  label?: string;
}

export const SEOProgressBar: React.FC<SEOProgressBarProps> = ({
  score,
  size = 'md',
  showLabel = true,
  label = 'SEO Score',
}) => {
  const getScoreColor = (val: number) => {
    if (val >= 90) return { stroke: '#10B981', text: 'text-emerald-500', bg: 'bg-emerald-500/10' };
    if (val >= 75) return { stroke: '#3B82F6', text: 'text-blue-500', bg: 'bg-blue-500/10' };
    if (val >= 50) return { stroke: '#F59E0B', text: 'text-amber-500', bg: 'bg-amber-500/10' };
    return { stroke: '#EF4444', text: 'text-red-500', bg: 'bg-red-500/10' };
  };

  const colors = getScoreColor(score);
  const strokeWidth = size === 'lg' ? 8 : size === 'md' ? 6 : 4;
  const radius = size === 'lg' ? 42 : size === 'md' ? 30 : 20;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const dimension = size === 'lg' ? 'w-24 h-24' : size === 'md' ? 'w-18 h-18' : 'w-12 h-12';
  const fontSize = size === 'lg' ? 'text-2xl font-black' : size === 'md' ? 'text-lg font-bold' : 'text-xs font-bold';

  return (
    <div className="flex flex-col items-center justify-center">
      <div className={`relative flex items-center justify-center ${dimension}`}>
        <svg className="w-full h-full transform -rotate-90">
          {/* Background circle */}
          <circle
            cx="50%"
            cy="50%"
            r={radius}
            className="stroke-slate-200 dark:stroke-slate-800"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx="50%"
            cy="50%"
            r={radius}
            stroke={colors.stroke}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <span className={`absolute ${fontSize} ${colors.text}`}>{score}</span>
      </div>
      {showLabel && (
        <span className="mt-1 text-xs font-semibold text-slate-500 dark:text-slate-400">
          {label}
        </span>
      )}
    </div>
  );
};
