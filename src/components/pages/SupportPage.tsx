import React, { useState } from 'react';
import { HelpCircle, MessageSquare, BookOpen, Send, Sparkles, CheckCircle2 } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const SupportPage: React.FC = () => {
  const { showToast } = useAppState();
  const [ticketSubject, setTicketSubject] = useState('');
  const [ticketMessage, setTicketMessage] = useState('');

  const handleSubmitTicket = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticketSubject.trim() || !ticketMessage.trim()) return;
    showToast('Support ticket submitted! Response expected within 2 hours.');
    setTicketSubject('');
    setTicketMessage('');
  };

  const faqs = [
    {
      q: 'How does VidPulse AI estimate video CTR and viral potential?',
      a: 'We evaluate historical thumbnail contrast, title power-word density, search volume momentum, and competitor retention averages using custom neural network models.',
    },
    {
      q: 'Will using AI scripts get my YouTube channel penalized?',
      a: 'No. YouTube values high retention and engagement. VidPulse produces structured outlines, hook storytelling, and visual cues meant for humans to deliver naturally.',
    },
    {
      q: 'Can I connect multiple YouTube channels?',
      a: 'Yes! Pro Creator supports up to 3 channels, and Agency Studio supports up to 10 channels with seamless switching in the navbar.',
    },
  ];

  return (
    <div className="space-y-8 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2">
          <HelpCircle className="w-7 h-7 text-amber-500" />
          Support & Creator Knowledge Base
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
          24/7 priority assistance for Pro and Studio creators, algorithm guides, and API status.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-4">
          <h3 className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-red-500" />
            Frequently Asked Questions
          </h3>

          <div className="space-y-4">
            {faqs.map((faq, i) => (
              <GlassCard key={i} className="p-5 space-y-2">
                <h4 className="text-sm font-extrabold text-slate-900 dark:text-white">{faq.q}</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{faq.a}</p>
              </GlassCard>
            ))}
          </div>
        </div>

        <GlassCard className="p-6 space-y-4 self-start">
          <h3 className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-amber-500" />
            Submit Priority Ticket
          </h3>

          <form onSubmit={handleSubmitTicket} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">Subject</label>
              <input
                type="text"
                value={ticketSubject}
                onChange={(e) => setTicketSubject(e.target.value)}
                placeholder="e.g. Question regarding YouTube OAuth sync"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-amber-500"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">Issue Description</label>
              <textarea
                rows={4}
                value={ticketMessage}
                onChange={(e) => setTicketMessage(e.target.value)}
                placeholder="Describe what you need help with..."
                className="w-full px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-amber-500 resize-none"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full py-3 rounded-xl bg-gradient-to-r from-amber-500 to-red-500 text-slate-950 font-black text-xs shadow-lg shadow-amber-500/20 hover:opacity-95 transition-all flex items-center justify-center gap-2"
            >
              <Send className="w-4 h-4" />
              <span>Send Ticket to Engineering</span>
            </button>
          </form>
        </GlassCard>
      </div>
    </div>
  );
};
