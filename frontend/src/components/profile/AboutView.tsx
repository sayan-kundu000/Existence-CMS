import React from 'react';
import { Compass, Mail, Phone, Globe, ShieldCheck, ArrowRight, UserCircle2, Sparkles, Building, ExternalLink } from 'lucide-react';
import { Profile, PublicTabType } from '../../types';
import { EmptyState } from '../common/EmptyState';

interface AboutViewProps {
  profile: Profile | null;
  onNavigate: (tab: PublicTabType) => void;
}

export const AboutView: React.FC<AboutViewProps> = ({ profile, onNavigate }) => {
  if (!profile || !profile.about || profile.about.trim().length === 0) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6">
        <EmptyState
          icon={UserCircle2}
          title="About narrative is currently unavailable"
          description="The professional executive summary and background description have not been entered into the system yet."
          actionText="Back to Home"
          onAction={() => onNavigate('home')}
        />
      </div>
    );
  }

  // Primary email
  const primaryEmailObj = profile.emails?.find((e) => e.is_primary);
  const primaryEmail = primaryEmailObj?.email || (profile.email_ids && profile.email_ids.length > 0 ? profile.email_ids[0] : null);

  // Split about text by double newlines into distinct paragraphs
  const paragraphs = profile.about.split(/\n\s*\n/).filter((p) => p.trim().length > 0);

  return (
    <div className="max-w-4xl mx-auto py-8 sm:py-16 px-4 sm:px-6 space-y-10 animate-fadeIn">
      {/* Breadcrumb / Section Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider">
          <Compass className="w-4 h-4" />
          <span>Executive Narrative & Biography</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          About {profile.name || 'the Professional'}
        </h1>
        <p className="text-xs sm:text-sm text-slate-400">
          Comprehensive overview of personal ethos, professional trajectory, and working principles.
        </p>
      </div>

      {/* Main Narrative Glass Panel */}
      <div className="glass-panel p-6 sm:p-10 rounded-3xl border border-slate-800 shadow-2xl relative overflow-hidden space-y-6">
        <div className="flex items-center justify-between pb-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center font-bold text-xl">
              {profile.name ? profile.name.charAt(0).toUpperCase() : 'E'}
            </div>
            <div>
              <h2 className="text-lg font-bold text-white leading-none">
                {profile.name || 'Verified Identity'}
              </h2>
              <span className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                Verified PostgreSQL Record
              </span>
            </div>
          </div>

          {profile.linkedin && (
            <a
              href={profile.linkedin.startsWith('http') ? profile.linkedin : `https://${profile.linkedin}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-medium text-indigo-300 hover:text-indigo-200 transition-all"
            >
              <Globe className="w-3.5 h-3.5 text-indigo-400" />
              <span>LinkedIn</span>
              <ExternalLink className="w-3 h-3 text-slate-500" />
            </a>
          )}
        </div>

        {/* Narrative Paragraphs */}
        <div className="space-y-5 text-sm sm:text-base text-slate-200 leading-relaxed font-light">
          {paragraphs.map((para, idx) => (
            <p key={idx} className="whitespace-pre-line">
              {para}
            </p>
          ))}
        </div>

        {/* Direct Contact Callout */}
        <div className="pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="text-xs text-slate-400">
            <span>Direct contact coordinates verified via PostgreSQL persistence layer.</span>
          </div>

          <div className="flex items-center gap-3">
            {primaryEmail && (
              <a
                href={`mailto:${primaryEmail}`}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all cursor-pointer"
              >
                <Mail className="w-3.5 h-3.5" />
                <span>Send Email</span>
              </a>
            )}
            <button
              onClick={() => onNavigate('contact')}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-semibold transition-all cursor-pointer"
            >
              <span>View All Endpoints</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
