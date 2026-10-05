import React, { useEffect } from 'react';
import {
  X,
  Calendar,
  ExternalLink,
  Layers,
  Star,
  Award,
  Globe,
  GitBranch,
  FileText,
  Code,
  Video,
  Copy,
  Check,
  Download,
  Sparkles
} from 'lucide-react';
import { Project, ProjectLinkType } from '../../types';
import { downloadProjectDossier, copyToClipboard } from '../../utils/githubExtractor';

interface ProjectDetailModalProps {
  project: Project | null;
  onClose: () => void;
}

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const formatTimeline = (p: Project): string | null => {
  if (!p.start_year) return null;
  const startStr = p.start_month
    ? `${MONTH_NAMES[p.start_month - 1]} ${p.start_year}`
    : `${p.start_year}`;

  if (p.is_current) {
    return `${startStr} – Present (Active)`;
  }
  if (!p.end_year) {
    return startStr;
  }
  const endStr = p.end_month
    ? `${MONTH_NAMES[p.end_month - 1]} ${p.end_year}`
    : `${p.end_year}`;
  return `${startStr} – ${endStr}`;
};

const getLinkTypeIcon = (type: ProjectLinkType) => {
  switch (type) {
    case 'GitHub':
    case 'Repository':
      return GitBranch;
    case 'Documentation':
      return FileText;
    case 'API':
      return Code;
    case 'Video Demo':
      return Video;
    case 'Live Demo':
    case 'Deployment':
    default:
      return Globe;
  }
};

export const ProjectDetailModal: React.FC<ProjectDetailModalProps> = ({ project, onClose }) => {
  const [copied, setCopied] = React.useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (project) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [project, onClose]);

  if (!project) return null;

  const timeline = formatTimeline(project);

  const handleCopy = async () => {
    const textToCopy = project.description || project.short_description || project.name;
    const ok = await copyToClipboard(textToCopy);
    if (ok) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    downloadProjectDossier(project);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/80 backdrop-blur-md animate-fadeIn"
      role="dialog"
      aria-modal="true"
      aria-labelledby="project-detail-title"
    >
      <div className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto glass-panel rounded-3xl p-6 sm:p-8 border border-slate-700/80 shadow-2xl bg-slate-900/95 space-y-6">
        {/* Top Header */}
        <div className="flex items-start justify-between gap-4 border-b border-slate-800 pb-5">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              {project.is_featured && (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-amber-500/15 text-amber-300 border border-amber-500/30">
                  <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                  Featured Project
                </span>
              )}
              {project.status && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                  {project.status}
                </span>
              )}
            </div>
            <h2 id="project-detail-title" className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {project.name}
            </h2>
            {timeline && (
              <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
                <Calendar className="w-3.5 h-3.5 text-slate-500" />
                <span>{timeline}</span>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Short Description */}
        {project.short_description && (
          <div className="text-sm sm:text-base text-slate-200 font-light leading-relaxed bg-slate-800/40 rounded-xl p-4 border border-slate-800">
            {project.short_description}
          </div>
        )}

        {/* Detailed Description */}
        {project.description && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>Overview & Architecture Dossier</span>
              </h4>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleCopy}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors cursor-pointer"
                  title="Copy formatted project overview and AI dossier"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5 text-slate-400" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={handleDownload}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors cursor-pointer"
                  title="Download project dossier as Markdown (.md)"
                >
                  <Download className="w-3.5 h-3.5 text-slate-400" />
                  <span>Download (.md)</span>
                </button>
              </div>
            </div>
            <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap font-light bg-slate-950/40 rounded-xl p-4 border border-slate-800/80">
              {project.description}
            </div>
          </div>
        )}

        {/* Technology Stack */}
        {project.technologies && project.technologies.length > 0 && (
          <div className="space-y-2.5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-indigo-400" />
              Technology Stack ({project.technologies.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {project.technologies.map((tech) => (
                <div
                  key={tech.id}
                  className="px-3 py-1.5 rounded-xl text-xs font-medium bg-slate-800/80 text-slate-200 border border-slate-700/80 flex items-center gap-1.5"
                >
                  <span className="font-semibold">{tech.name}</span>
                  {tech.category && tech.category !== 'Other' && (
                    <span className="text-[10px] text-slate-400 font-normal">
                      • {tech.category}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Deployment & Demo Links */}
        {project.links && project.links.length > 0 && (
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Deployments & Links ({project.links.length})
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {project.links.map((link) => {
                const IconComponent = getLinkTypeIcon(link.link_type);
                return (
                  <a
                    key={link.id}
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`flex items-center justify-between p-3 rounded-xl border transition-all ${
                      link.is_primary
                        ? 'bg-indigo-600/15 border-indigo-500/40 hover:bg-indigo-600/25 text-indigo-200'
                        : 'bg-slate-800/60 border-slate-700/80 hover:bg-slate-800 text-slate-200'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <IconComponent className="w-4 h-4 shrink-0 text-indigo-400" />
                      <div className="min-w-0">
                        <div className="text-xs font-semibold truncate flex items-center gap-1.5">
                          <span>{link.label}</span>
                          {link.is_primary && (
                            <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-indigo-500 text-white uppercase">
                              Primary
                            </span>
                          )}
                        </div>
                        <div className="text-[10px] text-slate-400 truncate font-mono">
                          {link.url}
                        </div>
                      </div>
                    </div>
                    <ExternalLink className="w-3.5 h-3.5 shrink-0 ml-2 text-slate-400" />
                  </a>
                );
              })}
            </div>
          </div>
        )}

        {/* Associated Skills */}
        {project.skills && project.skills.length > 0 && (
          <div className="space-y-2.5 pt-2 border-t border-slate-800/80">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5 text-purple-400" />
              Associated 7-Level Skills
            </h4>
            <div className="flex flex-wrap gap-2">
              {[...project.skills]
                .sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0) || a.name.localeCompare(b.name))
                .map((skill) => (
                <div
                  key={skill.id}
                  className="px-3 py-1 rounded-xl text-xs bg-purple-500/10 text-purple-300 border border-purple-500/20 flex items-center gap-2"
                >
                  <span className="font-semibold">{skill.name}</span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-200">
                    L{skill.rating} {skill.level_label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
          <button
            type="button"
            onClick={handleDownload}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors cursor-pointer"
          >
            <Download className="w-3.5 h-3.5 text-indigo-400" />
            <span>Download Project Dossier (.md)</span>
          </button>
          <button
            type="button"
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
