import React from 'react';
import {
  User,
  GraduationCap,
  Briefcase,
  Sparkles,
  Brain,
  Compass,
  Mail,
  Phone,
  Globe,
  ArrowRight,
  ShieldCheck,
  ExternalLink,
  ChevronDown
} from 'lucide-react';
import { Profile, Education, Experience, Skill, PersonalitySynthesis, PublicTabType } from '../../types';

interface HeroSectionProps {
  profile: Profile | null;
  educations: Education[];
  experiences: Experience[];
  skills: Skill[];
  synthesis: PersonalitySynthesis | null;
  onNavigate: (tab: PublicTabType) => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  profile,
  educations,
  experiences,
  skills,
  synthesis,
  onNavigate
}) => {
  const hasProfileName = Boolean(profile?.name && profile.name.trim().length > 0);
  const displayName = hasProfileName ? profile!.name : 'Personal Identity & Intelligence';
  const initial = hasProfileName ? profile!.name!.charAt(0).toUpperCase() : 'E';

  // Primary Email resolution
  const primaryEmailObj = profile?.emails?.find((e) => e.is_primary);
  const primaryEmail = primaryEmailObj?.email || (profile?.email_ids && profile.email_ids.length > 0 ? profile.email_ids[0] : null);

  // Active / current roles
  const currentRole = experiences.find((e) => e.currently_working);
  const currentStudy = educations.find((e) => e.currently_studying);

  return (
    <section className="relative overflow-hidden py-10 sm:py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-12 animate-fadeIn">
      {/* Background Decorative Ambient Glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 right-10 w-80 h-80 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Main Hero Card */}
      <div className="relative glass-panel rounded-3xl p-6 sm:p-10 md:p-12 border border-slate-800 shadow-2xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-8">
          {/* Identity info */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
            {/* Avatar / Monogram */}
            <div className="relative group shrink-0">
              <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-3xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-600 p-1 shadow-xl shadow-indigo-600/30">
                <div className="w-full h-full bg-slate-950 rounded-[22px] flex items-center justify-center">
                  <span className="text-4xl sm:text-5xl font-black bg-gradient-to-tr from-indigo-400 via-indigo-200 to-purple-300 bg-clip-text text-transparent">
                    {initial}
                  </span>
                </div>
              </div>
              <div className="absolute -bottom-1 -right-1 p-1 bg-slate-950 rounded-xl border border-slate-800 shadow-md" title="PostgreSQL-backed Verified Record">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
              </div>
            </div>

            {/* Titles & Summary */}
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  Verified Identity
                </span>
                {currentRole && (
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Active: {currentRole.role}
                  </span>
                )}
                {currentStudy && (
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-purple-500/10 text-purple-400 border border-purple-500/20">
                    Studying: {currentStudy.level}
                  </span>
                )}
              </div>

              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight">
                {displayName}
              </h1>

              {profile?.about ? (
                <p className="text-sm sm:text-base text-slate-300 max-w-2xl font-light line-clamp-3 leading-relaxed">
                  {profile.about}
                </p>
              ) : (
                <p className="text-xs sm:text-sm text-slate-400 max-w-xl font-light">
                  A calibrated digital portfolio connecting academic credentials, industry work trajectory, verified 7-level competencies, and psychological assessments.
                </p>
              )}

              {/* Direct Contact endpoints */}
              <div className="flex flex-wrap items-center gap-3 pt-2 text-xs">
                {primaryEmail && (
                  <a
                    href={`mailto:${primaryEmail}`}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-200 hover:text-white transition-all font-mono"
                  >
                    <Mail className="w-3.5 h-3.5 text-indigo-400" />
                    <span>{primaryEmail}</span>
                  </a>
                )}
                {profile?.mobile_number && (
                  <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 font-mono">
                    <Phone className="w-3.5 h-3.5 text-slate-400" />
                    <span>{profile.mobile_number}</span>
                  </span>
                )}
                {profile?.linkedin && (
                  <a
                    href={profile.linkedin.startsWith('http') ? profile.linkedin : `https://${profile.linkedin}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-indigo-300 hover:text-indigo-200 transition-all"
                  >
                    <Globe className="w-3.5 h-3.5 text-indigo-400" />
                    <span>LinkedIn</span>
                    <ExternalLink className="w-3 h-3 text-slate-500" />
                  </a>
                )}
              </div>
            </div>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex flex-row lg:flex-col gap-3 shrink-0">
            <button
              onClick={() => onNavigate('contact')}
              className="flex-1 lg:flex-initial flex items-center justify-center gap-2 px-6 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition-all cursor-pointer"
            >
              <Mail className="w-4 h-4" />
              <span>Get in Touch</span>
            </button>
            <button
              onClick={() => onNavigate('about')}
              className="flex-1 lg:flex-initial flex items-center justify-center gap-2 px-6 py-3 rounded-2xl bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white text-xs font-semibold transition-all cursor-pointer"
            >
              <span>Read Biography</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Live Empirical Metrics Strip */}
        <div className="mt-10 pt-8 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div
            onClick={() => onNavigate('education')}
            className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all cursor-pointer group"
          >
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>Education</span>
              <GraduationCap className="w-4 h-4 text-purple-400 group-hover:scale-110 transition-transform" />
            </div>
            <div className="text-2xl font-bold text-white font-mono">{educations.length}</div>
            <span className="text-[11px] text-slate-500">Academic Credentials</span>
          </div>

          <div
            onClick={() => onNavigate('experience')}
            className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all cursor-pointer group"
          >
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>Trajectory</span>
              <Briefcase className="w-4 h-4 text-indigo-400 group-hover:scale-110 transition-transform" />
            </div>
            <div className="text-2xl font-bold text-white font-mono">{experiences.length}</div>
            <span className="text-[11px] text-slate-500">Professional Roles</span>
          </div>

          <div
            onClick={() => onNavigate('skills')}
            className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all cursor-pointer group"
          >
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>Competencies</span>
              <Sparkles className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
            </div>
            <div className="text-2xl font-bold text-white font-mono">{skills.length}</div>
            <span className="text-[11px] text-slate-500">7-Level Rated Skills</span>
          </div>

          <div
            onClick={() => onNavigate('personality')}
            className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all cursor-pointer group"
          >
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>Psychology</span>
              <Brain className="w-4 h-4 text-teal-400 group-hover:scale-110 transition-transform" />
            </div>
            <div className="text-2xl font-bold text-white font-mono">
              {synthesis?.assessments_completed?.length || 0} / 3
            </div>
            <span className="text-[11px] text-slate-500">Assessments Scored</span>
          </div>
        </div>
      </div>

      {/* Structured Domain Navigation Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <span>Explore Portfolio Architecture</span>
          </h2>
          <span className="text-xs text-slate-500">Select any domain to inspect</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6">
          <div
            onClick={() => onNavigate('about')}
            className="glass-card p-6 rounded-3xl border border-slate-800 hover:border-indigo-500/40 transition-all cursor-pointer group flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Compass className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-1 group-hover:text-indigo-300 transition-colors">
                Executive Narrative
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Personal identity, professional philosophy, communication channels, and direct contact details.
              </p>
            </div>
            <div className="mt-6 flex items-center gap-1.5 text-xs font-semibold text-indigo-400">
              <span>Read narrative</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          <div
            onClick={() => onNavigate('experience')}
            className="glass-card p-6 rounded-3xl border border-slate-800 hover:border-indigo-500/40 transition-all cursor-pointer group flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-2xl bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Briefcase className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-1 group-hover:text-purple-300 transition-colors">
                Experience & Journey
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Chronological appointments, employers, work modes (On-site, Remote, Hybrid), and physical locations.
              </p>
            </div>
            <div className="mt-6 flex items-center gap-1.5 text-xs font-semibold text-purple-400">
              <span>View {experiences.length} roles</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          <div
            onClick={() => onNavigate('skills')}
            className="glass-card p-6 rounded-3xl border border-slate-800 hover:border-indigo-500/40 transition-all cursor-pointer group flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-2xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Sparkles className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-1 group-hover:text-amber-300 transition-colors">
                7-Level Mastery Engine
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Calibrated technical competencies ranked strictly from Level 1 (Beginner) to Level 7 (Master).
              </p>
            </div>
            <div className="mt-6 flex items-center gap-1.5 text-xs font-semibold text-amber-400">
              <span>Inspect {skills.length} skills</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
