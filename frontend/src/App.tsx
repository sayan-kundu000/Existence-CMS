import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { PublicNavbar, AllTabType } from './components/common/PublicNavbar';
import { PublicFooter } from './components/common/PublicFooter';
import { LoginModal } from './components/common/LoginModal';
import { GlobalLoadingState } from './components/common/GlobalLoadingState';
import { GlobalErrorState } from './components/common/GlobalErrorState';
import { HeroSection } from './components/profile/HeroSection';
import { AboutView } from './components/profile/AboutView';
import { EducationView } from './components/education/EducationView';
import { ExperienceView } from './components/experience/ExperienceView';
import { SkillsView } from './components/skills/SkillsView';
import { PersonalityView } from './components/personality/PersonalityView';
import { ProjectsView } from './components/projects/ProjectsView';
import { InterestsView } from './components/interests/InterestsView';
import { ContactView } from './components/contact/ContactView';
import { CmsDashboard } from './components/cms/CmsDashboard';
import { Profile, Education, Experience, Skill, Project, HobbyInterest, PersonalitySynthesis, PublicTabType } from './types';
import { api } from './services/api';

const parseRoute = (path: string): AllTabType => {
  const p = path.toLowerCase();
  if (p.startsWith('/admin') || p.startsWith('/cms')) return 'cms';
  if (p.startsWith('/about')) return 'about';
  if (p.startsWith('/education')) return 'education';
  if (p.startsWith('/experience')) return 'experience';
  if (p.startsWith('/skills')) return 'skills';
  if (p.startsWith('/projects')) return 'projects';
  if (p.startsWith('/personality')) return 'personality';
  if (p.startsWith('/interests')) return 'interests';
  if (p.startsWith('/contact')) return 'contact';
  return 'home';
};

const getPageTitle = (tab: AllTabType, name?: string | null): string => {
  const baseName = name ? `${name} — ` : '';
  switch (tab) {
    case 'about':
      return `${baseName}Executive Narrative | Existence`;
    case 'education':
      return `${baseName}Academic Lineage | Existence`;
    case 'experience':
      return `${baseName}Work Trajectory | Existence`;
    case 'skills':
      return `${baseName}7-Level Mastery Engine | Existence`;
    case 'projects':
      return `${baseName}Projects & Tech Stack Engine | Existence`;
    case 'personality':
      return `${baseName}Psychological Intelligence | Existence`;
    case 'interests':
      return `${baseName}Hobbies & Interests | Existence`;
    case 'contact':
      return `${baseName}Contact Coordinates | Existence`;
    case 'cms':
      return 'Existence Admin CMS';
    case 'home':
    default:
      return `${baseName}Personal Identity & Trajectory | Existence`;
  }
};

const AppContent: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [currentTab, setCurrentTab] = useState<AllTabType>(() => parseRoute(window.location.pathname));
  const [loginModalOpen, setLoginModalOpen] = useState(false);

  // Core Persisted Data
  const [profile, setProfile] = useState<Profile | null>(null);
  const [educations, setEducations] = useState<Education[]>([]);
  const [experiences, setExperiences] = useState<Experience[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [hobbiesInterests, setHobbiesInterests] = useState<HobbyInterest[]>([]);
  const [synthesis, setSynthesis] = useState<PersonalitySynthesis | null>(null);

  // State Management
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState(!navigator.onLine);

  const fetchAllData = async () => {
    setLoading(true);
    setFetchError(null);
    try {
      try {
        const consolidated = await api.getConsolidatedPublicProfile();
        setProfile(consolidated.profile);
        setEducations(consolidated.education || []);
        setExperiences(consolidated.experience || []);
        setSkills(consolidated.skills || []);
        setProjects(consolidated.projects || []);

        let combinedHI = [
          ...(consolidated.hobbies || []).map(h => ({
            id: h.id,
            type: 'hobby' as const,
            name: h.name,
            category: h.category,
            icon: h.icon,
            ordering: h.ordering || 0,
            created_at: h.created_at,
            updated_at: h.updated_at
          })),
          ...(consolidated.interests || []).map(i => ({
            id: i.id,
            type: 'interest' as const,
            name: i.name,
            category: i.category,
            icon: i.icon,
            ordering: i.ordering || 0,
            created_at: i.created_at,
            updated_at: i.updated_at
          }))
        ];

        if (combinedHI.length === 0) {
          try {
            const hiFallback = await api.getHobbiesInterests();
            if (hiFallback && hiFallback.length > 0) {
              combinedHI = hiFallback;
            }
          } catch (err) {
            console.warn('Fallback hobbies-interests fetch failed:', err);
          }
        }

        setHobbiesInterests(combinedHI);
        setSynthesis(consolidated.personality);
      } catch {
        // Fallback to individual calls if consolidated endpoint unavailable
        const [p, ed, ex, sk, proj, hi, syn] = await Promise.all([
          api.getProfile().catch(() => null),
          api.getEducation().catch(() => []),
          api.getExperience().catch(() => []),
          api.getSkills(false).catch(() => []),
          api.getProjects(false).catch(() => []),
          api.getHobbiesInterests().catch(() => []),
          api.getPersonalitySynthesis().catch(() => null)
        ]);
        setProfile(p);
        setEducations(ed);
        setExperiences(ex);
        setSkills(sk);
        setProjects(proj);
        setHobbiesInterests(hi);
        setSynthesis(syn);
      }
    } catch (e: any) {
      console.error('Data fetch error:', e);
      setFetchError(e?.message || 'Failed to fetch portfolio data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  // Update document title dynamically
  useEffect(() => {
    document.title = getPageTitle(currentTab, profile?.name);
  }, [currentTab, profile?.name]);

  // Synchronize browser history / popstate
  useEffect(() => {
    const handlePopState = () => {
      setCurrentTab(parseRoute(window.location.pathname));
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Network offline listener
  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleTabChange = (tab: AllTabType) => {
    setCurrentTab(tab);
    const targetPath = tab === 'home' ? '/' : `/${tab}`;
    if (window.location.pathname !== targetPath) {
      window.history.pushState({ tab }, '', targetPath);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const hobbies = hobbiesInterests.filter((i) => i.type === 'hobby');
  const interests = hobbiesInterests.filter((i) => i.type === 'interest');

  const primaryEmailObj = profile?.emails?.find((e) => e.is_primary);
  const primaryEmail = primaryEmailObj?.email || (profile?.email_ids && profile.email_ids.length > 0 ? profile.email_ids[0] : null);

  return (
    <div className="min-h-screen bhagwa-bg text-amber-50 flex flex-col font-sans selection:bg-amber-600/40 selection:text-amber-100 relative overflow-x-hidden">
      {/* Ambient Bhagwa / Saffron Glow Atmosphere */}
      <div className="fixed top-0 left-1/4 w-96 h-96 bg-gradient-to-br from-amber-600/15 via-orange-600/10 to-transparent rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="fixed bottom-10 right-10 w-96 h-96 bg-gradient-to-tl from-orange-600/20 via-amber-600/10 to-transparent rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Skip to Content link for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-50 px-4 py-2 bg-amber-600 text-white rounded-xl text-xs font-bold shadow-lg"
      >
        Skip to main content
      </a>

      {/* Public Header & Responsive Navigation */}
      <PublicNavbar
        currentTab={currentTab}
        onTabChange={handleTabChange}
        onOpenLogin={() => setLoginModalOpen(true)}
      />

      {/* Main Content Area */}
      <main id="main-content" className="flex-1 w-full" role="main">
        {loading ? (
          <GlobalLoadingState />
        ) : fetchError && !profile && educations.length === 0 && experiences.length === 0 ? (
          <GlobalErrorState
            message={fetchError}
            onRetry={fetchAllData}
            isOffline={isOffline}
          />
        ) : (
          <>
            {currentTab === 'home' && (
              <HeroSection
                profile={profile}
                educations={educations}
                experiences={experiences}
                skills={skills}
                synthesis={synthesis}
                onNavigate={(t) => handleTabChange(t)}
              />
            )}

            {currentTab === 'about' && (
              <AboutView
                profile={profile}
                onNavigate={(t) => handleTabChange(t)}
              />
            )}

            {currentTab === 'education' && (
              <EducationView
                educations={educations}
                onNavigate={(t) => handleTabChange(t)}
              />
            )}

            {currentTab === 'experience' && (
              <ExperienceView
                experiences={experiences}
                onNavigate={(t) => handleTabChange(t)}
              />
            )}

            {currentTab === 'skills' && (
              <SkillsView
                skills={skills}
                onNavigate={(t) => handleTabChange(t)}
                onNavigateToCms={() => handleTabChange('cms')}
              />
            )}

            {currentTab === 'projects' && (
              <ProjectsView projects={projects} />
            )}

            {currentTab === 'personality' && (
              <PersonalityView
                synthesis={synthesis}
                onRefreshSynthesis={fetchAllData}
                onNavigate={(t) => handleTabChange(t)}
              />
            )}

            {currentTab === 'interests' && (
              <InterestsView
                hobbies={hobbies}
                interests={interests}
                onNavigate={(t) => handleTabChange(t)}
              />
            )}

            {currentTab === 'contact' && (
              <ContactView
                profile={profile}
                onNavigate={(t) => handleTabChange(t)}
              />
            )}

            {currentTab === 'cms' && (
              <CmsDashboard
                onRefreshAll={fetchAllData}
                onOpenLogin={() => setLoginModalOpen(true)}
              />
            )}
          </>
        )}
      </main>

      {/* Public Footer */}
      <PublicFooter
        onNavigate={(t) => handleTabChange(t)}
        linkedinUrl={profile?.linkedin}
        primaryEmail={primaryEmail}
      />

      {/* Admin Login Modal */}
      <LoginModal isOpen={loginModalOpen} onClose={() => setLoginModalOpen(false)} />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
