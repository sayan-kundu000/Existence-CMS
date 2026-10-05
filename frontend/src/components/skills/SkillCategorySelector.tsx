import React from 'react';
import { Check, Tags, AlertCircle } from 'lucide-react';
import { SKILL_CATEGORIES } from '../../types';

interface SkillCategorySelectorProps {
  selectedCategories: string[];
  onChange: (categories: string[]) => void;
  error?: string;
  disabled?: boolean;
}

export const SkillCategorySelector: React.FC<SkillCategorySelectorProps> = ({
  selectedCategories,
  onChange,
  error,
  disabled = false,
}) => {
  // Ensure array
  const currentSelection = selectedCategories && selectedCategories.length > 0
    ? selectedCategories
    : ['Technical'];

  const toggleCategory = (cat: string) => {
    if (disabled) return;
    const exists = currentSelection.includes(cat);
    if (exists) {
      // Prevent leaving with 0 categories
      if (currentSelection.length <= 1) {
        return; // Keep at least one category selected
      }
      onChange(currentSelection.filter((c) => c !== cat));
    } else {
      onChange([...currentSelection, cat]);
    }
  };

  const handleSelectDefault = () => {
    if (disabled) return;
    onChange(['Technical']);
  };

  return (
    <div className="space-y-2.5">
      <div className="flex items-center justify-between gap-2">
        <label className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
          <Tags className="w-3.5 h-3.5 text-indigo-400" />
          <span>Skill Categories (Choose one or more)</span>
          <span className="text-[10px] text-slate-400 font-normal">
            ({currentSelection.length} selected)
          </span>
        </label>

        {currentSelection.length > 1 && (
          <button
            type="button"
            onClick={handleSelectDefault}
            disabled={disabled}
            className="text-[11px] text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer"
          >
            Reset to Technical
          </button>
        )}
      </div>

      {/* 17 Multi-Select Category Pills */}
      <div
        className="flex flex-wrap gap-1.5 p-3 rounded-2xl bg-slate-950/70 border border-slate-800/80"
        role="group"
        aria-label="Skill Categories Multi-Select"
      >
        {SKILL_CATEGORIES.map((cat) => {
          const isSelected = currentSelection.includes(cat);
          return (
            <button
              key={cat}
              type="button"
              disabled={disabled}
              onClick={() => toggleCategory(cat)}
              aria-pressed={isSelected}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-all duration-200 cursor-pointer select-none border ${
                isSelected
                  ? 'bg-indigo-600/25 border-indigo-500/80 text-indigo-200 font-semibold shadow-sm shadow-indigo-500/10'
                  : 'bg-slate-900/60 border-slate-800/70 text-slate-400 hover:border-slate-700 hover:text-slate-300 hover:bg-slate-900'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <span
                className={`w-3.5 h-3.5 rounded-md flex items-center justify-center border text-[9px] transition-colors ${
                  isSelected
                    ? 'bg-indigo-500 border-indigo-400 text-white'
                    : 'border-slate-700 bg-slate-950/50 text-transparent'
                }`}
              >
                <Check className="w-2.5 h-2.5 stroke-[3]" />
              </span>
              <span>{cat}</span>
            </button>
          );
        })}
      </div>

      {/* Selected summary */}
      <div className="flex items-center justify-between text-[11px] text-slate-400 px-1">
        <p className="truncate">
          <span className="text-slate-400 font-medium">Selected: </span>
          <span className="text-slate-300">{currentSelection.join(', ')}</span>
        </p>
      </div>

      {error && (
        <p className="flex items-center gap-1 text-[11px] text-rose-400 mt-1">
          <AlertCircle className="w-3 h-3 flex-shrink-0" />
          <span>{error}</span>
        </p>
      )}
    </div>
  );
};
