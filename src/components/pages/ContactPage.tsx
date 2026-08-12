import React, { useState } from 'react';
import { Mail, MessageSquare, Phone, MapPin, Send, CheckCircle2 } from 'lucide-react';
import { GlassCard } from '../common/GlassCard';
import { useAppState } from '../../store/useStore';

export const ContactPage: React.FC = () => {
  const { showToast } = useAppState();
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({ name: '', email: '', subject: 'General Support', message: '' });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    showToast('Your message has been received! Our support team will reply within 2 hours.');
  };

  return (
    <div className="min-h-screen py-16 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto">
      <div className="text-center max-w-2xl mx-auto mb-16">
        <h1 className="text-4xl sm:text-5xl font-black text-slate-900 dark:text-white">
          Get in Touch With Our <br />
          <span className="bg-gradient-to-r from-red-500 via-rose-400 to-amber-400 bg-clip-text text-transparent">
            Creator Success Team
          </span>
        </h1>
        <p className="mt-4 text-slate-600 dark:text-slate-400 font-medium text-base">
          Have questions about your channel growth, billing, or enterprise studio plans? We are here to help.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="space-y-6">
          <GlassCard className="flex items-center gap-4 p-5">
            <div className="p-3 rounded-xl bg-red-500/10 text-red-500">
              <Mail className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase">Support Email</h4>
              <p className="text-sm font-bold text-slate-900 dark:text-white mt-0.5">support@vidpulse.ai</p>
            </div>
          </GlassCard>

          <GlassCard className="flex items-center gap-4 p-5">
            <div className="p-3 rounded-xl bg-amber-500/10 text-amber-500">
              <MessageSquare className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase">Live Creator Chat</h4>
              <p className="text-sm font-bold text-slate-900 dark:text-white mt-0.5">Available 24/7 for Pro Users</p>
            </div>
          </GlassCard>

          <GlassCard className="flex items-center gap-4 p-5">
            <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-500">
              <MapPin className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase">Headquarters</h4>
              <p className="text-sm font-bold text-slate-900 dark:text-white mt-0.5">San Francisco, CA & Tokyo</p>
            </div>
          </GlassCard>
        </div>

        <GlassCard className="lg:col-span-2 p-8">
          {submitted ? (
            <div className="text-center py-12">
              <CheckCircle2 className="w-16 h-16 text-emerald-500 mx-auto mb-4 animate-bounce" />
              <h3 className="text-2xl font-black text-slate-900 dark:text-white">Message Sent!</h3>
              <p className="mt-2 text-xs text-slate-500 font-medium">
                Thank you for contacting VidPulse AI. An account specialist will reach out shortly.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                    Your Name
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Alex Rivera"
                    className="w-full px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-medium focus:ring-2 focus:ring-red-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="alex@vidpulse.ai"
                    className="w-full px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-medium focus:ring-2 focus:ring-red-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                  Subject
                </label>
                <select
                  value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-medium focus:ring-2 focus:ring-red-500 focus:outline-none"
                >
                  <option>General Support</option>
                  <option>Enterprise / Agency Demo</option>
                  <option>Billing & Credits Query</option>
                  <option>Feature Request</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
                  Message
                </label>
                <textarea
                  required
                  rows={4}
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  placeholder="How can we help your channel scale today?"
                  className="w-full px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-medium focus:ring-2 focus:ring-red-500 focus:outline-none"
                />
              </div>

              <button
                type="submit"
                className="w-full py-3.5 rounded-xl bg-gradient-to-r from-red-600 to-amber-500 text-white font-bold text-xs shadow-lg shadow-red-500/25 hover:opacity-95 transition-all flex items-center justify-center gap-2"
              >
                <Send className="w-4 h-4" />
                <span>Send Message</span>
              </button>
            </form>
          )}
        </GlassCard>
      </div>
    </div>
  );
};
