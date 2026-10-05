import React from 'react';
import { Edit2, Trash2, Eye, EyeOff, ArrowUp, ArrowDown } from 'lucide-react';
import { Skill } from '../../types';
import { SkillRatingBar } from './SkillRatingBar';

export interface SkillCardProps {
  skill: Skill;
  isAdmin?: boolean;
  onEdit?: (skill: Skill) => void;
  onDelete?: (skillId: number) => void;
  onToggleVisibility?: (skill: Skill) => void;
  onMoveUp?: () => void;
  onMoveDown?: () => void;
  canMoveUp?: boolean;
  canMoveDown?: boolean;
}

export const SkillCard: React.FC<SkillCardProps> = ({
  skill,
  isAdmin = false,
  onEdit,
  onDelete,
  onToggleVisibility,
  onMoveUp,
  onMoveDown,
  canMoveUp = false,
  canMoveDown = false,
}) => {
  const isVisible = skill.visibility ?? skill.is_visible ?? true;
  const displayOrder = skill.ordering ?? skill.display_order ?? 0;

  const domainList = skill.domains && skill.domains.length > 0
    ? skill.domains
    : (skill.domain || skill.metadata_info?.domain
        ? String(skill.domain || skill.metadata_info?.domain).split(',').map((d) => d.trim()).filter(Boolean)
        : []);

  return (
    <div
      className={`glass-panel p-5 sm:p-6 rounded-3xl border transition-all duration-300 flex flex-col justify-between shadow-lg relative group ${
        !isVisible && isAdmin
          ? 'border-amber-950/60 bg-slate-950/40 opacity-75'
          : 'border-amber-500/20 hover:border-amber-500/50 hover:shadow-amber-500/10'
      }`}
    >
      <div>
        {/* Header & Badges */}
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5 flex-wrap mb-1">
              {domainList.map((dom, dIdx) => (
                <span
                  key={dIdx}
                  className="px-2 py-0.5 rounded-md bg-amber-950/80 border border-amber-500/40 text-[10px] font-bold text-amber-300 tracking-wide flex items-center gap-1 shadow-sm"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                  {dom}
                </span>
              ))}
              {(skill.categories && skill.categories.length > 0
                ? skill.categories
                : (skill.category ? skill.category.split(',').map((c) => c.trim()).filter(Boolean) : ['Technical'])
              ).map((cat, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded-md bg-slate-900/90 border border-slate-800 text-[10px] font-semibold text-amber-200/80 tracking-wide"
                >
                  {cat}
                </span>
              ))}
              {isAdmin && (
                <>
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold border ${
                      isVisible
                        ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                        : 'bg-amber-500/10 border-amber-500/20 text-amber-400'
                    }`}
                  >
                    {isVisible ? (
                      <>
                        <Eye className="w-3 h-3" /> Public
                      </>
                    ) : (
                      <>
                        <EyeOff className="w-3 h-3" /> Hidden
                      </>
                    )}
                  </span>
                  <span className="px-2 py-0.5 rounded-md bg-slate-900/90 border border-slate-800 font-mono text-[10px] text-slate-400">
                    #{displayOrder}
                  </span>
                </>
              )}
            </div>
            <h3 className="text-base sm:text-lg font-bold text-white tracking-tight break-words">
              {skill.name}
            </h3>
          </div>

          {/* Admin Management Actions */}
          {isAdmin && (
            <div className="flex items-center gap-1 shrink-0 bg-slate-950/80 p-1 rounded-xl border border-slate-800">
              {onMoveUp && (
                <button
                  type="button"
                  onClick={onMoveUp}
                  disabled={!canMoveUp}
                  className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                    canMoveUp ? 'text-slate-400 hover:text-white hover:bg-slate-800' : 'text-slate-700 cursor-not-allowed'
                  }`}
                  title="Move Up"
                  aria-label="Move skill up"
                >
                  <ArrowUp className="w-3.5 h-3.5" />
                </button>
              )}
              {onMoveDown && (
                <button
                  type="button"
                  onClick={onMoveDown}
                  disabled={!canMoveDown}
                  className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                    canMoveDown ? 'text-slate-400 hover:text-white hover:bg-slate-800' : 'text-slate-700 cursor-not-allowed'
                  }`}
                  title="Move Down"
                  aria-label="Move skill down"
                >
                  <ArrowDown className="w-3.5 h-3.5" />
                </button>
              )}
              {onToggleVisibility && (
                <button
                  type="button"
                  onClick={() => onToggleVisibility(skill)}
                  className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                    isVisible ? 'text-emerald-400 hover:bg-slate-800' : 'text-slate-500 hover:bg-slate-800'
                  }`}
                  title={isVisible ? 'Hide from public view' : 'Show in public view'}
                  aria-label={isVisible ? 'Hide skill' : 'Show skill'}
                >
                  {isVisible ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                </button>
              )}
              {onEdit && (
                <button
                  type="button"
                  onClick={() => onEdit(skill)}
                  className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
                  title="Edit Skill"
                  aria-label="Edit skill"
                >
                  <Edit2 className="w-3.5 h-3.5" />
                </button>
              )}
              {onDelete && (
                <button
                  type="button"
                  onClick={() => onDelete(skill.id)}
                  className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
                  title="Delete Skill"
                  aria-label="Delete skill"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          )}
        </div>

        {/* Optional Description */}
        {skill.description && (
          <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
            {skill.description}
          </p>
        )}
      </div>

      {/* 7-Level Calibrated Rating Bar */}
      <div className="mt-4 pt-3 border-t border-slate-800/80">
        <SkillRatingBar
          rating={skill.rating}
          levelLabel={skill.level_label}
          showSegments={true}
        />
      </div>
    </div>
  );
};
