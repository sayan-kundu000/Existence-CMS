import React, { useState, useEffect, useRef } from 'react';
import {
  Home,
  User,
  GraduationCap,
  Briefcase,
  Sparkles,
  Brain,
  Compass,
  Mail,
  ShieldCheck,
  LayoutDashboard,
  FolderCode,
  LogIn,
  LogOut,
  Menu,
  X
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { PublicTabType } from '../../types';

export type AllTabType = PublicTabType | 'cms';

interface PublicNavbarProps {
  currentTab: AllTabType;
  onTabChange: (tab: AllTabType) => void;
  onOpenLogin: () => void;
}

export const PublicNavbar: React.FC<PublicNavbarProps> = ({
  currentTab,
  onTabChange,
  onOpenLogin
}) => {
  const { isAuthenticated, user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const mobileMenuRef = useRef<HTMLDivElement>(null);

  const navItems: { id: PublicTabType; label: string; icon: React.ElementType }[] = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'about', label: 'About', icon: User },
    { id: 'education', label: 'Education', icon: GraduationCap },
    { id: 'experience', label: 'Experience', icon: Briefcase },
    { id: 'skills', label: 'Skills (7-L)', icon: Sparkles },
    { id: 'projects', label: 'Projects', icon: FolderCode },
    { id: 'personality', label: 'Psychology', icon: Brain },
    { id: 'interests', label: 'Interests', icon: Compass },
    { id: 'contact', label: 'Contact', icon: Mail },
  ];

  // Close mobile drawer on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && mobileMenuOpen) {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [mobileMenuOpen]);

  // Lock background scroll when mobile drawer is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [mobileMenuOpen]);

  const handleSelectTab = (tab: AllTabType) => {
    onTabChange(tab);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          {/* Logo Brand */}
          <div
            onClick={() => handleSelectTab('home')}
            className="flex items-center gap-3 cursor-pointer group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 rounded-xl"
            tabIndex={0}
            role="button"
            aria-label="Existence Home"
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') handleSelectTab('home');
            }}
          >
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-600/30 group-hover:scale-105 transition-transform duration-200">
              <span className="font-black text-white text-lg tracking-wider">E</span>
            </div>
            <div>
              <span className="text-base sm:text-lg font-black tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-200 bg-clip-text text-transparent">
                EXISTENCE
              </span>
              <span className="hidden sm:inline-block ml-2 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 rounded-md">
                Portfolio
              </span>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav
            className="hidden lg:flex items-center gap-1 bg-slate-900/60 p-1.5 rounded-2xl border border-slate-800/60 shadow-inner"
            role="navigation"
            aria-label="Main Navigation"
          >
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSelectTab(item.id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-150 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Right Action: Admin Access & Mobile Toggle */}
          <div className="flex items-center gap-2.5">
            {/* Admin CMS Access */}
            <button
              onClick={() => handleSelectTab('cms')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 ${
                currentTab === 'cms'
                  ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                  : 'bg-slate-900/80 hover:bg-slate-850 text-slate-300 hover:text-white border border-slate-800'
              }`}
              title="Custom CMS Administration"
              aria-label="Admin CMS Portal"
            >
              <LayoutDashboard className="w-3.5 h-3.5 text-purple-400" />
              <span className="hidden sm:inline">Admin CMS</span>
            </button>

            {isAuthenticated ? (
              <button
                onClick={logout}
                title="Logout Admin"
                className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-xl transition-all cursor-pointer"
                aria-label="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={onOpenLogin}
                className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl transition-all cursor-pointer"
                aria-label="Admin Login"
              >
                <LogIn className="w-3.5 h-3.5 text-indigo-400" />
                <span>Login</span>
              </button>
            )}

            {/* Mobile Hamburger Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-slate-400 hover:text-white rounded-xl bg-slate-900 border border-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 cursor-pointer"
              aria-label={mobileMenuOpen ? 'Close Navigation Menu' : 'Open Navigation Menu'}
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Accessible Navigation Drawer */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 top-16 z-50 bg-slate-950/80 backdrop-blur-2xl lg:hidden flex flex-col animate-fadeIn"
          role="dialog"
          aria-modal="true"
          aria-label="Mobile Navigation Menu"
          ref={mobileMenuRef}
        >
          <div className="flex-1 overflow-y-auto p-6 space-y-3">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 px-3 block">
              Portfolio Navigation
            </span>

            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSelectTab(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-semibold transition-all cursor-pointer ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                      : 'text-slate-300 hover:bg-slate-900 border border-transparent hover:border-slate-800'
                  }`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </button>
              );
            })}

            <div className="pt-4 border-t border-slate-800/80 space-y-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 px-3 block">
                Administrative Area
              </span>

              <button
                onClick={() => handleSelectTab('cms')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-semibold transition-all cursor-pointer ${
                  currentTab === 'cms'
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'text-purple-300 bg-purple-500/10 border border-purple-500/20'
                }`}
              >
                <LayoutDashboard className="w-5 h-5" />
                <span>Custom CMS Portal</span>
              </button>

              {!isAuthenticated && (
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onOpenLogin();
                  }}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-2xl bg-slate-900 border border-slate-800 text-slate-300 text-xs font-semibold cursor-pointer"
                >
                  <LogIn className="w-4 h-4 text-indigo-400" />
                  <span>Admin Authentication</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
};
