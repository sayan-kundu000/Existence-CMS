import React, { useRef } from 'react';
import { LEVEL_NAMES } from './SkillRatingBar';

export interface SkillRatingSelectorProps {
  value: number; // 1 to 7
  onChange: (rating: number) => void;
  disabled?: boolean;
  error?: string;
  label?: string;
  helperText?: string;
}

const LEVEL_DESCRIPTIONS: Record<number, string> = {
  1: 'Beginner: Fundamental conceptual understanding & guided execution',
  2: 'Novice: Basic practical application following established patterns',
  3: 'Intermediate: Competent independent execution of standard workflows',
  4: 'Proficient: Fluent problem-solving, quality optimization & autonomy',
  5: 'Advanced: Deep architectural mastery & complex implementations',
  6: 'Expert: Authoritative domain mastery & technical leadership',
  7: 'Master: World-class synthesis, visionary standard definition',
};

export const SkillRatingSelector: React.FC<SkillRatingSelectorProps> = ({
  value,
  onChange,
  disabled = false,
  error,
  label = 'Calibrated Mastery Level (1–7)',
  helperText
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const normalizedValue = Math.max(1, Math.min(7, value || 4));

  const handleKeyDown = (e: React.KeyboardEvent, currentLvl: number) => {
    if (disabled) return;

    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      e.preventDefault();
      const next = Math.min(7, currentLvl + 1);
      onChange(next);
      focusLevel(next);
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      e.preventDefault();
      const prev = Math.max(1, currentLvl - 1);
      onChange(prev);
      focusLevel(prev);
    } else if (e.key === 'Home') {
      e.preventDefault();
      onChange(1);
      focusLevel(1);
    } else if (e.key === 'End') {
      e.preventDefault();
      onChange(7);
      focusLevel(7);
    }
  };

  const focusLevel = (lvl: number) => {
    const el = containerRef.current?.querySelector<HTMLButtonElement>(`[data-level="${lvl}"]`);
    el?.focus();
  };

  return (
    <div className="space-y-2 w-full">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold text-slate-300 tracking-wide">
          {label}
        </label>
        <span className="text-xs font-bold font-mono text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-0.5 rounded-full">
          Level {normalizedValue} — {LEVEL_NAMES[normalizedValue]}
        </span>
      </div>

      {/* 7-Level Radio Group */}
      <div
        ref={containerRef}
        role="radiogroup"
        aria-label={label}
        aria-disabled={disabled}
        aria-invalid={!!error}
        className={`grid grid-cols-7 gap-1.5 sm:gap-2 p-1.5 rounded-2xl bg-slate-950/80 border ${
          error ? 'border-rose-500/50' : 'border-slate-800'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        {[1, 2, 3, 4, 5, 6, 7].map((lvl) => {
          const isSelected = normalizedValue === lvl;
          return (
            <button
              key={lvl}
              type="button"
              data-level={lvl}
              role="radio"
              aria-checked={isSelected}
              aria-label={`Level ${lvl}: ${LEVEL_NAMES[lvl]}`}
              tabIndex={isSelected ? 0 : -1}
              disabled={disabled}
              onClick={() => !disabled && onChange(lvl)}
              onKeyDown={(e) => handleKeyDown(e, lvl)}
              className={`py-2 px-1 rounded-xl text-center transition-all cursor-pointer select-none outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 ${
                isSelected
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/40 ring-1 ring-indigo-400/50 scale-[1.02]'
                  : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 border border-transparent'
              }`}
            >
              <div className="text-sm font-extrabold font-mono leading-none">{lvl}</div>
              <div className="text-[9px] font-medium tracking-tight mt-1 truncate hidden sm:block">
                {LEVEL_NAMES[lvl]}
              </div>
            </button>
          );
        })}
      </div>

      {/* Contextual Description */}
      <p className="text-[11px] text-slate-400 italic">
        {LEVEL_DESCRIPTIONS[normalizedValue]}
      </p>

      {/* Helper / Error Text */}
      {error ? (
        <p className="text-xs text-rose-400 flex items-center gap-1 font-medium">
          {error}
        </p>
      ) : helperText ? (
        <p className="text-[11px] text-slate-500">{helperText}</p>
      ) : null}
    </div>
  );
};
