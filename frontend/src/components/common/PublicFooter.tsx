import React from 'react';
import { ShieldCheck, Mail, Globe, ArrowUp, ExternalLink } from 'lucide-react';
import { PublicTabType } from '../../types';

interface PublicFooterProps {
  onNavigate: (tab: PublicTabType) => void;
  linkedinUrl?: string | null;
  primaryEmail?: string | null;
}

export const PublicFooter: React.FC<PublicFooterProps> = ({
  onNavigate,
  linkedinUrl,
  primaryEmail
}) => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="w-full border-t border-slate-900 bg-slate-950/95 py-12 px-4 sm:px-6 lg:px-8 mt-auto">
      <div className="max-w-7xl mx-auto space-y-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Column 1: Brand & Ethos */}
          <div className="space-y-3 md:col-span-2">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center font-bold text-white text-sm">
                E
              </div>
              <span className="font-extrabold text-white text-base tracking-tight">EXISTENCE</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Portfolio UI
              </span>
            </div>
            <p className="text-xs text-slate-400 max-w-sm leading-relaxed font-light">
              Personal identity and psychological intelligence platform uniting formal academic trajectory, work experience, 7-level competency mastery, and empirical assessments.
            </p>
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>PostgreSQL Persisted & Verified</span>
            </div>
          </div>

          {/* Column 2: Navigation Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">Sections</h4>
            <ul className="space-y-2 text-xs text-slate-400">
              <li>
                <button
                  onClick={() => onNavigate('home')}
                  className="hover:text-indigo-400 transition-colors cursor-pointer"
                >
                  Home / Overview
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('about')}
                  className="hover:text-indigo-400 transition-colors cursor-pointer"
                >
                  Executive Narrative
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('education')}
                  className="hover:text-indigo-400 transition-colors cursor-pointer"
                >
                  Education Lineage
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('experience')}
                  className="hover:text-indigo-400 transition-colors cursor-pointer"
                >
                  Work Trajectory
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('skills')}
                  className="hover:text-indigo-400 transition-colors cursor-pointer"
                >
                  7-Level Skills
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('personality')}
                  className="hover:text-indigo-400 transition-colors cursor-pointer"
                >
                  Psychology & Synthesis
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('interests')}
                  className="hover:text-indigo-400 transition-colors cursor-pointer"
                >
                  Hobbies & Interests
                </button>
              </li>
            </ul>
          </div>

          {/* Column 3: Communication & Return to top */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">Channels</h4>
            <div className="space-y-2 text-xs">
              {primaryEmail && (
                <a
                  href={`mailto:${primaryEmail}`}
                  className="flex items-center gap-1.5 text-slate-400 hover:text-white transition-colors"
                >
                  <Mail className="w-3.5 h-3.5 text-indigo-400" />
                  <span className="truncate">{primaryEmail}</span>
                </a>
              )}
              {linkedinUrl && (
                <a
                  href={linkedinUrl.startsWith('http') ? linkedinUrl : `https://${linkedinUrl}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-slate-400 hover:text-indigo-300 transition-colors"
                >
                  <Globe className="w-3.5 h-3.5 text-indigo-400" />
                  <span>LinkedIn Network</span>
                  <ExternalLink className="w-3 h-3 text-slate-600" />
                </a>
              )}
              <button
                onClick={() => onNavigate('contact')}
                className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 pt-1 block cursor-pointer"
              >
                View all contact channels →
              </button>
            </div>

            <div className="pt-2">
              <button
                onClick={scrollToTop}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-850 border border-slate-800 text-[11px] text-slate-400 hover:text-white transition-all cursor-pointer"
              >
                <ArrowUp className="w-3.5 h-3.5" />
                <span>Back to top</span>
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Strip */}
        <div className="pt-8 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-slate-500">
          <div>
            © {new Date().getFullYear()} Existence Platform. All rights reserved.
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <span>FastAPI + PostgreSQL</span>
            <span>•</span>
            <span>React + TypeScript + Vite</span>
            <span>•</span>
            <span>7-Level Mastery</span>
            <span>•</span>
            <span>PIN-Protected CMS</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
