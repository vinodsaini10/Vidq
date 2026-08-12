export type PageId =
  | 'landing'
  | 'pricing'
  | 'features'
  | 'blog'
  | 'about'
  | 'contact'
  | 'login'
  | 'register'
  | 'forgot-password'
  | 'dashboard'
  | 'analytics'
  | 'keyword-research'
  | 'keyword-explorer'
  | 'video-seo'
  | 'ai-script'
  | 'ai-title'
  | 'description-generator'
  | 'tags-generator'
  | 'thumbnail-prompts'
  | 'competitors'
  | 'trends'
  | 'channel-overview'
  | 'video-performance'
  | 'content-calendar'
  | 'reports'
  | 'settings'
  | 'billing'
  | 'notifications'
  | 'support'
  | 'admin'
  | '404';

export interface ChannelStats {
  name: string;
  handle: string;
  subscribers: number;
  subscribersChange: number;
  viewsTotal: number;
  views30Days: number;
  viewsChange: number;
  watchTimeHours: number;
  estimatedRevenue: number;
  revenueChange: number;
  avgCtr: number;
  avgDuration: string;
  channelHealthScore: number;
  avatarUrl: string;
  bannerUrl: string;
  topNiche: string;
}

export interface VideoItem {
  id: string;
  title: string;
  thumbnail: string;
  publishedAt: string;
  views: number;
  likes: number;
  comments: number;
  ctr: number;
  avgWatchTime: string;
  retentionPercent: number;
  seoScore: number;
  status: 'Published' | 'Scheduled' | 'Draft';
  category: string;
  impressions: number;
}

export interface KeywordResult {
  keyword: string;
  searchVolume: number;
  competition: 'Low' | 'Medium' | 'High' | 'Very High';
  overallScore: number; // 0-100
  cpmEstimate: string;
  trendPercentage: number;
  searchIntent: 'Informational' | 'Commercial' | 'Navigational' | 'Transactional';
  topCompetitors: string[];
  relatedKeywords: string[];
}

export interface VideoSEOResult {
  title: string;
  seoScore: number; // 0-100
  titleScore: number;
  descriptionScore: number;
  tagsScore: number;
  thumbnailScore: number;
  recommendations: {
    id: string;
    type: 'success' | 'warning' | 'critical';
    title: string;
    description: string;
  }[];
  extractedTags: string[];
  missingPowerWords: string[];
  suggestedTitles: string[];
}

export interface AIScriptOutput {
  title: string;
  targetDuration: string;
  estimatedWordCount: number;
  hook: string;
  intro: string;
  mainPoints: {
    heading: string;
    scriptText: string;
    visualCue: string;
  }[];
  callToAction: string;
  outro: string;
}

export interface AITitleOption {
  id: string;
  title: string;
  ctrScore: number;
  style: 'Curiosity' | 'Urgency' | 'How-To' | 'Storytelling' | 'Authority';
  powerWord: string;
  charCount: number;
}

export interface CompetitorChannel {
  id: string;
  name: string;
  handle: string;
  avatar: string;
  subscribers: number;
  uploadFrequency: string; // e.g. "3.2 videos/week"
  avgViews: number;
  outlierVideo: {
    title: string;
    views: number;
    multiplier: string; // e.g. "4.8x channel avg"
  };
  contentGap: string;
  overlapScore: number;
}

export interface TrendTopic {
  id: string;
  topic: string;
  niche: string;
  velocityScore: number; // 0-100
  searchVolumeGrowth: string;
  topVideoExample: string;
  opportunityRating: 'High' | 'Extreme' | 'Moderate';
}

export interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  status: 'Idea' | 'Scripting' | 'Filming' | 'Editing' | 'Scheduled' | 'Published';
  niche: string;
  estimatedViews: string;
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  time: string;
  read: boolean;
  type: 'milestone' | 'alert' | 'ai' | 'system';
}

export interface BlogPost {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  category: string;
  readTime: string;
  publishedDate: string;
  author: {
    name: string;
    role: string;
    avatar: string;
  };
  image: string;
  content: string;
}

export interface UserProfile {
  name: string;
  email: string;
  avatar: string;
  plan: 'Free Creator' | 'Pro Creator' | 'Agency Studio';
  aiCreditsUsed: number;
  aiCreditsMax: number;
  connectedYoutubeAccount: boolean;
  theme: 'dark' | 'light';
  isAuthenticated?: boolean;
}
