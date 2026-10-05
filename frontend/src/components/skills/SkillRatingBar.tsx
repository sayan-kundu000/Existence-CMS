import React from 'react';

export interface SkillRatingBarProps {
  rating: number; // 1 to 7
  levelLabel?: string;
  size?: 'sm' | 'md' | 'lg';
  showSegments?: boolean;
}

const LEVEL_COLORS: Record<number, { bg: string; text: string; bar: string; glow: string }> = {
  1: { bg: 'bg-slate-800/80', text: 'text-slate-300 border-slate-700', bar: 'bg-slate-400', glow: '' },
  2: { bg: 'bg-zinc-800/80', text: 'text-zinc-200 border-zinc-700', bar: 'bg-zinc-400', glow: '' },
  3: { bg: 'bg-blue-950/60', text: 'text-blue-300 border-blue-800/60', bar: 'bg-blue-500', glow: 'shadow-[0_0_12px_rgba(59,130,246,0.4)]' },
  4: { bg: 'bg-cyan-950/60', text: 'text-cyan-300 border-cyan-800/60', bar: 'bg-cyan-400', glow: 'shadow-[0_0_12px_rgba(34,211,238,0.4)]' },
  5: { bg: 'bg-indigo-950/60', text: 'text-indigo-300 border-indigo-800/60', bar: 'bg-indigo-500', glow: 'shadow-[0_0_12px_rgba(99,102,241,0.5)]' },
  6: { bg: 'bg-purple-950/60', text: 'text-purple-300 border-purple-800/60', bar: 'bg-purple-400', glow: 'shadow-[0_0_15px_rgba(192,132,252,0.5)]' },
  7: { bg: 'bg-amber-950/60', text: 'text-amber-300 border-amber-800/60', bar: 'bg-gradient-to-r from-amber-400 to-yellow-300', glow: 'shadow-[0_0_18px_rgba(251,191,36,0.6)]' },
};

export const LEVEL_NAMES: Record<number, string> = {
  1: 'Beginner',
  2: 'Novice',
  3: 'Intermediate',
  4: 'Proficient',
  5: 'Advanced',
  6: 'Expert',
  7: 'Master',
};

export const SkillRatingBar: React.FC<SkillRatingBarProps> = ({
  rating,
  levelLabel,
  size = 'md',
  showSegments = true
}) => {
  const normalizedRating = Math.max(1, Math.min(7, rating));
  const colors = LEVEL_COLORS[normalizedRating] || LEVEL_COLORS[1];
  const label = levelLabel || LEVEL_NAMES[normalizedRating];

  const heightClass = size === 'sm' ? 'h-1.5' : size === 'lg' ? 'h-3' : 'h-2';

  return (
    <div
      className="w-full"
      role="progressbar"
      aria-label={`Skill level ${label}`}
      aria-valuenow={normalizedRating}
      aria-valuemin={1}
      aria-valuemax={7}
      aria-valuetext={`Level ${normalizedRating} of 7: ${label}`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-wide uppercase border ${colors.bg} ${colors.text}`}>
          Level {normalizedRating} · {label}
        </span>
        <span className="text-[11px] font-mono text-slate-400" aria-hidden="true">
          {normalizedRating} / 7
        </span>
      </div>

      {showSegments ? (
        <div className="grid grid-cols-7 gap-1.5 w-full" aria-hidden="true">
          {[1, 2, 3, 4, 5, 6, 7].map((step) => {
            const isFilled = step <= normalizedRating;
            const isCurrent = step === normalizedRating;
            return (
              <div
                key={step}
                className={`${heightClass} rounded-full transition-all duration-300 ${
                  isFilled
                    ? `${colors.bar} ${isCurrent ? colors.glow : 'opacity-85'}`
                    : 'bg-slate-800/70'
                }`}
                title={`Level ${step}: ${LEVEL_NAMES[step]}`}
              />
            );
          })}
        </div>
      ) : (
        <div className={`w-full ${heightClass} bg-slate-800/80 rounded-full overflow-hidden`} aria-hidden="true">
          <div
            className={`h-full transition-all duration-500 rounded-full ${colors.bar} ${colors.glow}`}
            style={{ width: `${(normalizedRating / 7) * 100}%` }}
          />
        </div>
      )}
    </div>
  );
};
