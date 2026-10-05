import React, { useState } from 'react';
import {
  X,
  Sparkles,
  GitBranch,
  Layers,
  Star,
  ExternalLink,
  Copy,
  Check,
  Download,
  CheckSquare,
  Square,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Globe,
  Key,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';
import { ExtractedProject, ProjectCreateInput, ProjectLinkType } from '../../types';
import { api } from '../../services/api';
import {
  extractGithubClientSide,
  downloadProjectDossier,
  downloadAllDossiers,
  copyToClipboard
} from '../../utils/githubExtractor';

interface GithubExtractionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImportComplete: () => void;
  executeWithPin: (action: () => Promise<void>) => void;
  notify: (type: 'success' | 'error', text: string) => void;
}

export const GithubExtractionModal: React.FC<GithubExtractionModalProps> = ({
  isOpen,
  onClose,
  onImportComplete,
  executeWithPin,
  notify
}) => {
  const [githubUrl, setGithubUrl] = useState('');
  const [customToken, setCustomToken] = useState('');
  const [showTokenInput, setShowTokenInput] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [extractedProjects, setExtractedProjects] = useState<ExtractedProject[]>([]);
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(new Set());
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [autoLinkAccount, setAutoLinkAccount] = useState(true);

  if (!isOpen) return null;

  const handleExtract = async () => {
    const cleanUrl = githubUrl.trim();
    if (!cleanUrl) {
      notify('error', 'Please enter your GitHub profile link or username.');
      return;
    }

    setIsLoading(true);
    setLoadingStep('Connecting to GitHub API...');

    try {
      setLoadingStep('Fetching repositories & README files...');
      let response;
      try {
        // Try backend extraction first
        response = await api.extractGithubProjects(cleanUrl, customToken.trim() || undefined);
      } catch (err: any) {
        // Graceful fallback to client-side extractor
        setLoadingStep('Processing directly via GitHub client engine...');
        response = await extractGithubClientSide(cleanUrl, customToken.trim() || undefined);
      }

      setLoadingStep('Generating plain-English AI dossiers...');
      if (!response.projects || response.projects.length === 0) {
        notify('error', 'No public repositories found for this GitHub account.');
        setExtractedProjects([]);
        setSelectedIndices(new Set());
      } else {
        setExtractedProjects(response.projects);
        // By default, select all extracted projects
        const allIndices = new Set<number>(response.projects.map((_, i) => i));
        setSelectedIndices(allIndices);
        notify('success', `Successfully extracted ${response.projects.length} projects with AI dossiers!`);
      }
    } catch (err: any) {
      notify('error', err.message || 'Failed to extract projects from GitHub.');
    } finally {
      setIsLoading(false);
      setLoadingStep('');
    }
  };

  const handleToggleSelectAll = () => {
    if (selectedIndices.size === extractedProjects.length) {
      setSelectedIndices(new Set());
    } else {
      setSelectedIndices(new Set(extractedProjects.map((_, i) => i)));
    }
  };

  const handleToggleSelectOne = (index: number) => {
    const updated = new Set(selectedIndices);
    if (updated.has(index)) {
      updated.delete(index);
    } else {
      updated.add(index);
    }
    setSelectedIndices(updated);
  };

  const handleCopyDossier = async (proj: ExtractedProject, index: number) => {
    const textToCopy = proj.full_ai_dossier || proj.description || '';
    const success = await copyToClipboard(textToCopy);
    if (success) {
      setCopiedIndex(index);
      notify('success', `Copied AI dossier for '${proj.name}' to clipboard!`);
      setTimeout(() => setCopiedIndex(null), 2500);
    } else {
      notify('error', 'Failed to copy to clipboard.');
    }
  };

  const handleDownloadSingle = (proj: ExtractedProject) => {
    downloadProjectDossier(proj);
    notify('success', `Downloaded '${proj.name}' dossier as Markdown!`);
  };

  const handleDownloadAll = () => {
    if (extractedProjects.length === 0) return;
    downloadAllDossiers(extractedProjects);
    notify('success', `Downloaded bundle with all ${extractedProjects.length} project dossiers!`);
  };

  const formatProjectForImport = (p: ExtractedProject): ProjectCreateInput => {
    return {
      name: p.name,
      short_description: p.short_description || null,
      description: p.full_ai_dossier || p.description || null,
      status: p.status,
      is_featured: p.is_featured,
      is_visible: true,
      technologies: (p.technologies || []).map((t) => ({
        name: t.name,
        category: t.category || 'Other'
      })),
      links: (p.links || []).map((l, idx) => ({
        label: l.label,
        url: l.url,
        link_type: l.link_type as ProjectLinkType,
        is_primary: l.is_primary,
        is_visible: l.is_visible,
        display_order: idx
      }))
    };
  };

  const handleImportSingle = (proj: ExtractedProject) => {
    const payload = formatProjectForImport(proj);
    executeWithPin(async () => {
      await api.bulkImportProjects([payload]);
      notify('success', `Imported '${proj.name}' into your Existence CMS projects!`);
      onImportComplete();
    });
  };

  const handleImportSelected = () => {
    if (selectedIndices.size === 0) {
      notify('error', 'Please select at least one project to import.');
      return;
    }

    const toImport = extractedProjects
      .filter((_, idx) => selectedIndices.has(idx))
      .map(formatProjectForImport);

    executeWithPin(async () => {
      setIsImporting(true);
      try {
        await api.bulkImportProjects(toImport);
        if (autoLinkAccount && githubUrl.trim()) {
          try {
            await api.saveGithubLink({
              github_url: githubUrl.trim(),
              custom_token: customToken.trim() || undefined,
              auto_sync: true
            });
          } catch {
            // graceful non-blocking fallback if link fails
          }
        }
        notify('success', `Successfully imported ${toImport.length} project(s) into your portfolio!`);
        onImportComplete();
        onClose();
      } finally {
        setIsImporting(false);
      }
    });
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-slate-950/85 backdrop-blur-md animate-fadeIn"
      role="dialog"
      aria-modal="true"
    >
      <div className="relative w-full max-w-4xl max-h-[92vh] flex flex-col glass-panel rounded-3xl border border-indigo-500/30 bg-slate-900/95 shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-5 sm:p-6 border-b border-slate-800 bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
              <GitBranch className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base sm:text-lg font-bold text-white">GitHub Project Extraction & AI Dossier Engine</h3>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                  <Sparkles className="w-3 h-3 text-emerald-400" />
                  AI Powered
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Link with GitHub to extract repositories, tech stacks, live links, and generate plain-English project breakdowns.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-6">
          {/* Input Panel */}
          <div className="p-4 sm:p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-200 mb-1.5 flex items-center gap-1.5">
                <GitBranch className="w-4 h-4 text-indigo-400" />
                <span>GitHub Profile or Repository URL</span>
                <span className="text-rose-400">*</span>
              </label>
              <div className="flex flex-col sm:flex-row gap-2.5">
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={githubUrl}
                    onChange={(e) => setGithubUrl(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !isLoading) handleExtract();
                    }}
                    placeholder="e.g. https://github.com/username or https://github.com/owner/repository"
                    className="w-full pl-3.5 pr-4 py-2.5 rounded-xl text-xs sm:text-sm bg-slate-900 border border-slate-700/80 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
                  />
                </div>
                <button
                  type="button"
                  onClick={handleExtract}
                  disabled={isLoading}
                  className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 transition-all shadow-md shadow-indigo-600/25 cursor-pointer shrink-0"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin text-white" />
                      <span>Extracting...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 text-amber-300" />
                      <span>Extract Projects</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Optional Personal Access Token accordion */}
            <div className="pt-2 border-t border-slate-800/60">
              <button
                type="button"
                onClick={() => setShowTokenInput(!showTokenInput)}
                className="inline-flex items-center gap-1.5 text-[11px] text-slate-400 hover:text-indigo-300 transition-colors cursor-pointer"
              >
                <Key className="w-3.5 h-3.5" />
                <span>{showTokenInput ? 'Hide' : 'Add'} optional GitHub Personal Access Token (for higher API rate limit)</span>
                {showTokenInput ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>

              {showTokenInput && (
                <div className="mt-2.5 p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                  <input
                    type="password"
                    value={customToken}
                    onChange={(e) => setCustomToken(e.target.value)}
                    placeholder="ghp_xxxxxxxxxxxxxxxxxxxx (Optional PAT with public_repo read)"
                    className="w-full px-3 py-1.5 rounded-lg text-xs bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
                  />
                  <p className="text-[10px] text-slate-400">
                    GitHub allows 60 anonymous requests per hour. Providing a token increases your limit to 5,000 requests/hr.
                  </p>
                </div>
              )}
            </div>

            {/* Loading Indicator */}
            {isLoading && (
              <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center gap-3 animate-pulse">
                <RefreshCw className="w-5 h-5 text-indigo-400 animate-spin shrink-0" />
                <div className="text-xs text-indigo-200">
                  <div className="font-semibold">{loadingStep || 'Processing GitHub extraction...'}</div>
                  <div className="text-[10px] text-indigo-300/80 mt-0.5">
                    Analyzing README files, categorizing tech stacks, detecting deployment links, and writing simple AI dossiers...
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Results Showcase */}
          {extractedProjects.length > 0 && (
            <div className="space-y-4">
              {/* Batch Actions Bar */}
              <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800">
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={handleToggleSelectAll}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-300 hover:text-white cursor-pointer"
                  >
                    {selectedIndices.size === extractedProjects.length ? (
                      <CheckSquare className="w-4 h-4 text-indigo-400" />
                    ) : (
                      <Square className="w-4 h-4 text-slate-500" />
                    )}
                    <span>
                      {selectedIndices.size === extractedProjects.length
                        ? 'Deselect All'
                        : `Select All (${extractedProjects.length})`}
                    </span>
                  </button>

                  <span className="text-xs text-slate-400 font-medium">
                    • {selectedIndices.size} selected for import
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleDownloadAll}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors cursor-pointer"
                    title="Download all generated AI dossiers in one Markdown file"
                  >
                    <Download className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Download All Dossiers (.md)</span>
                  </button>

                  <button
                    type="button"
                    onClick={handleImportSelected}
                    disabled={selectedIndices.size === 0 || isImporting}
                    className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 transition-all shadow-md cursor-pointer"
                  >
                    <ShieldCheck className="w-4 h-4 text-white" />
                    <span>Import Selected ({selectedIndices.size})</span>
                  </button>
                </div>
              </div>

              {/* Projects List */}
              <div className="space-y-4">
                {extractedProjects.map((project, idx) => {
                  const isSelected = selectedIndices.has(idx);
                  const isExpanded = expandedIndex === idx;
                  const isCopied = copiedIndex === idx;

                  const githubLink = project.links.find((l) => l.link_type === 'GitHub');
                  const optionalLinks = project.links.filter((l) => l.link_type !== 'GitHub');

                  return (
                    <div
                      key={`extracted-${idx}`}
                      className={`rounded-2xl border transition-all ${
                        isSelected
                          ? 'border-indigo-500/40 bg-slate-900/90 shadow-lg'
                          : 'border-slate-800 bg-slate-950/40 hover:border-slate-700'
                      }`}
                    >
                      {/* Project Header Bar */}
                      <div className="p-4 sm:p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                        <div className="flex items-start gap-3 min-w-0">
                          <button
                            type="button"
                            onClick={() => handleToggleSelectOne(idx)}
                            className="mt-1 text-slate-400 hover:text-white cursor-pointer shrink-0"
                          >
                            {isSelected ? (
                              <CheckSquare className="w-5 h-5 text-indigo-400" />
                            ) : (
                              <Square className="w-5 h-5 text-slate-600" />
                            )}
                          </button>

                          <div className="min-w-0">
                            <div className="flex flex-wrap items-center gap-2">
                              <h4 className="text-base font-bold text-white truncate">{project.name}</h4>
                              {project.stars > 0 && (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/20">
                                  <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                                  {project.stars}
                                </span>
                              )}
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                                {project.status}
                              </span>
                            </div>

                            {/* Short Description */}
                            <p className="text-xs text-slate-300 mt-1 line-clamp-2 font-light">
                              {project.short_description}
                            </p>
                          </div>
                        </div>

                        {/* Top quick actions */}
                        <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                          <button
                            type="button"
                            onClick={() => handleCopyDossier(project, idx)}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[11px] font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors cursor-pointer"
                            title="Copy full AI generated description & dossier"
                          >
                            {isCopied ? (
                              <>
                                <Check className="w-3.5 h-3.5 text-emerald-400" />
                                <span className="text-emerald-400">Copied</span>
                              </>
                            ) : (
                              <>
                                <Copy className="w-3.5 h-3.5 text-slate-400" />
                                <span>Copy AI Dossier</span>
                              </>
                            )}
                          </button>

                          <button
                            type="button"
                            onClick={() => handleDownloadSingle(project)}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[11px] font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors cursor-pointer"
                            title="Download project dossier as Markdown (.md)"
                          >
                            <Download className="w-3.5 h-3.5 text-slate-400" />
                            <span>Download (.md)</span>
                          </button>

                          <button
                            type="button"
                            onClick={() => handleImportSingle(project)}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-[11px] font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors cursor-pointer"
                          >
                            <span>Import</span>
                          </button>
                        </div>
                      </div>

                      {/* Tech stack & Links tags */}
                      <div className="px-4 sm:px-5 pb-3 pt-1 border-t border-slate-800/60 flex flex-wrap items-center justify-between gap-3 text-xs">
                        {/* Technologies */}
                        <div className="flex flex-wrap items-center gap-1.5">
                          <Layers className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                          {project.technologies.slice(0, 6).map((tech, tIdx) => (
                            <span
                              key={tIdx}
                              className="px-2 py-0.5 rounded-md text-[10px] font-medium bg-slate-800/90 text-slate-300 border border-slate-700/60"
                            >
                              {tech.name}
                            </span>
                          ))}
                          {project.technologies.length > 6 && (
                            <span className="text-[10px] text-slate-500">
                              +{project.technologies.length - 6} more
                            </span>
                          )}
                        </div>

                        {/* Links indicator: Mandatory GitHub + Optional Deployments */}
                        <div className="flex flex-wrap items-center gap-2">
                          {githubLink && (
                            <a
                              href={githubLink.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 hover:underline"
                            >
                              <GitBranch className="w-3 h-3 text-indigo-400" />
                              <span>GitHub (Mandatory)</span>
                              <ExternalLink className="w-2.5 h-2.5" />
                            </a>
                          )}

                          {optionalLinks.map((optLink, oIdx) => (
                            <a
                              key={oIdx}
                              href={optLink.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 hover:underline"
                            >
                              <Globe className="w-3 h-3 text-emerald-400" />
                              <span>{optLink.label} (Optional)</span>
                              <ExternalLink className="w-2.5 h-2.5" />
                            </a>
                          ))}
                        </div>
                      </div>

                      {/* Expandable AI Dossier Accordion */}
                      <div className="border-t border-slate-800/80 bg-slate-950/40">
                        <button
                          type="button"
                          onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                          className="w-full px-4 sm:px-5 py-2.5 flex items-center justify-between text-xs font-semibold text-slate-400 hover:text-indigo-300 transition-colors cursor-pointer"
                        >
                          <span className="flex items-center gap-1.5">
                            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                            {isExpanded ? 'Hide AI Project Dossier' : 'Preview Full AI Dossier (Purpose, Tech Stack, Architecture & Roadmap)'}
                          </span>
                          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>

                        {isExpanded && (
                          <div className="p-4 sm:p-5 border-t border-slate-800/60 space-y-4 text-xs text-slate-300 font-light leading-relaxed animate-fadeIn">
                            <div className="bg-slate-900/90 rounded-xl p-4 border border-slate-800 font-mono text-[11px] whitespace-pre-wrap max-h-80 overflow-y-auto">
                              {project.full_ai_dossier || project.description}
                            </div>
                            <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                              <span>Formatted in simple words with Tech Stack, Purpose, Architecture & Future Roadmap.</span>
                              <div className="flex items-center gap-2">
                                <button
                                  type="button"
                                  onClick={() => handleCopyDossier(project, idx)}
                                  className="text-indigo-400 hover:underline cursor-pointer"
                                >
                                  Copy Text
                                </button>
                                <span>•</span>
                                <button
                                  type="button"
                                  onClick={() => handleDownloadSingle(project)}
                                  className="text-indigo-400 hover:underline cursor-pointer"
                                >
                                  Download File
                                </button>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 sm:p-5 border-t border-slate-800 bg-slate-950/60">
          <div className="text-xs text-slate-400">
            {extractedProjects.length > 0 ? (
              <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300 hover:text-white select-none">
                <input
                  type="checkbox"
                  checked={autoLinkAccount}
                  onChange={(e) => setAutoLinkAccount(e.target.checked)}
                  className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 bg-slate-900 border-slate-700"
                />
                <span>🔗 Link this GitHub account to auto-sync future projects & code changes</span>
              </label>
            ) : (
              <span>Enter a GitHub URL or username to begin automated extraction.</span>
            )}
          </div>

          <div className="flex items-center gap-2.5">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-white transition-colors cursor-pointer"
            >
              Close
            </button>
            {extractedProjects.length > 0 && (
              <button
                type="button"
                onClick={handleImportSelected}
                disabled={selectedIndices.size === 0 || isImporting}
                className="inline-flex items-center gap-1.5 px-5 py-2 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 transition-all shadow-md cursor-pointer"
              >
                <Check className="w-4 h-4 text-white" />
                <span>Import Selected Projects ({selectedIndices.size})</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
