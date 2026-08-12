import React from 'react';
import { AppStateProvider, useAppState } from './store/useStore';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';
import { Toast } from './components/common/Toast';

// Pages
import { LandingPage } from './components/pages/LandingPage';
import { PricingPage } from './components/pages/PricingPage';
import { FeaturesPage } from './components/pages/FeaturesPage';
import { BlogPage } from './components/pages/BlogPage';
import { AboutPage } from './components/pages/AboutPage';
import { ContactPage } from './components/pages/ContactPage';
import { AuthPages } from './components/pages/AuthPages';
import { DashboardPage } from './components/pages/DashboardPage';
import { AnalyticsPage } from './components/pages/AnalyticsPage';
import { KeywordResearchPage } from './components/pages/KeywordResearchPage';
import { VideoSEOPage } from './components/pages/VideoSEOPage';
import { AIScriptGeneratorPage } from './components/pages/AIScriptGeneratorPage';
import { AITitleGeneratorPage } from './components/pages/AITitleGeneratorPage';
import { DescriptionGeneratorPage } from './components/pages/DescriptionGeneratorPage';
import { TagsGeneratorPage } from './components/pages/TagsGeneratorPage';
import { ThumbnailPromptPage } from './components/pages/ThumbnailPromptPage';
import { CompetitorAnalysisPage } from './components/pages/CompetitorAnalysisPage';
import { TrendExplorerPage } from './components/pages/TrendExplorerPage';
import { ContentCalendarPage } from './components/pages/ContentCalendarPage';
import { ReportsPage } from './components/pages/ReportsPage';
import { BillingPage } from './components/pages/BillingPage';
import { NotificationsPage } from './components/pages/NotificationsPage';
import { SettingsPage } from './components/pages/SettingsPage';
import { SupportPage } from './components/pages/SupportPage';
import { AdminPage } from './components/pages/AdminPage';

const AppContent: React.FC = () => {
  const { currentPage, userProfile } = useAppState();

  const publicPages = [
    'landing',
    'pricing',
    'features',
    'blog',
    'about',
    'contact',
    'login',
    'register',
    'forgot-password',
  ];

  const isPublic = publicPages.includes(currentPage);
  const isAuthenticated = Boolean(userProfile.isAuthenticated);

  const renderCurrentPage = () => {
    // If attempting to access a protected app route without login, force login view
    if (!isPublic && !isAuthenticated) {
      return <AuthPages mode="login" />;
    }

    switch (currentPage) {
      case 'landing':
        return <LandingPage />;
      case 'pricing':
        return <PricingPage />;
      case 'features':
        return <FeaturesPage />;
      case 'blog':
        return <BlogPage />;
      case 'about':
        return <AboutPage />;
      case 'contact':
        return <ContactPage />;
      case 'login':
      case 'register':
      case 'forgot-password':
        return <AuthPages />;
      case 'dashboard':
      case 'channel-overview':
        return <DashboardPage />;
      case 'analytics':
      case 'video-performance':
        return <AnalyticsPage />;
      case 'keyword-research':
      case 'keyword-explorer':
        return <KeywordResearchPage />;
      case 'video-seo':
        return <VideoSEOPage />;
      case 'ai-script':
        return <AIScriptGeneratorPage />;
      case 'ai-title':
        return <AITitleGeneratorPage />;
      case 'description-generator':
        return <DescriptionGeneratorPage />;
      case 'tags-generator':
        return <TagsGeneratorPage />;
      case 'thumbnail-prompts':
        return <ThumbnailPromptPage />;
      case 'competitors':
        return <CompetitorAnalysisPage />;
      case 'trends':
        return <TrendExplorerPage />;
      case 'content-calendar':
        return <ContentCalendarPage />;
      case 'reports':
        return <ReportsPage />;
      case 'billing':
        return <BillingPage />;
      case 'notifications':
        return <NotificationsPage />;
      case 'settings':
        return <SettingsPage />;
      case 'support':
        return <SupportPage />;
      case 'admin':
        return <AdminPage />;
      default:
        return <LandingPage />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans transition-colors duration-300">
      <Navbar />
      <Toast />

      {isPublic || !isAuthenticated ? (
        <main className="flex-1 w-full">{renderCurrentPage()}</main>
      ) : (
        <div className="flex flex-1 w-full relative">
          <Sidebar />
          <main className="flex-1 min-w-0 overflow-y-auto pb-16">{renderCurrentPage()}</main>
        </div>
      )}
    </div>
  );
};

export default function App() {
  return (
    <AppStateProvider>
      <AppContent />
    </AppStateProvider>
  );
}
