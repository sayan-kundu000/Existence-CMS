import React, { useState, useMemo } from 'react';
import {
  FolderCode,
  Search,
  Filter,
  Star,
  Layers,
  Sparkles,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { Project } from '../../types';
import { ProjectCard } from './ProjectCard';
import { ProjectDetailModal } from './ProjectDetailModal';

interface ProjectsViewProps {
  projects: Project[];
}

export const ProjectsView: React.FC<ProjectsViewProps> = ({ projects }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTech, setSelectedTech] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null);
  const [featuredOnly, setFeaturedOnly] = useState(false);
  const [activeDetailProject, setActiveDetailProject] = useState<Project | null>(null);

  // Extract all unique technologies across projects
  const availableTechnologies = useMemo(() => {
    const techSet = new Set<string>();
    projects.forEach((p) => {
      p.technologies?.forEach((t) => {
        if (t.name) techSet.add(t.name);
      });
    });
    return Array.from(techSet).sort((a, b) => a.localeCompare(b));
  }, [projects]);

  // Filter projects based on user controls
  const filteredProjects = useMemo(() => {
    return projects.filter((p) => {
      // 1. Visibility (public view only renders visible projects)
      if (p.is_visible === false) return false;

      // 2. Featured filter
      if (featuredOnly && !p.is_featured) return false;

      // 3. Status filter
      if (selectedStatus && p.status !== selectedStatus) return false;

      // 4. Technology filter
      if (selectedTech) {
        const hasTech = p.technologies?.some(
          (t) => t.name.toLowerCase() === selectedTech.toLowerCase()
        );
        if (!hasTech) return false;
      }

      // 5. Search query
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase().trim();
        const matchName = p.name.toLowerCase().includes(query);
        const matchShort = p.short_description?.toLowerCase().includes(query) || false;
        const matchDesc = p.description?.toLowerCase().includes(query) || false;
        const matchTech = p.technologies?.some((t) => t.name.toLowerCase().includes(query)) || false;
        if (!matchName && !matchShort && !matchDesc && !matchTech) return false;
      }

      return true;
    });
  }, [projects, searchQuery, selectedTech, selectedStatus, featuredOnly]);

  const featuredProjects = useMemo(() => {
    return projects.filter((p) => p.is_visible !== false && p.is_featured);
  }, [projects]);

  return (
    <div className="space-y-10 animate-fadeIn max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Header */}
      <div className="text-center max-w-3xl mx-auto space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
          <FolderCode className="w-4 h-4" />
          <span>Projects & Tech Stack Engine</span>
        </div>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight">
          Portfolio & Engineering Systems
        </h1>
        <p className="text-sm sm:text-base text-slate-300 font-light leading-relaxed">
          Production systems, architectural prototypes, technology stacks, and live deployment coordinates.
        </p>
      </div>

      {/* Featured Showcase (if any featured projects exist and no specific filters active) */}
      {!searchQuery && !selectedTech && !selectedStatus && !featuredOnly && featuredProjects.length > 0 && (
        <div className="space-y-4 pt-2">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-amber-300">
            <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
            <span>Featured Highlights</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {featuredProjects.map((proj) => (
              <ProjectCard
                key={`featured-${proj.id}`}
                project={proj}
                onOpenDetail={(p) => setActiveDetailProject(p)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Search & Filter Controls */}
      <div className="glass-panel rounded-2xl p-5 sm:p-6 border border-slate-800 space-y-4 bg-slate-900/60">
        <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search projects by name, description, or technology..."
              className="w-full pl-10 pr-4 py-2 rounded-xl text-xs sm:text-sm bg-slate-950/80 border border-slate-700/80 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-white"
              >
                Clear
              </button>
            )}
          </div>

          {/* Quick Filters */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => setFeaturedOnly(!featuredOnly)}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                featuredOnly
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 shadow-sm'
                  : 'bg-slate-800 text-slate-300 border-slate-700 hover:text-white'
              }`}
            >
              <Star className={`w-3.5 h-3.5 ${featuredOnly ? 'fill-amber-400 text-amber-400' : ''}`} />
              <span>Featured Only</span>
            </button>

            <select
              value={selectedStatus || ''}
              onChange={(e) => setSelectedStatus(e.target.value || null)}
              className="px-3 py-1.5 rounded-xl text-xs bg-slate-800 border border-slate-700 text-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
            >
              <option value="">All Statuses</option>
              <option value="Completed">Completed</option>
              <option value="In Progress">In Progress</option>
              <option value="Planned">Planned</option>
              <option value="Archived">Archived</option>
            </select>
          </div>
        </div>

        {/* Technology Filter Chips */}
        {availableTechnologies.length > 0 && (
          <div className="space-y-2 pt-2 border-t border-slate-800/80">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
              <Layers className="w-3 h-3" /> Filter by Technology:
            </div>
            <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
              <button
                type="button"
                onClick={() => setSelectedTech(null)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition-colors cursor-pointer ${
                  selectedTech === null
                    ? 'bg-indigo-600 text-white border-indigo-500'
                    : 'bg-slate-800/80 text-slate-300 border-slate-700/60 hover:text-white'
                }`}
              >
                All Tech
              </button>
              {availableTechnologies.map((tech) => (
                <button
                  key={tech}
                  type="button"
                  onClick={() => setSelectedTech(selectedTech === tech ? null : tech)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition-colors cursor-pointer ${
                    selectedTech === tech
                      ? 'bg-indigo-600 text-white border-indigo-500'
                      : 'bg-slate-800/80 text-slate-300 border-slate-700/60 hover:text-white'
                  }`}
                >
                  {tech}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Projects Grid */}
      {filteredProjects.length > 0 ? (
        <div className="space-y-4">
          <div className="text-xs text-slate-400 font-medium">
            Showing {filteredProjects.length} {filteredProjects.length === 1 ? 'project' : 'projects'}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProjects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onOpenDetail={(p) => setActiveDetailProject(p)}
              />
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-16 px-4 glass-panel rounded-3xl border border-slate-800/80 bg-slate-900/40 space-y-4">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <FolderCode className="w-7 h-7" />
          </div>
          <h3 className="text-lg font-bold text-white">No Projects Found</h3>
          <p className="text-xs sm:text-sm text-slate-400 max-w-md mx-auto font-light">
            {projects.length === 0
              ? 'No projects have been published yet. The profile owner will curate and add their portfolio projects soon.'
              : 'No projects match your current search and filter criteria. Try resetting filters or clearing the search.'}
          </p>
          {(searchQuery || selectedTech || selectedStatus || featuredOnly) && (
            <button
              type="button"
              onClick={() => {
                setSearchQuery('');
                setSelectedTech(null);
                setSelectedStatus(null);
                setFeaturedOnly(false);
              }}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors cursor-pointer"
            >
              Reset Filters
            </button>
          )}
        </div>
      )}

      {/* Project Detail Modal */}
      {activeDetailProject && (
        <ProjectDetailModal
          project={activeDetailProject}
          onClose={() => setActiveDetailProject(null)}
        />
      )}
    </div>
  );
};
