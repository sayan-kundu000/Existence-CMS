import React from 'react';
import {
  ExternalLink,
  GitBranch,
  Globe,
  FileText,
  Code,
  Video,
  Layers,
  Calendar,
  Star,
  Info
} from 'lucide-react';
import { Project, ProjectLink, ProjectLinkType } from '../../types';

interface ProjectCardProps {
  project: Project;
  onOpenDetail?: (project: Project) => void;
}

const MONTH_NAMES = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

const formatProjectDates = (p: Project): string | null => {
  if (!p.start_year) return null;
  const startStr = p.start_month
    ? `${MONTH_NAMES[p.start_month - 1]} ${p.start_year}`
    : `${p.start_year}`;

  if (p.is_current) {
    return `${startStr} – Present`;
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

const getCategoryColor = (category?: string) => {
  switch (category?.toLowerCase()) {
    case 'programming language':
      return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
    case 'framework':
      return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';
    case 'database':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    case 'cloud/deployment':
    case 'devops':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    case 'frontend':
      return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
    case 'backend':
      return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
    case 'data/ai':
      return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
    default:
      return 'bg-slate-800 text-slate-300 border-slate-700';
  }
};

const getStatusColor = (status?: string) => {
  switch (status) {
    case 'Completed':
      return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
    case 'In Progress':
      return 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30';
    case 'Planned':
      return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
    case 'Archived':
      return 'bg-slate-700/50 text-slate-400 border-slate-600/30';
    default:
      return 'bg-slate-800 text-slate-300 border-slate-700';
  }
};

export const ProjectCard: React.FC<ProjectCardProps> = ({ project, onOpenDetail }) => {
  const dates = formatProjectDates(project);
  const primaryLink = project.primary_link || (project.links && project.links.length > 0 ? project.links[0] : null);
  const additionalLinks = project.links ? project.links.filter(l => l.id !== primaryLink?.id && l.is_visible) : [];

  return (
    <div className="group relative flex flex-col justify-between glass-panel rounded-2xl p-6 sm:p-7 border border-slate-800/80 hover:border-indigo-500/40 transition-all duration-300 shadow-lg hover:shadow-indigo-500/5 bg-slate-900/60 hover:bg-slate-900/90">
      {/* Top Header & Badges */}
      <div className="space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2">
            {project.is_featured && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-300 border border-amber-500/30 shadow-sm">
                <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                Featured
              </span>
            )}
            {project.status && (
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-semibold border ${getStatusColor(project.status)}`}>
                {project.status}
              </span>
            )}
            {!project.is_visible && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-rose-500/10 text-rose-400 border border-rose-500/20">
                Private Draft
              </span>
            )}
          </div>

          {dates && (
            <div className="flex items-center gap-1.5 text-xs text-slate-400 shrink-0 font-mono">
              <Calendar className="w-3.5 h-3.5 text-slate-500" />
              <span>{dates}</span>
            </div>
          )}
        </div>

        {/* Project Title */}
        <div>
          <h3 className="text-xl sm:text-2xl font-bold text-white tracking-tight group-hover:text-indigo-200 transition-colors">
            {project.name}
          </h3>
          {project.short_description && (
            <p className="mt-2 text-sm text-slate-300 font-light leading-relaxed line-clamp-2">
              {project.short_description}
            </p>
          )}
        </div>

        {/* Tech Stack Chips */}
        {project.technologies && project.technologies.length > 0 && (
          <div className="space-y-1.5 pt-1">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
              <Layers className="w-3 h-3" /> Tech Stack
            </span>
            <div className="flex flex-wrap gap-1.5">
              {project.technologies.map((tech) => (
                <span
                  key={tech.id}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition-colors ${getCategoryColor(tech.category)}`}
                  title={tech.category ? `Category: ${tech.category}` : undefined}
                >
                  {tech.name}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Action Links & Footer */}
      <div className="pt-6 mt-6 border-t border-slate-800/80 space-y-3">
        {/* Primary Link Button & Secondary Links */}
        <div className="flex flex-wrap items-center justify-between gap-2.5">
          {primaryLink ? (
            <a
              href={primaryLink.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white shadow-md shadow-indigo-600/20 transition-all hover:scale-102 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400"
              aria-label={`Open primary link: ${primaryLink.label} for ${project.name}`}
            >
              {(() => {
                const IconComponent = getLinkTypeIcon(primaryLink.link_type);
                return <IconComponent className="w-3.5 h-3.5" />;
              })()}
              <span>{primaryLink.label}</span>
              <ExternalLink className="w-3 h-3 text-indigo-200" />
            </a>
          ) : (
            <span className="text-xs text-slate-400 italic">No deployment link</span>
          )}

          {/* Additional Links Buttons */}
          <div className="flex flex-wrap items-center gap-1.5">
            {additionalLinks.map((link) => {
              const IconComp = getLinkTypeIcon(link.link_type);
              return (
                <a
                  key={link.id}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-700 border border-slate-700/60 transition-colors"
                  title={`${link.link_type}: ${link.url}`}
                  aria-label={`${link.label} for ${project.name}`}
                >
                  <IconComp className="w-3.5 h-3.5 text-slate-400" />
                  <span>{link.label}</span>
                </a>
              );
            })}

            {/* Read Detail modal button */}
            {onOpenDetail && (
              <button
                type="button"
                onClick={() => onOpenDetail(project)}
                className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-indigo-300 hover:text-white hover:bg-indigo-600/20 border border-indigo-500/20 transition-colors cursor-pointer"
                title="View full project details"
              >
                <Info className="w-3.5 h-3.5" />
                <span>Details</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
