import {
  ChannelStats,
  VideoItem,
  KeywordResult,
  CompetitorChannel,
  TrendTopic,
  CalendarEvent,
  NotificationItem,
  BlogPost,
  UserProfile,
} from '../types';

export const initialProfile: UserProfile = {
  name: '',
  email: '',
  avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250',
  plan: 'Pro Creator',
  aiCreditsUsed: 0,
  aiCreditsMax: 1000,
  connectedYoutubeAccount: false,
  theme: 'dark',
  isAuthenticated: false,
};

export const initialChannelStats: ChannelStats = {
  name: 'No Channel Connected',
  handle: '@connect_youtube',
  subscribers: 0,
  subscribersChange: 0,
  viewsTotal: 0,
  views30Days: 0,
  viewsChange: 0,
  watchTimeHours: 0,
  estimatedRevenue: 0,
  revenueChange: 0,
  avgCtr: 0,
  avgDuration: '0m 0s',
  channelHealthScore: 0,
  avatarUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=200',
  bannerUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=1200',
  topNiche: 'Uncategorized',
};

export const mockVideos: VideoItem[] = [];

export const mockKeywords: KeywordResult[] = [];

export const mockCompetitors: CompetitorChannel[] = [];

export const mockTrends: TrendTopic[] = [
  {
    id: 'tr-1',
    topic: 'YouTube Shorts Algorithm Updates 2026',
    niche: 'YouTube Growth',
    velocityScore: 94,
    searchVolumeGrowth: '+340%',
    topVideoExample: 'Shorts Virality Breakdown',
    opportunityRating: 'Extreme',
  },
  {
    id: 'tr-2',
    topic: 'AI Video Generators & Sora Workflows',
    niche: 'Artificial Intelligence',
    velocityScore: 89,
    searchVolumeGrowth: '+210%',
    topVideoExample: 'Complete Sora 2026 Guide',
    opportunityRating: 'High',
  },
];

export const mockCalendarEvents: CalendarEvent[] = [];

export const mockNotifications: NotificationItem[] = [
  {
    id: 'notif-1',
    title: 'Welcome to VidPulse AI',
    message: 'Connect your YouTube channel to fetch live channel statistics and video analytics.',
    time: 'Just now',
    read: false,
    type: 'system',
  },
];

export const mockBlogPosts: BlogPost[] = [
  {
    id: 'blog-1',
    slug: 'youtube-algorithm-2026-guide',
    title: 'Mastering the 2026 YouTube Algorithm: CTR, Retention & AI Distribution',
    excerpt: 'An in-depth analysis of YouTube\'s latest recommendation engine and how creators can double their organic reach.',
    category: 'Algorithm Strategy',
    readTime: '6 min read',
    publishedDate: 'August 10, 2026',
    author: {
      name: 'Alex Rivera',
      role: 'Head of Growth',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200',
    },
    image: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=800',
    content: 'Full article content on YouTube 2026 algorithm strategies...',
  },
];
