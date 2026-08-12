import React from 'react';
import { Sparkles, CheckCircle2 } from 'lucide-react';
import { useAppState } from '../../store/useStore';

export const Toast: React.FC = () => {
  const { toastMessage } = useAppState();

  if (!toastMessage) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-bounce">
      <div className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-slate-900 text-white dark:bg-white dark:text-slate-900 shadow-2xl border border-red-500/30">
        <div className="p-1.5 rounded-xl bg-red-500 text-white">
          <Sparkles className="w-4 h-4 animate-spin" />
        </div>
        <span className="text-xs font-bold">{toastMessage}</span>
        <CheckCircle2 className="w-4 h-4 text-emerald-400 dark:text-emerald-600" />
      </div>
    </div>
  );
};
