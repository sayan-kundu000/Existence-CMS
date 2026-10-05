import React, { useState, useEffect } from 'react';
import {
  FolderCode,
  Plus,
  Trash2,
  Edit2,
  Save,
  X,
  Star,
  Eye,
  EyeOff,
  ArrowUp,
  ArrowDown,
  Layers,
  Globe,
  Award,
  GitBranch,
  Sparkles,
  RefreshCw,
  Zap,
  Unlink,
  Copy,
  Check,
  ExternalLink,
  Link2,
  ShieldCheck,
  AlertCircle,
  Key,
  HelpCircle
} from 'lucide-react';
import { Project, Skill, ProjectStatus, GitHubAccountLink } from '../../types';
import { api } from '../../services/api';
import { TechnologySelector, TechItem } from '../projects/TechnologySelector';
import { ProjectLinkEditor, EditableLink } from '../projects/ProjectLinkEditor';
import { GithubExtractionModal } from './GithubExtractionModal';
import { synthesizeAiDossier } from '../../utils/githubExtractor';

interface CmsProjectsSectionProps {
  projects: Project[];
  skills: Skill[];
  onRefresh: () => void;
  executeWithPin: (action: () => Promise<void>) => void;
  notify: (type: 'success' | 'error', text: string) => void;
}

const PROJECT_STATUSES: ProjectStatus[] = ['Planned', 'In Progress', 'Completed', 'Archived'];

export const CmsProjectsSection: React.FC<CmsProjectsSectionProps> = ({
  projects,
  skills,
  onRefresh,
  executeWithPin,
  notify
}) => {
  const [editingProjectId, setEditingProjectId] = useState<number | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [extractModalOpen, setExtractModalOpen] = useState(false);

  // GitHub Auto-Sync states
  const [githubLink, setGithubLink] = useState<GitHubAccountLink | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [webhookModalOpen, setWebhookModalOpen] = useState(false);
  const [copiedWebhook, setCopiedWebhook] = useState(false);
  const [linkAccountModalOpen, setLinkAccountModalOpen] = useState(false);
  const [linkUrlInput, setLinkUrlInput] = useState('');
  const [linkTokenInput, setLinkTokenInput] = useState('');
  const [isLinkingAccount, setIsLinkingAccount] = useState(false);
  const [linkError, setLinkError] = useState<string | null>(null);

  useEffect(() => {
    loadGithubLink();
  }, []);

  const loadGithubLink = async () => {
    try {
      const link = await api.getGithubLink();
      setGithubLink(link);
    } catch {
      // not linked or unauthenticated
    }
  };

  const handleSyncGithub = () => {
    executeWithPin(async () => {
      setIsSyncing(true);
      try {
        const res = await api.syncGithubProjects();
        notify('success', res.message || `Synced with GitHub: ${res.created_count} added, ${res.updated_count} updated.`);
        await loadGithubLink();
        onRefresh();
      } catch (err: any) {
        notify('error', err.message || 'Failed to synchronize with GitHub.');
      } finally {
        setIsSyncing(false);
      }
    });
  };

  const handleUnlinkGithub = () => {
    if (!window.confirm('Are you sure you want to unlink this GitHub account? Automatic synchronization will be paused.')) return;
    executeWithPin(async () => {
      try {
        await api.unlinkGithubAccount();
        setGithubLink(null);
        notify('success', 'GitHub account unlinked successfully.');
      } catch (err: any) {
        notify('error', err.message || 'Failed to unlink account.');
      }
    });
  };

  const handleManualLinkAccount = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanUrl = linkUrlInput.trim();
    if (!cleanUrl) {
      notify('error', 'Please enter a GitHub profile or repository URL.');
      return;
    }
    setLinkError(null);
    executeWithPin(async () => {
      setIsLinkingAccount(true);
      try {
        const link = await api.saveGithubLink({
          github_url: cleanUrl,
          custom_token: linkTokenInput.trim() || undefined,
          auto_sync: true
        });
        setGithubLink(link);
        if (link.last_sync_status === 'error') {
          const errMsg = link.last_sync_summary || 'Repositories could not be loaded due to GitHub API rate limits.';
          setLinkError(errMsg);
          notify('error', `Linked @${link.username}, but initial sync had an issue: ${errMsg}`);
          onRefresh();
        } else {
          setLinkAccountModalOpen(false);
          setLinkUrlInput('');
          setLinkTokenInput('');
          notify('success', `Linked GitHub account @${link.username}! ${link.last_sync_summary || 'Repositories synchronized successfully.'}`);
          onRefresh();
        }
      } catch (err: any) {
        const msg = err.message || 'Failed to link GitHub account.';
        setLinkError(msg);
        notify('error', msg);
      } finally {
        setIsLinkingAccount(false);
      }
    });
  };


  // Form states
  const [name, setName] = useState('');
  const [shortDesc, setShortDesc] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<ProjectStatus>('Completed');
  const [startMonth, setStartMonth] = useState<number | ''>('');
  const [startYear, setStartYear] = useState<number | ''>('');
  const [endMonth, setEndMonth] = useState<number | ''>('');
  const [endYear, setEndYear] = useState<number | ''>('');
  const [isCurrent, setIsCurrent] = useState(false);
  const [isFeatured, setIsFeatured] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [techList, setTechList] = useState<TechItem[]>([]);
  const [linksList, setLinksList] = useState<EditableLink[]>([]);
  const [selectedSkillIds, setSelectedSkillIds] = useState<number[]>([]);

  const resetForm = () => {
    setEditingProjectId(null);
    setName('');
    setShortDesc('');
    setDescription('');
    setStatus('Completed');
    setStartMonth('');
    setStartYear('');
    setEndMonth('');
    setEndYear('');
    setIsCurrent(false);
    setIsFeatured(false);
    setIsVisible(true);
    setTechList([]);
    setLinksList([]);
    setSelectedSkillIds([]);
    setFormOpen(false);
  };

  const handleStartEdit = (proj: Project) => {
    setEditingProjectId(proj.id);
    setName(proj.name);
    setShortDesc(proj.short_description || '');
    setDescription(proj.description || '');
    setStatus(proj.status || 'Completed');
    setStartMonth(proj.start_month ?? '');
    setStartYear(proj.start_year ?? '');
    setEndMonth(proj.end_month ?? '');
    setEndYear(proj.end_year ?? '');
    setIsCurrent(proj.is_current);
    setIsFeatured(proj.is_featured);
    setIsVisible(proj.is_visible);

    setTechList(
      (proj.technologies || []).map((t) => ({
        name: t.name,
        category: (t.category as any) || 'Other'
      }))
    );

    setLinksList(
      (proj.links || []).map((l) => ({
        id: l.id,
        label: l.label,
        url: l.url,
        link_type: l.link_type,
        is_primary: l.is_primary,
        is_visible: l.is_visible,
        display_order: l.display_order
      }))
    );

    setSelectedSkillIds((proj.skills || []).map((s) => s.id));
    setFormOpen(true);
  };

  const [isGeneratingAi, setIsGeneratingAi] = useState(false);

  const handleGenerateAiDossier = async () => {
    const cleanName = name.trim();
    if (!cleanName) {
      notify('error', 'Please enter a project name first.');
      return;
    }

    setIsGeneratingAi(true);
    try {
      const techPayload = techList.map((t) => ({ name: t.name, category: t.category }));
      const linksPayload = linksList.map((l) => ({
        label: l.label,
        url: l.url,
        link_type: l.link_type,
        is_primary: l.is_primary
      }));

      let result: { short_description: string; description: string };
      try {
        result = await api.generateAiDossier({
          name: cleanName,
          raw_description: shortDesc.trim() || undefined,
          technologies: techPayload,
          links: linksPayload
        });
      } catch (err) {
        // Graceful fallback to client-side synthesizer
        const clientResult = synthesizeAiDossier(
          cleanName,
          shortDesc.trim(),
          techList[0]?.name || null,
          [],
          techList.map((t, idx) => ({ id: idx, name: t.name, category: t.category || 'Other' })),
          linksList.map((l, idx) => ({
            label: l.label,
            url: l.url,
            link_type: l.link_type,
            is_primary: l.is_primary,
            is_visible: true,
            display_order: idx
          })),
          0
        );
        result = { short_description: clientResult.shortDesc, description: clientResult.fullDossier };
      }

      setShortDesc(result.short_description);
      setDescription(result.description);
      notify('success', '✨ Super-simple AI project details generated successfully! Review and save whenever you are ready.');
    } catch (err: any) {
      notify('error', err.message || 'Failed to generate AI project details.');
    } finally {
      setIsGeneratingAi(false);
    }
  };

  const handleSaveProject = () => {
    const cleanName = name.trim();
    if (!cleanName) {
      notify('error', 'Project name is required.');
      return;
    }

    if (isCurrent && (endMonth !== '' || endYear !== '')) {
      notify('error', 'Active projects cannot have an ending date.');
      return;
    }

    if (!isCurrent && startYear !== '' && endYear !== '') {
      const sY = Number(startYear);
      const eY = Number(endYear);
      if (eY < sY) {
        notify('error', 'End year cannot be earlier than start year.');
        return;
      }
      if (eY === sY && startMonth !== '' && endMonth !== '') {
        if (Number(endMonth) < Number(startMonth)) {
          notify('error', 'End month cannot precede start month in the same year.');
          return;
        }
      }
    }

    const payload = {
      name: cleanName,
      short_description: shortDesc.trim() || null,
      description: description.trim() || null,
      status,
      start_month: startMonth !== '' ? Number(startMonth) : null,
      start_year: startYear !== '' ? Number(startYear) : null,
      end_month: isCurrent ? null : (endMonth !== '' ? Number(endMonth) : null),
      end_year: isCurrent ? null : (endYear !== '' ? Number(endYear) : null),
      is_current: isCurrent,
      is_featured: isFeatured,
      is_visible: isVisible,
      technologies: techList.map((t) => ({ name: t.name, category: t.category || 'Other' })),
      links: linksList.map((l, idx) => ({
        label: l.label,
        url: l.url,
        link_type: l.link_type,
        is_primary: l.is_primary,
        is_visible: l.is_visible,
        display_order: idx
      })),
      skill_ids: selectedSkillIds
    };

    executeWithPin(async () => {
      if (editingProjectId) {
        await api.updateProject(editingProjectId, payload);
        notify('success', `Project '${cleanName}' updated successfully.`);
      } else {
        await api.createProject(payload);
        notify('success', `Project '${cleanName}' created successfully.`);
      }
      resetForm();
      onRefresh();
    });
  };

  const handleDeleteProject = (proj: Project) => {
    if (!confirm(`Are you sure you want to delete project '${proj.name}'? This action is protected and cannot be undone.`)) {
      return;
    }

    executeWithPin(async () => {
      await api.deleteProject(proj.id);
      notify('success', `Project '${proj.name}' deleted.`);
      onRefresh();
    });
  };

  const handleMoveProject = (index: number, direction: 'up' | 'down') => {
    const targetIdx = direction === 'up' ? index - 1 : index + 1;
    if (targetIdx < 0 || targetIdx >= projects.length) return;

    const copy = [...projects];
    const temp = copy[index];
    copy[index] = copy[targetIdx];
    copy[targetIdx] = temp;

    const reorderPayload = copy.map((p, idx) => ({
      id: p.id,
      display_order: idx
    }));

    executeWithPin(async () => {
      await api.reorderProjects(reorderPayload);
      notify('success', 'Projects reordered successfully.');
      onRefresh();
    });
  };

  const handleToggleVisibility = (proj: Project) => {
    executeWithPin(async () => {
      await api.patchProject(proj.id, { is_visible: !proj.is_visible });
      notify('success', `Project visibility toggled to ${!proj.is_visible ? 'Public' : 'Private'}.`);
      onRefresh();
    });
  };

  const handleToggleFeatured = (proj: Project) => {
    executeWithPin(async () => {
      await api.patchProject(proj.id, { is_featured: !proj.is_featured });
      notify('success', `Project ${!proj.is_featured ? 'marked as featured' : 'unmarked from featured'}.`);
      onRefresh();
    });
  };

  const toggleSkillSelection = (skillId: number) => {
    if (selectedSkillIds.includes(skillId)) {
      setSelectedSkillIds(selectedSkillIds.filter((id) => id !== skillId));
    } else {
      setSelectedSkillIds([...selectedSkillIds, skillId]);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 glass-card p-5 rounded-2xl border border-slate-800">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <FolderCode className="w-5 h-5 text-indigo-400" />
            <span>Projects & Tech Stack Engine</span>
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Manage projects, technology stack metadata, and attach multiple deployment/demo links per project.
          </p>
        </div>

        {!formOpen && (
          <div className="flex flex-wrap items-center gap-2.5 shrink-0">
            {!githubLink && (
              <button
                type="button"
                onClick={() => setLinkAccountModalOpen(true)}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-slate-800/90 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold border border-slate-700/80 transition-colors cursor-pointer"
              >
                <Link2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Connect GitHub</span>
              </button>
            )}
            <button
              type="button"
              onClick={() => setExtractModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-xs font-semibold shadow-md transition-all cursor-pointer"
            >
              <GitBranch className="w-4 h-4 text-emerald-200" />
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>Extract from GitHub</span>
            </button>
            <button
              type="button"
              onClick={() => {
                resetForm();
                setFormOpen(true);
              }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-md transition-all cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>Add New Project</span>
            </button>
          </div>
        )}
      </div>

      {/* GitHub Account Link & Real-time Auto-Sync Status Card */}
      {githubLink && !formOpen && (
        <div className="glass-panel p-4 sm:p-5 rounded-2xl border border-indigo-500/30 bg-gradient-to-r from-slate-900 via-indigo-950/30 to-slate-900 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4 animate-fadeIn">
          <div className="flex items-start sm:items-center gap-3.5">
            <div className="w-10 h-10 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 shrink-0">
              <GitBranch className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm font-bold text-white">GitHub Auto-Sync Active</span>
                <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  @{githubLink.username}
                </span>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Real-time Updates
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                New repositories are extracted automatically. Repository changes (e.g. backend removed/added) dynamically re-classify tech stack & generate updated AI dossiers.
                {githubLink.last_synced_at && (
                  <span className="ml-1 text-slate-500">
                    • Last synced: {new Date(githubLink.last_synced_at).toLocaleString()}
                  </span>
                )}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0 flex-wrap">
            <button
              type="button"
              onClick={handleSyncGithub}
              disabled={isSyncing}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white transition-all shadow-md cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
              <span>{isSyncing ? 'Syncing...' : 'Sync with GitHub'}</span>
            </button>
            <button
              type="button"
              onClick={() => setWebhookModalOpen(true)}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors cursor-pointer"
            >
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>Webhook Setup</span>
            </button>
            <button
              type="button"
              onClick={handleUnlinkGithub}
              className="p-2 text-slate-400 hover:text-rose-400 rounded-xl hover:bg-rose-500/10 transition-colors cursor-pointer"
              title="Unlink GitHub account"
            >
              <Unlink className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}


      {/* Project Form (Create / Edit) */}
      {formOpen && (
        <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-indigo-500/30 bg-slate-900/90 shadow-xl space-y-6 animate-fadeIn">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <FolderCode className="w-4 h-4 text-indigo-400" />
              <span>{editingProjectId ? 'Edit Project' : 'Create New Project'}</span>
            </h4>
            <button
              type="button"
              onClick={resetForm}
              className="text-slate-400 hover:text-white p-1 rounded-lg transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-4">
            {/* Project Name & Status */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Project Title <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Existence CMS Platform"
                  className="w-full px-3.5 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Status</label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value as ProjectStatus)}
                  className="w-full px-3.5 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
                >
                  {PROJECT_STATUSES.map((st) => (
                    <option key={st} value={st}>
                      {st}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Short Description */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Short Description (Card Summary)
              </label>
              <input
                type="text"
                value={shortDesc}
                onChange={(e) => setShortDesc(e.target.value)}
                placeholder="Concise overview suitable for portfolio preview cards..."
                className="w-full px-3.5 py-2 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* Detailed Description */}
            <div>
              <div className="flex items-center justify-between mb-1.5 gap-2">
                <label className="block text-xs font-semibold text-slate-300">
                  Detailed Overview & AI Project Dossier
                </label>
                <button
                  type="button"
                  onClick={handleGenerateAiDossier}
                  disabled={isGeneratingAi || !name.trim()}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold text-amber-300 bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 transition-all shadow-sm cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                  title="Generate a massively big, advancedly detailed AI project dossier in super simple everyday words"
                >
                  <Sparkles className={`w-3.5 h-3.5 text-amber-400 ${isGeneratingAi ? 'animate-spin' : ''}`} />
                  <span>{isGeneratingAi ? 'Generating Dossier...' : '✨ Generate Super-Simple AI Details'}</span>
                </button>
              </div>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={8}
                placeholder="Comprehensive overview and architecture written in super simple everyday words..."
                className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 leading-relaxed font-mono"
              />
            </div>

            {/* Timeline & Active Flag */}
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
              <span className="text-xs font-semibold text-slate-300">Project Timeline</span>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div>
                  <label className="block text-[10px] text-slate-400 mb-1">Start Month (1-12)</label>
                  <input
                    type="number"
                    min={1}
                    max={12}
                    value={startMonth}
                    onChange={(e) => setStartMonth(e.target.value === '' ? '' : Number(e.target.value))}
                    placeholder="e.g. 1"
                    className="w-full px-3 py-1.5 rounded-lg text-xs bg-slate-900 border border-slate-700 text-white"
                  />
                </div>
                <div>
                  <label className="block text-[10px] text-slate-400 mb-1">Start Year</label>
                  <input
                    type="number"
                    min={1980}
                    max={2100}
                    value={startYear}
                    onChange={(e) => setStartYear(e.target.value === '' ? '' : Number(e.target.value))}
                    placeholder="e.g. 2025"
                    className="w-full px-3 py-1.5 rounded-lg text-xs bg-slate-900 border border-slate-700 text-white"
                  />
                </div>
                <div>
                  <label className="block text-[10px] text-slate-400 mb-1">End Month</label>
                  <input
                    type="number"
                    min={1}
                    max={12}
                    disabled={isCurrent}
                    value={isCurrent ? '' : endMonth}
                    onChange={(e) => setEndMonth(e.target.value === '' ? '' : Number(e.target.value))}
                    placeholder="e.g. 12"
                    className="w-full px-3 py-1.5 rounded-lg text-xs bg-slate-900 border border-slate-700 text-white disabled:opacity-40"
                  />
                </div>
                <div>
                  <label className="block text-[10px] text-slate-400 mb-1">End Year</label>
                  <input
                    type="number"
                    min={1980}
                    max={2100}
                    disabled={isCurrent}
                    value={isCurrent ? '' : endYear}
                    onChange={(e) => setEndYear(e.target.value === '' ? '' : Number(e.target.value))}
                    placeholder="e.g. 2026"
                    className="w-full px-3 py-1.5 rounded-lg text-xs bg-slate-900 border border-slate-700 text-white disabled:opacity-40"
                  />
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-6 pt-1">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isCurrent}
                    onChange={(e) => {
                      setIsCurrent(e.target.checked);
                      if (e.target.checked) {
                        setEndMonth('');
                        setEndYear('');
                      }
                    }}
                    className="w-4 h-4 rounded text-indigo-600 bg-slate-900 border-slate-700"
                  />
                  <span className="text-xs text-slate-300 font-medium">Currently Active Project</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isFeatured}
                    onChange={(e) => setIsFeatured(e.target.checked)}
                    className="w-4 h-4 rounded text-amber-500 bg-slate-900 border-slate-700"
                  />
                  <span className="text-xs text-amber-300 font-medium">Mark as Featured Highlight</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isVisible}
                    onChange={(e) => setIsVisible(e.target.checked)}
                    className="w-4 h-4 rounded text-indigo-600 bg-slate-900 border-slate-700"
                  />
                  <span className="text-xs text-slate-300 font-medium">Publicly Visible</span>
                </label>
              </div>
            </div>

            {/* Tech Stack Engine Section */}
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-indigo-400" />
                <span>Technologies & Tech Stack</span>
              </span>
              <TechnologySelector value={techList} onChange={setTechList} />
            </div>

            {/* Multiple Deployment Links Section */}
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5 text-indigo-400" />
                <span>Multiple Deployment & Demo Links</span>
              </span>
              <ProjectLinkEditor links={linksList} onChange={setLinksList} />
            </div>

            {/* Associated 7-Level Skills */}
            {skills.length > 0 && (
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
                <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <Award className="w-3.5 h-3.5 text-purple-400" />
                  <span>Associate Existing Verified Skills</span>
                </span>
                <p className="text-[11px] text-slate-400">
                  Select which skills from your 7-Level Mastery Engine apply to this project:
                </p>
                <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto">
                  {skills.map((skill) => {
                    const isSelected = selectedSkillIds.includes(skill.id);
                    return (
                      <button
                        key={skill.id}
                        type="button"
                        onClick={() => toggleSkillSelection(skill.id)}
                        className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition-colors cursor-pointer ${
                          isSelected
                            ? 'bg-purple-600 text-white border-purple-500 shadow-sm'
                            : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-white'
                        }`}
                      >
                        {skill.name} (L{skill.rating})
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={resetForm}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white border border-slate-800 hover:bg-slate-800 transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSaveProject}
              className="inline-flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition-all cursor-pointer"
            >
              <Save className="w-3.5 h-3.5" />
              <span>{editingProjectId ? 'Save Changes' : 'Publish Project'}</span>
            </button>
          </div>
        </div>
      )}

      {/* Projects List with Reordering */}
      <div className="space-y-3">
        {projects.length > 0 ? (
          projects.map((proj, idx) => (
            <div
              key={proj.id}
              className="glass-card p-4 sm:p-5 rounded-2xl border border-slate-800 hover:border-slate-700/80 flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all"
            >
              <div className="space-y-2 min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-mono text-slate-500">#{proj.display_order}</span>
                  <h4 className="text-base font-bold text-white truncate">{proj.name}</h4>
                  {proj.is_featured && (
                    <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">
                      <Star className="w-2.5 h-2.5 fill-amber-400" /> Featured
                    </span>
                  )}
                  {proj.status && (
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-semibold">
                      {proj.status}
                    </span>
                  )}
                  {!proj.is_visible && (
                    <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 font-bold uppercase">
                      Private Draft
                    </span>
                  )}
                </div>

                {proj.short_description && (
                  <p className="text-xs text-slate-400 line-clamp-1">{proj.short_description}</p>
                )}

                {/* Tech and Link summary counters */}
                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
                  <span className="flex items-center gap-1">
                    <Layers className="w-3.5 h-3.5 text-indigo-400" />
                    <span>{proj.technologies?.length || 0} technologies</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <Globe className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{proj.links?.length || 0} deployment links</span>
                  </span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 shrink-0 self-end md:self-center">
                {/* Reorder Buttons */}
                <button
                  type="button"
                  onClick={() => handleMoveProject(idx, 'up')}
                  disabled={idx === 0}
                  className="p-2 rounded-xl text-slate-400 hover:text-white bg-slate-900 border border-slate-800 disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
                  title="Move project up"
                >
                  <ArrowUp className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => handleMoveProject(idx, 'down')}
                  disabled={idx === projects.length - 1}
                  className="p-2 rounded-xl text-slate-400 hover:text-white bg-slate-900 border border-slate-800 disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
                  title="Move project down"
                >
                  <ArrowDown className="w-3.5 h-3.5" />
                </button>

                {/* Quick Toggle Featured */}
                <button
                  type="button"
                  onClick={() => handleToggleFeatured(proj)}
                  className={`p-2 rounded-xl border transition-colors cursor-pointer ${
                    proj.is_featured
                      ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                      : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-amber-300'
                  }`}
                  title={proj.is_featured ? 'Unfeature project' : 'Feature project'}
                >
                  <Star className={`w-3.5 h-3.5 ${proj.is_featured ? 'fill-amber-400' : ''}`} />
                </button>

                {/* Quick Toggle Visibility */}
                <button
                  type="button"
                  onClick={() => handleToggleVisibility(proj)}
                  className={`p-2 rounded-xl border transition-colors cursor-pointer ${
                    proj.is_visible
                      ? 'bg-slate-900 text-slate-300 border-slate-800 hover:text-white'
                      : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                  }`}
                  title={proj.is_visible ? 'Make Private' : 'Make Public'}
                >
                  {proj.is_visible ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                </button>

                {/* Edit Button */}
                <button
                  type="button"
                  onClick={() => handleStartEdit(proj)}
                  className="p-2 rounded-xl text-indigo-300 hover:text-white bg-indigo-600/10 hover:bg-indigo-600/30 border border-indigo-500/20 transition-colors cursor-pointer"
                  title="Edit project"
                >
                  <Edit2 className="w-3.5 h-3.5" />
                </button>

                {/* Delete Button */}
                <button
                  type="button"
                  onClick={() => handleDeleteProject(proj)}
                  className="p-2 rounded-xl text-rose-400 hover:text-white bg-rose-500/10 hover:bg-rose-600/40 border border-rose-500/20 transition-colors cursor-pointer"
                  title="Delete project"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12 glass-card rounded-2xl border border-dashed border-slate-800 space-y-4">
            <FolderCode className="w-10 h-10 text-indigo-400/60 mx-auto" />
            <h4 className="text-sm font-semibold text-slate-200">No Projects Configured Yet</h4>
            <p className="text-xs text-slate-400 max-w-md mx-auto font-light">
              Extract all your projects directly from GitHub with AI dossiers, or click &apos;Add New Project&apos; to create one manually.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
              <button
                type="button"
                onClick={() => setExtractModalOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-xs font-semibold shadow-md transition-all cursor-pointer"
              >
                <GitBranch className="w-4 h-4 text-emerald-200" />
                <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                <span>Extract from GitHub</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  resetForm();
                  setFormOpen(true);
                }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-md transition-all cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                <span>Add New Project</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* GitHub Extraction & AI Dossier Modal */}
      <GithubExtractionModal
        isOpen={extractModalOpen}
        onClose={() => setExtractModalOpen(false)}
        onImportComplete={() => {
          loadGithubLink();
          onRefresh();
        }}
        executeWithPin={executeWithPin}
        notify={notify}
      />

      {/* GitHub Webhook Setup Modal */}
      {webhookModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-slate-950/85 backdrop-blur-md animate-fadeIn">
          <div className="relative w-full max-w-xl glass-panel rounded-3xl border border-indigo-500/30 bg-slate-900/95 shadow-2xl p-6 sm:p-7 space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center">
                  <Zap className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">GitHub Real-time Webhook Setup</h4>
                  <p className="text-[11px] text-slate-400">Automate real-time updates directly from GitHub</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setWebhookModalOpen(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              When a webhook is configured in your GitHub repository or account settings, GitHub will automatically ping Existence CMS whenever you push code changes or create new repositories.
            </p>

            <div className="space-y-3 bg-slate-950/80 p-4 rounded-2xl border border-slate-800">
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">Payload URL</label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    readOnly
                    value={`${typeof window !== 'undefined' ? window.location.origin : ''}/api/v1/projects/github-webhook`}
                    className="w-full px-3 py-1.5 rounded-lg text-xs bg-slate-900 border border-slate-700 text-indigo-300 font-mono select-all focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      const url = `${typeof window !== 'undefined' ? window.location.origin : ''}/api/v1/projects/github-webhook`;
                      navigator.clipboard.writeText(url);
                      setCopiedWebhook(true);
                      setTimeout(() => setCopiedWebhook(false), 2000);
                      notify('success', 'Webhook URL copied to clipboard!');
                    }}
                    className="inline-flex items-center gap-1 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold cursor-pointer shrink-0"
                  >
                    {copiedWebhook ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedWebhook ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-1">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Content type</label>
                  <div className="px-3 py-1.5 rounded-lg text-xs bg-slate-900 border border-slate-800 text-slate-200 font-mono">
                    application/json
                  </div>
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Which events to trigger?</label>
                  <div className="px-3 py-1.5 rounded-lg text-xs bg-slate-900 border border-slate-800 text-slate-200">
                    Just the push event & repositories
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-2 text-xs text-slate-400 bg-indigo-950/20 p-3.5 rounded-xl border border-indigo-500/20">
              <span className="font-semibold text-indigo-300 block">✨ What happens on code changes:</span>
              <ul className="list-disc list-inside space-y-1 text-[11px]">
                <li>If you add a new repo, it is automatically extracted with AI dossier & links.</li>
                <li>If you delete or add backend/frontend dependencies, the tech stack is cleaned up and the AI architecture & description are regenerated automatically!</li>
              </ul>
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="button"
                onClick={() => setWebhookModalOpen(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-semibold cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Manual Connect GitHub Modal */}
      {linkAccountModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-slate-950/85 backdrop-blur-md animate-fadeIn">
          <div className="relative w-full max-w-lg glass-panel rounded-3xl border border-indigo-500/30 bg-slate-900/95 shadow-2xl p-6 sm:p-7 space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center">
                  <Link2 className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">Connect GitHub Account</h4>
                  <p className="text-[11px] text-slate-400">Enable automatic repository synchronization & AI dossiers</p>
                </div>
              </div>
              <button
                type="button"
                disabled={isLinkingAccount}
                onClick={() => {
                  setLinkAccountModalOpen(false);
                  setLinkError(null);
                }}
                className="text-slate-400 hover:text-white p-1 rounded-lg disabled:opacity-50"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {linkError && (
              <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-2.5">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                <div className="space-y-1">
                  <span className="font-semibold block">Connection or Sync Issue</span>
                  <p className="text-[11px] leading-relaxed text-rose-200/90">{linkError}</p>
                  <p className="text-[11px] text-slate-300 pt-1">
                    If GitHub is rate-limiting your connection, generate a free Personal Access Token below to immediately bypass limits.
                  </p>
                </div>
              </div>
            )}

            <form onSubmit={handleManualLinkAccount} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  GitHub Profile, Handle, or Repository <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  required
                  disabled={isLinkingAccount}
                  value={linkUrlInput}
                  onChange={(e) => setLinkUrlInput(e.target.value)}
                  placeholder="e.g. https://github.com/octocat, @octocat, or octocat"
                  className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
                />
                <p className="text-[10px] text-slate-400 mt-1">
                  Paste your GitHub profile URL, handle, or a single repository URL.
                </p>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-xs font-semibold text-slate-300">
                    Personal Access Token <span className="text-slate-500 font-normal">(Recommended for rate limits)</span>
                  </label>
                  <a
                    href="https://github.com/settings/tokens/new?description=Existence+CMS+Portfolio&scopes=public_repo"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[11px] text-indigo-400 hover:text-indigo-300 hover:underline"
                  >
                    <span>Generate Free Token</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
                <input
                  type="password"
                  disabled={isLinkingAccount}
                  value={linkTokenInput}
                  onChange={(e) => setLinkTokenInput(e.target.value)}
                  placeholder="ghp_... (classic token with public_repo scope)"
                  className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
                />
                <p className="text-[10px] text-slate-400 mt-1">
                  Unauthenticated GitHub requests are capped at 60/hr. Providing a classic token unlocks 5,000 requests/hr.
                </p>
              </div>

              <div className="flex justify-end gap-2.5 pt-2">
                <button
                  type="button"
                  disabled={isLinkingAccount}
                  onClick={() => {
                    setLinkAccountModalOpen(false);
                    setLinkError(null);
                  }}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-semibold cursor-pointer disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLinkingAccount}
                  className="inline-flex items-center gap-1.5 px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-md cursor-pointer disabled:opacity-50"
                >
                  {isLinkingAccount ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Connecting & Syncing...</span>
                    </>
                  ) : (
                    <span>Connect & Sync</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
