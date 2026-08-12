import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  PageId,
  ChannelStats,
  VideoItem,
  KeywordResult,
  CompetitorChannel,
  TrendTopic,
  CalendarEvent,
  NotificationItem,
  UserProfile,
} from '../types';
import {
  initialProfile,
  initialChannelStats,
  mockVideos,
  mockKeywords,
  mockCompetitors,
  mockTrends,
  mockCalendarEvents,
  mockNotifications,
} from '../data/mockData';

interface AppStateContextType {
  currentPage: PageId;
  navigateTo: (page: PageId) => void;
  isDarkMode: boolean;
  toggleDarkMode: () => void;
  sidebarOpen: boolean;
  setSidebarOpen: React.Dispatch<React.SetStateAction<boolean>>;
  userProfile: UserProfile;
  setUserProfile: React.Dispatch<React.SetStateAction<UserProfile>>;
  channelStats: ChannelStats;
  setChannelStats: React.Dispatch<React.SetStateAction<ChannelStats>>;
  videos: VideoItem[];
  setVideos: React.Dispatch<React.SetStateAction<VideoItem[]>>;
  keywords: KeywordResult[];
  competitors: CompetitorChannel[];
  trends: TrendTopic[];
  calendarEvents: CalendarEvent[];
  setCalendarEvents: React.Dispatch<React.SetStateAction<CalendarEvent[]>>;
  notifications: NotificationItem[];
  markNotificationRead: (id: string) => void;
  clearAllNotifications: () => void;
  globalSearch: string;
  setGlobalSearch: (term: string) => void;
  toastMessage: string | null;
  showToast: (msg: string) => void;
  activeVideoFilter: string;
  setActiveVideoFilter: (filter: string) => void;
  logout: () => void;
}

const AppStateContext = createContext<AppStateContextType | undefined>(undefined);

export const AppStateProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentPage, setCurrentPage] = useState<PageId>('landing');
  const [isDarkMode, setIsDarkMode] = useState<boolean>(true);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [userProfile, setUserProfile] = useState<UserProfile>(initialProfile);
  const [channelStats, setChannelStats] = useState<ChannelStats>(initialChannelStats);
  const [videos, setVideos] = useState<VideoItem[]>(mockVideos);
  const [keywords] = useState<KeywordResult[]>(mockKeywords);
  const [competitors] = useState<CompetitorChannel[]>(mockCompetitors);
  const [trends] = useState<TrendTopic[]>(mockTrends);
  const [calendarEvents, setCalendarEvents] = useState<CalendarEvent[]>(mockCalendarEvents);
  const [notifications, setNotifications] = useState<NotificationItem[]>(mockNotifications);
  const [globalSearch, setGlobalSearch] = useState<string>('');
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [activeVideoFilter, setActiveVideoFilter] = useState<string>('All');

  // Check URL params for OAuth callback output or saved session token
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const authToken = urlParams.get('auth_token');
    const urlEmail = urlParams.get('email');
    const urlName = urlParams.get('name');
    const channelConnected = urlParams.get('channel_connected');

    if (authToken) {
      localStorage.setItem('token', authToken);
      setUserProfile({
        name: urlName || 'Google Creator',
        email: urlEmail || '',
        avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250',
        plan: 'Pro Creator',
        aiCreditsUsed: 0,
        aiCreditsMax: 1000,
        connectedYoutubeAccount: channelConnected === 'true',
        theme: 'dark',
        isAuthenticated: true,
      });
      showToast('Successfully authenticated with Google / Gmail!');
      setCurrentPage('dashboard');
      window.history.replaceState({}, document.title, window.location.pathname);
    } else {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        fetch('/api/v1/auth/me', {
          headers: { Authorization: `Bearer ${storedToken}` },
        })
          .then((res) => (res.ok ? res.json() : null))
          .then((userData) => {
            if (userData) {
              setUserProfile({
                name: userData.full_name || userData.email?.split('@')[0] || 'Creator',
                email: userData.email || '',
                avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250',
                plan: 'Pro Creator',
                aiCreditsUsed: 0,
                aiCreditsMax: 1000,
                connectedYoutubeAccount: Boolean(userData.youtube_channel_id),
                theme: 'dark',
                isAuthenticated: true,
              });
            }
          })
          .catch(() => {});
      }
    }
  }, []);

  // Fetch connected channels if authenticated
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (userProfile.isAuthenticated && token) {
      fetch('/api/v1/youtube/channels', {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => {
          if (data?.data && data.data.length > 0) {
            const ch = data.data[0];
            setChannelStats({
              name: ch.title || 'Connected Channel',
              handle: ch.custom_url || '@channel',
              subscribers: ch.subscriber_count || 0,
              subscribersChange: 0,
              viewsTotal: ch.view_count || 0,
              views30Days: ch.view_count || 0,
              viewsChange: 0,
              watchTimeHours: 0,
              estimatedRevenue: 0,
              revenueChange: 0,
              avgCtr: 0,
              avgDuration: '0m 0s',
              channelHealthScore: 90,
              avatarUrl: ch.thumbnail_url || 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=200',
              bannerUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=1200',
              topNiche: 'YouTube Strategy',
            });
            setUserProfile((prev) => ({ ...prev, connectedYoutubeAccount: true }));
          }
        })
        .catch(() => {});
    }
  }, [userProfile.isAuthenticated]);

  // Handle Theme switching
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const navigateTo = (page: PageId) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const toggleDarkMode = () => {
    setIsDarkMode((prev) => !prev);
  };

  const markNotificationRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 3500);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUserProfile({ ...initialProfile, isAuthenticated: false });
    showToast('Signed out successfully.');
    setCurrentPage('login');
  };

  return (
    <AppStateContext.Provider
      value={{
        currentPage,
        navigateTo,
        isDarkMode,
        toggleDarkMode,
        sidebarOpen,
        setSidebarOpen,
        userProfile,
        setUserProfile,
        channelStats,
        setChannelStats,
        videos,
        setVideos,
        keywords,
        competitors,
        trends,
        calendarEvents,
        setCalendarEvents,
        notifications,
        markNotificationRead,
        clearAllNotifications,
        globalSearch,
        setGlobalSearch,
        toastMessage,
        showToast,
        activeVideoFilter,
        setActiveVideoFilter,
        logout,
      }}
    >
      {children}
    </AppStateContext.Provider>
  );
};

export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error('useAppState must be used within an AppStateProvider');
  }
  return context;
};
