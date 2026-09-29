import React, { useState } from 'react';
import { Mail, Phone, Globe, ShieldCheck, Copy, Check, ExternalLink, MessageSquare, ArrowRight } from 'lucide-react';
import { Profile, PublicTabType } from '../../types';
import { EmptyState } from '../common/EmptyState';

interface ContactViewProps {
  profile: Profile | null;
  onNavigate: (tab: PublicTabType) => void;
}

export const ContactView: React.FC<ContactViewProps> = ({ profile, onNavigate }) => {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const emails = profile?.emails || (profile?.email_ids ? profile.email_ids.map((e, idx) => ({
    id: idx,
    profile_id: profile.id,
    email: e,
    label: idx === 0 ? 'Primary' : 'Alternative',
    is_primary: idx === 0,
    display_order: idx,
    created_at: '',
    updated_at: ''
  })) : []);

  const hasAnyContact = emails.length > 0 || Boolean(profile?.mobile_number) || Boolean(profile?.linkedin);

  if (!hasAnyContact) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6">
        <EmptyState
          icon={Mail}
          title="No contact endpoints configured"
          description="Direct communication channels, verified email endpoints, and professional links have not been entered yet."
          actionText="Back to Home"
          onAction={() => onNavigate('home')}
        />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8 sm:py-16 px-4 sm:px-6 space-y-10 animate-fadeIn">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider">
          <MessageSquare className="w-4 h-4" />
          <span>Direct Endpoints & Channels</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Contact & Communication
        </h1>
        <p className="text-xs sm:text-sm text-slate-400">
          Verified direct endpoints backed by PostgreSQL database persistence.
        </p>
      </div>

      {/* Contact Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Email Addresses */}
        {emails.length > 0 && (
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6 md:col-span-2">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center">
                  <Mail className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Direct Email Channels</h3>
                  <p className="text-xs text-slate-400">Verified electronic mail communication</p>
                </div>
              </div>
              <span className="text-xs font-mono text-slate-500">
                {emails.length} {emails.length === 1 ? 'Address' : 'Addresses'}
              </span>
            </div>

            <div className="space-y-3">
              {emails.map((e, idx) => {
                const isCopied = copiedKey === `email-${idx}`;
                return (
                  <div
                    key={idx}
                    className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono text-slate-200 font-medium">
                        {e.email}
                      </span>
                      {e.is_primary && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          Primary
                        </span>
                      )}
                      {e.label && (
                        <span className="text-[10px] text-slate-500 bg-slate-800 px-2 py-0.5 rounded-md">
                          {e.label}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-2 self-end sm:self-auto">
                      <button
                        onClick={() => copyToClipboard(e.email, `email-${idx}`)}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-all cursor-pointer"
                        title="Copy to clipboard"
                      >
                        {isCopied ? (
                          <>
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                            <span className="text-emerald-400">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>

                      <a
                        href={`mailto:${e.email}`}
                        className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-sm transition-all"
                      >
                        <span>Mail</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Mobile Number */}
        {profile?.mobile_number && (
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 flex flex-col justify-between space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center">
                <Phone className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Telephone / Mobile</h3>
                <p className="text-xs text-slate-400">Direct voice & SMS communication</p>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 flex items-center justify-between">
              <span className="text-sm font-mono text-slate-200 font-semibold">
                {profile.mobile_number}
              </span>
              <button
                onClick={() => copyToClipboard(profile.mobile_number!, 'phone')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-all cursor-pointer"
              >
                {copiedKey === 'phone' ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* LinkedIn Profile */}
        {profile?.linkedin && (
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 flex flex-col justify-between space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center justify-center">
                <Globe className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">LinkedIn Network</h3>
                <p className="text-xs text-slate-400">Professional network connection</p>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 flex items-center justify-between">
              <span className="text-xs font-mono text-indigo-300 truncate max-w-[200px]">
                {profile.linkedin}
              </span>
              <a
                href={profile.linkedin.startsWith('http') ? profile.linkedin : `https://${profile.linkedin}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-sm transition-all"
              >
                <span>Visit</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        )}
      </div>

      {/* Trust & Verification Footnote */}
      <div className="p-4 rounded-2xl bg-slate-900/50 border border-slate-800 flex items-center gap-3 text-xs text-slate-400">
        <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
        <span>All endpoints above represent real, verified coordinates persisted in the PostgreSQL database.</span>
      </div>
    </div>
  );
};
