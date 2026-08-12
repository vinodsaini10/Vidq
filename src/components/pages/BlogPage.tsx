import React, { useState } from 'react';
import { mockBlogPosts } from '../../data/mockData';
import { BlogPost } from '../../types';
import { GlassCard } from '../common/GlassCard';
import { Sparkles, Calendar, Clock, ArrowRight, X } from 'lucide-react';

export const BlogPage: React.FC = () => {
  const [selectedPost, setSelectedPost] = useState<BlogPost | null>(null);

  return (
    <div className="min-h-screen py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <h1 className="text-4xl sm:text-6xl font-black text-slate-900 dark:text-white">
          YouTube Growth Insights & <br />
          <span className="bg-gradient-to-r from-red-500 via-rose-400 to-amber-400 bg-clip-text text-transparent">
            Algorithm Strategy
          </span>
        </h1>
        <p className="mt-4 text-slate-600 dark:text-slate-400 font-medium text-base">
          Proven strategies, case studies, and AI research from the VidPulse engineering team.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {mockBlogPosts.map((post) => (
          <GlassCard key={post.id} className="overflow-hidden flex flex-col justify-between group">
            <div>
              <div className="relative h-48 rounded-xl overflow-hidden mb-5">
                <img
                  src={post.image}
                  alt={post.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <span className="absolute top-3 left-3 bg-red-600 text-white text-[10px] font-extrabold uppercase tracking-wider px-3 py-1 rounded-full shadow-lg">
                  {post.category}
                </span>
              </div>

              <div className="flex items-center gap-4 text-xs text-slate-400 mb-3 font-medium">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  {post.publishedDate}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {post.readTime}
                </span>
              </div>

              <h3 className="text-xl font-bold text-slate-900 dark:text-white leading-snug">
                {post.title}
              </h3>

              <p className="mt-3 text-xs text-slate-500 dark:text-slate-400 leading-relaxed line-clamp-3">
                {post.excerpt}
              </p>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <img
                  src={post.author.avatar}
                  alt={post.author.name}
                  className="w-7 h-7 rounded-full object-cover"
                />
                <div>
                  <span className="text-xs font-bold text-slate-900 dark:text-white block">
                    {post.author.name}
                  </span>
                  <span className="text-[10px] text-slate-400 block">{post.author.role}</span>
                </div>
              </div>

              <button
                onClick={() => setSelectedPost(post)}
                className="px-4 py-2 rounded-xl bg-red-500/10 text-red-500 font-bold text-xs hover:bg-red-500 hover:text-white transition-all flex items-center gap-1.5"
              >
                <span>Read Article</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </GlassCard>
        ))}
      </div>

      {/* Article Reader Modal */}
      {selectedPost && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-3xl w-full p-6 sm:p-10 border border-slate-200 dark:border-slate-800 shadow-2xl relative my-8">
            <button
              onClick={() => setSelectedPost(null)}
              className="absolute top-6 right-6 p-2 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-slate-900 dark:hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <span className="bg-red-500/10 text-red-500 text-xs font-bold px-3 py-1 rounded-full inline-block mb-4">
              {selectedPost.category}
            </span>

            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white leading-tight">
              {selectedPost.title}
            </h2>

            <div className="flex items-center gap-3 my-6 pt-4 border-t border-slate-200 dark:border-slate-800 text-xs text-slate-500">
              <img
                src={selectedPost.author.avatar}
                alt={selectedPost.author.name}
                className="w-8 h-8 rounded-full object-cover"
              />
              <div>
                <span className="font-bold text-slate-900 dark:text-white block">
                  {selectedPost.author.name}
                </span>
                <span>{selectedPost.publishedDate} · {selectedPost.readTime}</span>
              </div>
            </div>

            <div className="prose dark:prose-invert max-w-none text-sm text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
              {selectedPost.content}
            </div>

            <button
              onClick={() => setSelectedPost(null)}
              className="mt-8 w-full py-3 rounded-xl bg-red-600 text-white font-bold text-xs"
            >
              Close Article
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
