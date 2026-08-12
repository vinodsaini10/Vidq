import React, { useState } from 'react';
import {
  Sparkles,
  Search,
  Bell,
  Sun,
  Moon,
  ChevronDown,
  User,
  Settings,
  CreditCard,
  LogOut,
  Zap,
  Menu,
  X,
  Check,
  Video,
  FileText,
  Key,
  Flame,
  LayoutDashboard,
} from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { PageId } from '../../types';

export const Navbar: React.FC = () => {
  const {
    currentPage,
    navigateTo,
    isDarkMode,
    toggleDarkMode,
    sidebarOpen,
    setSidebarOpen,
    userProfile,
    notifications,
    markNotificationRead,
    clearAllNotifications,
    globalSearch,
    setGlobalSearch,
    logout,
  } = useAppState();

  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showQuickAi, setShowQuickAi] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const isPublicPage = [
    'landing',
    'pricing',
    'features',
    'blog',
    'about',
    'contact',
    'login',
    'register',
    'forgot-password',
  ].includes(currentPage);

  const navLinks: { id: PageId; label: string }[] = [
    { id: 'landing', label: 'Home' },
    { id: 'features', label: 'Features' },
    { id: 'pricing', label: 'Pricing' },
    { id: 'blog', label: 'Blog' },
    { id: 'about', label: 'About' },
    { id: 'contact', label: 'Contact' },
  ];

  const quickAiTools: { id: PageId; label: string; icon: any; desc: string }[] = [
    { id: 'ai-title', label: 'AI Title Generator', icon: Sparkles, desc: 'Generate high CTR titles' },
    { id: 'ai-script', label: 'AI Script Generator', icon: FileText, desc: 'Full structured scripts' },
    { id: 'video-seo', label: 'Video SEO Inspector', icon: Video, desc: 'Audit SEO score 0-100' },
    { id: 'keyword-research', label: 'Keyword Research', icon: Key, desc: 'Search volume & competition' },
    { id: 'trends', label: 'Trend Explorer', icon: Flame, desc: 'Viral breakout topics' },
  ];

  return (
    <header className="sticky top-0 z-40 w-full backdrop-blur-xl bg-white/70 dark:bg-slate-950/70 border-b border-slate-200/80 dark:border-slate-800/80 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Left Side: Brand & Sidebar Toggle */}
        <div className="flex items-center gap-3">
          {!isPublicPage && (
            <button
              onClick={() => setSidebarOpen((prev) => !prev)}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Toggle Sidebar"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          )}

          <div
            onClick={() => navigateTo(isPublicPage ? 'landing' : 'dashboard')}
            className="flex items-center gap-2.5 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-red-600 via-rose-500 to-amber-500 p-0.5 shadow-lg shadow-red-500/20 group-hover:scale-105 transition-transform duration-300">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-red-500 animate-pulse" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-black tracking-tight bg-gradient-to-r from-red-500 via-rose-400 to-amber-400 bg-clip-text text-transparent">
                VidPulse <span className="text-slate-900 dark:text-white font-bold">AI</span>
              </span>
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest -mt-1 hidden sm:block">
                YouTube Growth Engine
              </span>
            </div>
          </div>
        </div>

        {/* Middle Navigation / Global Search */}
        {isPublicPage ? (
          <nav className="hidden md:flex items-center gap-1 bg-slate-100/80 dark:bg-slate-900/80 px-3 py-1.5 rounded-full border border-slate-200/80 dark:border-slate-800">
            {navLinks.map((link) => (
              <button
                key={link.id}
                onClick={() => navigateTo(link.id)}
                className={`px-3.5 py-1.5 rounded-full text-sm font-semibold transition-all duration-200 ${
                  currentPage === link.id
                    ? 'bg-red-500 text-white shadow-md shadow-red-500/20'
                    : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/50 dark:hover:bg-slate-800/50'
                }`}
              >
                {link.label}
              </button>
            ))}
          </nav>
        ) : (
          <div className="hidden sm:flex flex-1 max-w-md mx-4 relative">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={globalSearch}
              onChange={(e) => setGlobalSearch(e.target.value)}
              placeholder="Search keywords, videos, titles, or AI tools..."
              className="w-full pl-10 pr-12 py-2 text-sm rounded-full bg-slate-100/90 dark:bg-slate-900/90 border border-slate-200/80 dark:border-slate-800 focus:outline-none focus:ring-2 focus:ring-red-500/50 text-slate-900 dark:text-slate-100 placeholder-slate-400 transition-all"
            />
            <kbd className="absolute right-3 top-1/2 -translate-y-1/2 hidden md:inline-flex items-center px-2 py-0.5 text-[10px] font-medium text-slate-400 bg-slate-200/60 dark:bg-slate-800 rounded">
              ⌘K
            </kbd>
          </div>
        )}

        {/* Right Side Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Theme Toggle */}
          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-xl text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {isDarkMode ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-slate-700" />}
          </button>

          {!isPublicPage && (
            <>
              {/* Quick AI Tools Dropdown */}
              <div className="relative hidden md:block">
                <button
                  onClick={() => {
                    setShowQuickAi(!showQuickAi);
                    setShowNotifications(false);
                    setShowProfileMenu(false);
                  }}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-gradient-to-r from-red-500 to-rose-600 text-white font-semibold text-xs shadow-md shadow-red-500/20 hover:opacity-95 transition-all"
                >
                  <Zap className="w-3.5 h-3.5" />
                  <span>AI Tools</span>
                  <ChevronDown className="w-3 h-3" />
                </button>

                {showQuickAi && (
                  <div className="absolute right-0 mt-2 w-64 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xl p-2 z-50">
                    <div className="px-3 py-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                      Quick AI Suite
                    </div>
                    {quickAiTools.map((tool) => {
                      const Icon = tool.icon;
                      return (
                        <button
                          key={tool.id}
                          onClick={() => {
                            navigateTo(tool.id);
                            setShowQuickAi(false);
                          }}
                          className="w-full text-left flex items-start gap-3 p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800/80 transition-colors group"
                        >
                          <div className="p-2 rounded-lg bg-red-500/10 text-red-500 group-hover:bg-red-500 group-hover:text-white transition-colors">
                            <Icon className="w-4 h-4" />
                          </div>
                          <div>
                            <div className="text-xs font-bold text-slate-900 dark:text-slate-100">
                              {tool.label}
                            </div>
                            <div className="text-[11px] text-slate-500 dark:text-slate-400">
                              {tool.desc}
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Notifications Bell */}
              <div className="relative">
                <button
                  onClick={() => {
                    setShowNotifications(!showNotifications);
                    setShowQuickAi(false);
                    setShowProfileMenu(false);
                  }}
                  className="p-2 rounded-xl text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 relative transition-colors"
                >
                  <Bell className="w-5 h-5" />
                  {unreadCount > 0 && (
                    <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-red-500 rounded-full ring-2 ring-white dark:ring-slate-950 animate-pulse" />
                  )}
                </button>

                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xl p-4 z-50">
                    <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
                      <h4 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <Bell className="w-4 h-4 text-red-500" />
                        Notifications ({notifications.length})
                      </h4>
                      <button
                        onClick={clearAllNotifications}
                        className="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 font-medium"
                      >
                        Clear All
                      </button>
                    </div>

                    <div className="max-h-72 overflow-y-auto my-2 space-y-2">
                      {notifications.length === 0 ? (
                        <div className="text-center py-6 text-xs text-slate-400">
                          No new notifications
                        </div>
                      ) : (
                        notifications.map((notif) => (
                          <div
                            key={notif.id}
                            onClick={() => markNotificationRead(notif.id)}
                            className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                              notif.read
                                ? 'bg-slate-50 dark:bg-slate-900/40 border-slate-200/50 dark:border-slate-800/50 opacity-70'
                                : 'bg-red-500/5 dark:bg-red-500/10 border-red-500/20'
                            }`}
                          >
                            <div className="flex items-center justify-between font-semibold text-slate-900 dark:text-slate-100">
                              <span>{notif.title}</span>
                              <span className="text-[10px] text-slate-400">{notif.time}</span>
                            </div>
                            <p className="mt-1 text-slate-600 dark:text-slate-300 leading-relaxed">
                              {notif.message}
                            </p>
                          </div>
                        ))
                      )}
                    </div>

                    <button
                      onClick={() => {
                        navigateTo('notifications');
                        setShowNotifications(false);
                      }}
                      className="w-full text-center py-2 text-xs font-bold text-red-500 hover:text-red-600 border-t border-slate-200 dark:border-slate-800"
                    >
                      View All Notifications
                    </button>
                  </div>
                )}
              </div>
            </>
          )}

          {/* User Profile or Public Auth Buttons */}
          {isPublicPage ? (
            <div className="flex items-center gap-2">
              <button
                onClick={() => navigateTo('login')}
                className="px-4 py-2 rounded-xl text-xs font-bold text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
              >
                Sign In
              </button>
              <button
                onClick={() => navigateTo('dashboard')}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-red-600 to-amber-500 text-white font-bold text-xs shadow-lg shadow-red-500/25 hover:opacity-95 transition-all flex items-center gap-1.5"
              >
                <span>Launch Platform</span>
                <Sparkles className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <div className="relative">
              <button
                onClick={() => {
                  setShowProfileMenu(!showProfileMenu);
                  setShowNotifications(false);
                  setShowQuickAi(false);
                }}
                className="flex items-center gap-2 p-1 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <img
                  src={userProfile.avatar}
                  alt={userProfile.name}
                  className="w-8 h-8 rounded-lg object-cover ring-2 ring-red-500/30"
                />
                <div className="hidden lg:flex flex-col text-left">
                  <span className="text-xs font-bold text-slate-900 dark:text-white leading-none">
                    {userProfile.name}
                  </span>
                  <span className="text-[10px] font-semibold text-red-500 leading-none mt-1">
                    {userProfile.plan}
                  </span>
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400 hidden lg:block" />
              </button>

              {showProfileMenu && (
                <div className="absolute right-0 mt-2 w-56 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xl p-2 z-50">
                  <div className="p-3 border-b border-slate-200 dark:border-slate-800">
                    <p className="text-xs font-bold text-slate-900 dark:text-white">
                      {userProfile.name}
                    </p>
                    <p className="text-[11px] text-slate-400 truncate">{userProfile.email}</p>
                    <div className="mt-2 text-[10px] bg-red-500/10 text-red-500 font-bold px-2 py-0.5 rounded-full inline-block">
                      {userProfile.plan}
                    </div>
                  </div>

                  <div className="py-1">
                    <button
                      onClick={() => {
                        navigateTo('settings');
                        setShowProfileMenu(false);
                      }}
                      className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
                    >
                      <User className="w-4 h-4 text-slate-400" />
                      <span>Channel & Account</span>
                    </button>
                    <button
                      onClick={() => {
                        navigateTo('billing');
                        setShowProfileMenu(false);
                      }}
                      className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
                    >
                      <CreditCard className="w-4 h-4 text-slate-400" />
                      <span>Billing & AI Credits</span>
                    </button>
                    <button
                      onClick={() => {
                        navigateTo('admin');
                        setShowProfileMenu(false);
                      }}
                      className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
                    >
                      <LayoutDashboard className="w-4 h-4 text-slate-400" />
                      <span>Admin Control Panel</span>
                    </button>
                  </div>

                  <div className="pt-1 border-t border-slate-200 dark:border-slate-800">
                    <button
                      onClick={() => {
                        logout();
                        setShowProfileMenu(false);
                      }}
                      className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-rose-500 hover:bg-rose-500/10 rounded-xl transition-colors cursor-pointer"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Mobile Menu Toggle button */}
          {isPublicPage && (
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-slate-600 dark:text-slate-300"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          )}
        </div>
      </div>

      {/* Mobile Drawer Navigation for Marketing Page */}
      {isPublicPage && mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-950/95 px-4 pt-3 pb-6 space-y-2">
          {navLinks.map((link) => (
            <button
              key={link.id}
              onClick={() => {
                navigateTo(link.id);
                setMobileMenuOpen(false);
              }}
              className="block w-full text-left px-4 py-2.5 rounded-xl text-sm font-bold text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-900"
            >
              {link.label}
            </button>
          ))}
          <div className="pt-2 border-t border-slate-200 dark:border-slate-800 flex flex-col gap-2">
            <button
              onClick={() => {
                navigateTo('login');
                setMobileMenuOpen(false);
              }}
              className="w-full text-center py-2.5 text-sm font-bold text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 rounded-xl"
            >
              Sign In
            </button>
            <button
              onClick={() => {
                navigateTo('dashboard');
                setMobileMenuOpen(false);
              }}
              className="w-full text-center py-2.5 text-sm font-bold text-white bg-gradient-to-r from-red-600 to-amber-500 rounded-xl shadow-lg shadow-red-500/20"
            >
              Launch Dashboard
            </button>
          </div>
        </div>
      )}
    </header>
  );
};
