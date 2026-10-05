import React, { useState } from 'react';
import { Plus, Trash2, ArrowUp, ArrowDown, Star, Globe, AlertCircle } from 'lucide-react';
import { ProjectLinkType } from '../../types';

export const LINK_TYPES: ProjectLinkType[] = [
  'Live Demo',
  'Deployment',
  'GitHub',
  'Repository',
  'Documentation',
  'API',
  'Video Demo',
  'Case Study',
  'Other'
];

export interface EditableLink {
  id?: number;
  label: string;
  url: string;
  link_type: ProjectLinkType;
  is_primary: boolean;
  is_visible: boolean;
  display_order: number;
}

interface ProjectLinkEditorProps {
  links: EditableLink[];
  onChange: (links: EditableLink[]) => void;
}

export const ProjectLinkEditor: React.FC<ProjectLinkEditorProps> = ({ links, onChange }) => {
  const [newLabel, setNewLabel] = useState('Live Demo');
  const [newUrl, setNewUrl] = useState('');
  const [newType, setNewType] = useState<ProjectLinkType>('Live Demo');
  const [newIsPrimary, setNewIsPrimary] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateUrl = (url: string): string | null => {
    const trimmed = url.trim();
    if (!trimmed) return 'URL cannot be empty.';
    const lowered = trimmed.toLowerCase();
    if (lowered.startsWith('javascript:') || lowered.startsWith('data:')) {
      return 'Unsafe URL scheme detected.';
    }
    if (!lowered.startsWith('http://') && !lowered.startsWith('https://')) {
      return 'URL must start with http:// or https://';
    }
    return null;
  };

  const handleAddLink = () => {
    setError(null);
    const labelClean = newLabel.trim();
    if (!labelClean) {
      setError('Please provide a link label.');
      return;
    }

    const urlError = validateUrl(newUrl);
    if (urlError) {
      setError(urlError);
      return;
    }

    const urlClean = newUrl.trim();
    if (links.some(l => l.url.toLowerCase() === urlClean.toLowerCase())) {
      setError('This URL has already been added to this project.');
      return;
    }

    // If marked primary, unset other links' primary flag
    const updatedExisting = newIsPrimary
      ? links.map(l => ({ ...l, is_primary: false }))
      : [...links];

    const newLinkItem: EditableLink = {
      label: labelClean,
      url: urlClean,
      link_type: newType,
      is_primary: newIsPrimary || links.length === 0, // auto-mark first link as primary
      is_visible: true,
      display_order: links.length
    };

    onChange([...updatedExisting, newLinkItem]);
    setNewUrl('');
    setNewLabel('GitHub');
    setNewType('GitHub');
    setNewIsPrimary(false);
  };

  const handleSetPrimary = (index: number) => {
    const updated = links.map((l, i) => ({
      ...l,
      is_primary: i === index
    }));
    onChange(updated);
  };

  const handleToggleVisible = (index: number) => {
    const updated = [...links];
    updated[index] = { ...updated[index], is_visible: !updated[index].is_visible };
    onChange(updated);
  };

  const handleRemove = (index: number) => {
    const wasPrimary = links[index].is_primary;
    const remaining = links.filter((_, i) => i !== index);
    // If we removed the primary link and there are remaining links, assign primary to first
    if (wasPrimary && remaining.length > 0) {
      remaining[0].is_primary = true;
    }
    onChange(remaining);
  };

  const handleMove = (index: number, direction: 'up' | 'down') => {
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= links.length) return;

    const copy = [...links];
    const temp = copy[index];
    copy[index] = copy[targetIndex];
    copy[targetIndex] = temp;

    // Normalize display_orders
    copy.forEach((l, idx) => {
      l.display_order = idx;
    });

    onChange(copy);
  };

  return (
    <div className="space-y-4">
      {/* Existing Links List */}
      {links.length > 0 ? (
        <div className="space-y-2">
          {links.map((link, idx) => (
            <div
              key={idx}
              className={`flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-3 rounded-xl border transition-all ${
                link.is_primary
                  ? 'bg-indigo-950/40 border-indigo-500/50 shadow-sm'
                  : 'bg-slate-900/80 border-slate-800'
              }`}
            >
              <div className="flex items-center gap-3 min-w-0">
                <Globe className="w-4 h-4 text-indigo-400 shrink-0" />
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white truncate">{link.label}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium">
                      {link.link_type}
                    </span>
                    {link.is_primary && (
                      <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        <Star className="w-2.5 h-2.5 fill-amber-400" /> Primary CTA
                      </span>
                    )}
                    {!link.is_visible && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-400 font-bold uppercase">
                        Hidden
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono truncate max-w-sm sm:max-w-md">
                    {link.url}
                  </div>
                </div>
              </div>

              {/* Link actions */}
              <div className="flex items-center gap-1.5 self-end sm:self-center shrink-0">
                {!link.is_primary && (
                  <button
                    type="button"
                    onClick={() => handleSetPrimary(idx)}
                    className="px-2 py-1 rounded-lg text-[10px] font-semibold text-slate-300 hover:text-amber-300 bg-slate-800 hover:bg-slate-700 transition-colors cursor-pointer"
                    title="Mark as primary deployment link"
                  >
                    Set Primary
                  </button>
                )}

                <button
                  type="button"
                  onClick={() => handleToggleVisible(idx)}
                  className={`px-2 py-1 rounded-lg text-[10px] font-semibold transition-colors cursor-pointer ${
                    link.is_visible ? 'text-slate-400 hover:text-slate-200' : 'text-amber-400'
                  }`}
                  title="Toggle link visibility"
                >
                  {link.is_visible ? 'Visible' : 'Hidden'}
                </button>

                <button
                  type="button"
                  onClick={() => handleMove(idx, 'up')}
                  disabled={idx === 0}
                  className="p-1 rounded text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
                  title="Move up"
                >
                  <ArrowUp className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => handleMove(idx, 'down')}
                  disabled={idx === links.length - 1}
                  className="p-1 rounded text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
                  title="Move down"
                >
                  <ArrowDown className="w-3.5 h-3.5" />
                </button>

                <button
                  type="button"
                  onClick={() => handleRemove(idx)}
                  className="p-1 rounded text-slate-400 hover:text-rose-400 transition-colors cursor-pointer"
                  title="Delete link"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-xs text-slate-400 italic font-light p-3 bg-slate-900/40 rounded-xl border border-dashed border-slate-800">
          No deployment links added. A project can support multiple links (e.g. Live Demo, GitHub Repository, Docs).
        </div>
      )}

      {/* Add New Link Card */}
      <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
        <div className="text-xs font-semibold text-slate-300">Add Deployment / Demo Link</div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          <div>
            <label className="block text-[10px] font-medium text-slate-400 mb-1">Label</label>
            <input
              type="text"
              value={newLabel}
              onChange={(e) => setNewLabel(e.target.value)}
              placeholder="e.g. Live Demo, GitHub..."
              className="w-full px-3 py-1.5 rounded-lg text-xs bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-[10px] font-medium text-slate-400 mb-1">Type</label>
            <select
              value={newType}
              onChange={(e) => setNewType(e.target.value as ProjectLinkType)}
              className="w-full px-3 py-1.5 rounded-lg text-xs bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
            >
              {LINK_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-medium text-slate-400 mb-1">Primary Link?</label>
            <label className="flex items-center gap-2 mt-2 cursor-pointer">
              <input
                type="checkbox"
                checked={newIsPrimary}
                onChange={(e) => setNewIsPrimary(e.target.checked)}
                className="w-3.5 h-3.5 rounded text-indigo-600 bg-slate-900 border-slate-700 focus:ring-indigo-500"
              />
              <span className="text-xs text-slate-300">Set as Primary CTA</span>
            </label>
          </div>
        </div>

        <div>
          <label className="block text-[10px] font-medium text-slate-400 mb-1">URL (must start with http:// or https://)</label>
          <div className="flex gap-2">
            <input
              type="url"
              value={newUrl}
              onChange={(e) => {
                setNewUrl(e.target.value);
                if (error) setError(null);
              }}
              placeholder="https://example.com/demo"
              className="flex-1 px-3 py-1.5 rounded-lg text-xs bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
            <button
              type="button"
              onClick={handleAddLink}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors cursor-pointer shrink-0"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Attach Link</span>
            </button>
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-1.5 text-xs text-rose-400">
            <AlertCircle className="w-3.5 h-3.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>
    </div>
  );
};
