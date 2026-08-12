import React, { useState } from 'react';
import { Calendar as CalendarIcon, Plus, Sparkles, Clock, CheckCircle2, Video, ChevronLeft, ChevronRight } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const ContentCalendarPage: React.FC = () => {
  const { calendarEvents, setCalendarEvents, showToast, navigateTo } = useAppState();
  const [showNewModal, setShowNewModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDate, setNewDate] = useState('2025-06-20');
  const [newStatus, setNewStatus] = useState<'Idea' | 'Scripting' | 'Filming' | 'Editing' | 'Scheduled' | 'Published'>('Idea');
  const [newNiche, setNewNiche] = useState('AI & Tech');

  const handleAddEvent = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    const newEv = {
      id: `ev-${Date.now()}`,
      title: newTitle,
      date: newDate,
      status: newStatus,
      niche: newNiche,
      estimatedViews: '15,000+',
    };

    setCalendarEvents([newEv, ...calendarEvents]);
    showToast(`Added "${newTitle}" to Content Planner!`);
    setNewTitle('');
    setShowNewModal(false);
  };

  const statusColors = {
    Idea: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
    Scripting: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
    Filming: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
    Editing: 'bg-rose-500/10 text-rose-500 border-rose-500/20',
    Scheduled: 'bg-cyan-500/10 text-cyan-500 border-cyan-500/20',
    Published: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  };

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2">
            <CalendarIcon className="w-7 h-7 text-red-500" />
            AI Content Planner & Calendar
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
            Schedule uploads, track production pipelines, and auto-sync script drafts to your YouTube release schedule.
          </p>
        </div>

        <button
          onClick={() => setShowNewModal(true)}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-red-600 to-amber-500 text-white font-bold text-xs shadow-lg shadow-red-500/20 hover:opacity-95 transition-all flex items-center gap-2 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Plan New Video</span>
        </button>
      </div>

      {/* Grid of Planned Videos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {calendarEvents.map((ev) => (
          <GlassCard key={ev.id} className="p-6 space-y-4 hover:border-red-500/40 transition-all flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className={`text-[10px] font-black uppercase tracking-wider px-2.5 py-1 rounded-full border ${statusColors[ev.status]}`}>
                  {ev.status}
                </span>
                <span className="text-xs font-bold text-slate-400 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {ev.date}
                </span>
              </div>

              <h3 className="text-base font-extrabold text-slate-900 dark:text-white leading-snug">
                {ev.title}
              </h3>

              <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 pt-2 border-t border-slate-200 dark:border-slate-800">
                <span>Niche: <strong className="text-slate-800 dark:text-slate-200">{ev.niche}</strong></span>
                <span>Est. Views: <strong className="text-emerald-500">{ev.estimatedViews}</strong></span>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2">
              <button
                onClick={() => {
                  showToast(`Opening script writer for "${ev.title}"`);
                  navigateTo('ai-script');
                }}
                className="w-full py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-red-500 hover:text-white text-slate-700 dark:text-slate-300 font-bold text-xs transition-all flex items-center justify-center gap-1.5"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Write Script</span>
              </button>
            </div>
          </GlassCard>
        ))}
      </div>

      {/* Modal */}
      {showNewModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-md">
          <div className="w-full max-w-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4">
            <h3 className="text-lg font-black text-slate-900 dark:text-white">Plan New Video Content</h3>

            <form onSubmit={handleAddEvent} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">
                  Video Working Title
                </label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. 10 AI Tools That Will Replace Programmers"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-red-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">
                    Target Release Date
                  </label>
                  <input
                    type="date"
                    value={newDate}
                    onChange={(e) => setNewDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-semibold"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">
                    Pipeline Stage
                  </label>
                  <select
                    value={newStatus}
                    onChange={(e: any) => setNewStatus(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-semibold"
                  >
                    <option value="Idea">Idea</option>
                    <option value="Scripting">Scripting</option>
                    <option value="Filming">Filming</option>
                    <option value="Editing">Editing</option>
                    <option value="Scheduled">Scheduled</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowNewModal(false)}
                  className="px-4 py-2 text-xs font-bold text-slate-400 hover:text-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-red-500 text-white font-bold text-xs shadow-lg shadow-red-500/20 hover:bg-red-600"
                >
                  Save to Calendar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
