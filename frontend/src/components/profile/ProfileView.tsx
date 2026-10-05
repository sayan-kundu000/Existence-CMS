import React from 'react';
import { Mail, Phone, Globe, UserCircle2, Sparkles, Heart, Compass, Shield, Edit3, ArrowRight } from 'lucide-react';
import { Profile, HobbyInterest, PersonalitySynthesis } from '../../types';
import { EmptyState } from '../common/EmptyState';

interface ProfileViewProps {
  profile: Profile | null;
  hobbiesInterests: HobbyInterest[];
  synthesis: PersonalitySynthesis | null;
  onNavigateToCms: () => void;
}

export const ProfileView: React.FC<ProfileViewProps> = ({
  profile,
  hobbiesInterests,
  synthesis,
  onNavigateToCms
}) => {
  if (!profile || profile.is_empty) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6">
        <div className="text-center mb-10">
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-3">
            Identity & Portfolio Intelligence
          </h1>
          <p className="text-slate-400 max-w-xl mx-auto text-sm sm:text-base">
            Existence provides architectural clarity over personal trajectory, verified competencies, and psychological dynamics.
          </p>
        </div>

        <EmptyState
          icon={UserCircle2}
          title="No Profile Information Added Yet"
          description="Your personal identity, contact endpoints, and bio have not been entered. Populate them securely from the custom CMS admin portal."
          actionText="Open CMS Editor"
          onAction={onNavigateToCms}
        />
      </div>
    );
  }

  const hobbies = hobbiesInterests.filter((i) => i.type === 'hobby');
  const interests = hobbiesInterests.filter((i) => i.type === 'interest');

  return (
    <div className="max-w-5xl mx-auto py-8 sm:py-12 px-4 sm:px-6 space-y-8 animate-fadeIn">
      {/* Hero Profile Header */}
      <div className="relative overflow-hidden rounded-3xl glass-panel p-6 sm:p-10 border border-slate-800 shadow-2xl">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div className="flex items-center gap-5">
            <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-3xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-600 p-1 shadow-xl shadow-indigo-600/30 flex items-center justify-center">
              <div className="w-full h-full bg-slate-950 rounded-[22px] flex items-center justify-center">
                <span className="text-3xl sm:text-4xl font-extrabold bg-gradient-to-tr from-indigo-400 to-purple-300 bg-clip-text text-transparent">
                  {profile.name ? profile.name.charAt(0).toUpperCase() : 'E'}
                </span>
              </div>
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
                {profile.name || 'Unnamed Profile'}
              </h1>
              <p className="text-xs sm:text-sm text-indigo-400 font-medium mt-0.5">
                Verified Personal Entity
              </p>
              <div className="flex flex-wrap items-center gap-3 mt-3 text-xs text-slate-400">
                {profile.mobile_number && (
                  <span className="flex items-center gap-1.5 bg-slate-900/80 px-2.5 py-1 rounded-lg border border-slate-800">
                    <Phone className="w-3.5 h-3.5 text-slate-400" />
                    {profile.mobile_number}
                  </span>
                )}
                {profile.linkedin && (
                  <a
                    href={profile.linkedin.startsWith('http') ? profile.linkedin : `https://${profile.linkedin}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 bg-slate-900/80 hover:bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-800 text-indigo-300 hover:text-indigo-200 transition-colors"
                  >
                    <Globe className="w-3.5 h-3.5" />
                    LinkedIn
                  </a>
                )}
              </div>
            </div>
          </div>

          <button
            onClick={onNavigateToCms}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-200 transition-all cursor-pointer self-start sm:self-auto shadow-sm"
          >
            <Edit3 className="w-3.5 h-3.5 text-indigo-400" />
            <span>Manage via CMS</span>
          </button>
        </div>

        {/* Email Addresses list */}
        {profile.email_ids && profile.email_ids.length > 0 && (
          <div className="mt-6 pt-6 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
            <span className="text-xs text-slate-500 font-medium mr-1 flex items-center gap-1">
              <Mail className="w-3.5 h-3.5" /> Direct Endpoints:
            </span>
            {profile.email_ids.map((email, idx) => (
              <a
                key={idx}
                href={`mailto:${email}`}
                className="px-3 py-1 rounded-lg bg-slate-900/90 border border-slate-800 text-xs text-slate-300 hover:text-white hover:border-slate-700 transition-colors font-mono"
              >
                {email}
              </a>
            ))}
          </div>
        )}
      </div>

      {/* About Section */}
      {profile.about && (
        <div className="glass-card p-6 sm:p-8 rounded-3xl border border-slate-800/80 shadow-xl">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
            <Compass className="w-4 h-4 text-indigo-400" />
            Executive Narrative
          </h2>
          <p className="text-sm sm:text-base text-slate-300 leading-relaxed whitespace-pre-line font-light">
            {profile.about}
          </p>
        </div>
      )}

      {/* Psychological Synthesis Highlights */}
      {synthesis && synthesis.has_assessments && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Key Strengths */}
          <div className="glass-card p-6 rounded-3xl border border-slate-800/80">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                Verified Key Strengths
              </h3>
              <span className="text-[10px] font-mono text-slate-500">
                {synthesis.assessments_completed?.length || 1} Test{(synthesis.assessments_completed?.length || 1) !== 1 ? 's' : ''} Basis
              </span>
            </div>
            {synthesis.key_strengths.length > 0 ? (
              <ul className="space-y-2.5">
                {synthesis.key_strengths.slice(0, 5).map((str, i) => (
                  <li key={i} className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-2 shrink-0" />
                    <span>{str}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-slate-500 italic">No key strengths derived yet.</p>
            )}
          </div>

          {/* Key Growth Blindspots / Weaknesses */}
          <div className="glass-card p-6 rounded-3xl border border-slate-800/80">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Key Growth Blindspots (Weaknesses)
              </h3>
              <span className="text-[10px] font-mono text-slate-500">
                {synthesis.assessments_completed?.length || 1} Test{(synthesis.assessments_completed?.length || 1) !== 1 ? 's' : ''} Basis
              </span>
            </div>
            {synthesis.key_weaknesses.length > 0 ? (
              <ul className="space-y-2.5">
                {synthesis.key_weaknesses.slice(0, 5).map((wk, i) => (
                  <li key={i} className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-2 shrink-0" />
                    <span>{wk}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-slate-500 italic">No growth areas derived yet.</p>
            )}
          </div>
        </div>
      )}

      {/* Hobbies & Interests */}
      {(hobbies.length > 0 || interests.length > 0) && (
        <div className="glass-card p-6 sm:p-8 rounded-3xl border border-slate-800/80">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {hobbies.length > 0 && (
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-rose-400 mb-3 flex items-center gap-2">
                  <Heart className="w-4 h-4" />
                  Hobbies
                </h3>
                <div className="flex flex-wrap gap-2">
                  {hobbies.map((h) => (
                    <span
                      key={h.id}
                      className="px-3 py-1 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 flex items-center gap-1.5"
                    >
                      {h.icon && <span>{h.icon}</span>}
                      <span>{h.name}</span>
                    </span>
                  ))}
                </div>
              </div>
            )}

            {interests.length > 0 && (
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-purple-400 mb-3 flex items-center gap-2">
                  <Compass className="w-4 h-4" />
                  Interests
                </h3>
                <div className="flex flex-wrap gap-2">
                  {interests.map((it) => (
                    <span
                      key={it.id}
                      className="px-3 py-1 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 flex items-center gap-1.5"
                    >
                      {it.icon && <span>{it.icon}</span>}
                      <span>{it.name}</span>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
