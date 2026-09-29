import React, { useState } from 'react';
import { Sparkles, Search, Filter, Layers, ArrowRight } from 'lucide-react';
import { Skill, PublicTabType } from '../../types';
import { SkillRatingBar, LEVEL_NAMES } from './SkillRatingBar';
import { EmptyState } from '../common/EmptyState';

interface SkillsViewProps {
  skills: Skill[];
  onNavigateToCms?: () => void;
  onNavigate?: (tab: PublicTabType) => void;
}

export const SkillsView: React.FC<SkillsViewProps> = ({ skills, onNavigateToCms, onNavigate }) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedLevel, setSelectedLevel] = useState<number | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  if (skills.length === 0) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6">
        <EmptyState
          icon={Sparkles}
          title="No skills have been added yet"
          description="The 7-level mastery ratings and skills repository have not been populated yet."
          actionText={onNavigate ? "Back to Home" : "Add Skill via CMS"}
          onAction={() => {
            if (onNavigate) onNavigate('home');
            else if (onNavigateToCms) onNavigateToCms();
          }}
        />
      </div>
    );
  }

  // Categories extraction
  const categories = ['all', ...Array.from(new Set(skills.map((s) => s.category).filter(Boolean)))];

  // Rating level counts
  const levelCounts: Record<number, number> = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0 };
  skills.forEach((s) => {
    if (s.rating >= 1 && s.rating <= 7) {
      levelCounts[s.rating] = (levelCounts[s.rating] || 0) + 1;
    }
  });

  const filteredSkills = skills.filter((skill) => {
    const matchesCat = selectedCategory === 'all' || skill.category === selectedCategory;
    const matchesLevel = selectedLevel === 'all' || skill.rating === selectedLevel;
    const matchesQuery =
      skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (skill.category && skill.category.toLowerCase().includes(searchQuery.toLowerCase())) ||
      skill.level_label.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesLevel && matchesQuery;
  });

  return (
    <div className="max-w-6xl mx-auto py-8 sm:py-16 px-4 sm:px-6 space-y-10 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-amber-400 uppercase tracking-wider">
            <Sparkles className="w-4 h-4" />
            <span>7-Level Competency Benchmark</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Skills & Mastery Framework
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
            Calibrated technical competencies ranked strictly from Level 1 (Beginner) to Level 7 (Master) with category segregation.
          </p>
        </div>

        {/* Search */}
        <div className="relative min-w-[260px]">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search skills, category, level..."
            className="w-full pl-9 pr-4 py-2.5 bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-2xl text-xs text-white placeholder-slate-500 outline-none transition-all shadow-inner"
          />
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
        </div>
      </div>

      {/* 7-Level Benchmark Cards & Distribution */}
      <div className="glass-panel p-5 sm:p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="flex items-center justify-between text-xs text-slate-400 pb-2 border-b border-slate-800/80">
          <span className="font-semibold uppercase tracking-wider text-[11px]">7-Level Mastery Scale</span>
          <span className="font-mono text-indigo-400">{skills.length} Total Competencies</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
          {[1, 2, 3, 4, 5, 6, 7].map((lvl) => {
            const count = levelCounts[lvl] || 0;
            const isSelected = selectedLevel === lvl;
            return (
              <button
                key={lvl}
                onClick={() => setSelectedLevel(isSelected ? 'all' : lvl)}
                className={`p-2.5 rounded-2xl text-center border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-indigo-600 border-indigo-500 text-white shadow-md shadow-indigo-600/30'
                    : 'bg-slate-900/70 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between text-[10px] font-mono text-indigo-300 font-bold mb-1">
                  <span>L{lvl}</span>
                  <span className="px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300">{count}</span>
                </div>
                <div className="text-xs font-semibold truncate">{LEVEL_NAMES[lvl]}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Category Filter Pills */}
      {categories.length > 2 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          <span className="text-xs text-slate-500 flex items-center gap-1 font-medium mr-1 shrink-0">
            <Filter className="w-3.5 h-3.5" /> Category:
          </span>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-medium capitalize transition-all cursor-pointer shrink-0 ${
                selectedCategory === cat
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {/* Skills Grid */}
      {filteredSkills.length === 0 ? (
        <div className="glass-panel p-12 text-center text-slate-400 text-xs rounded-3xl border border-slate-800">
          No skills match your active filter criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {filteredSkills.map((skill) => (
            <div
              key={skill.id}
              className="glass-panel p-6 rounded-3xl border border-slate-800 hover:border-indigo-500/30 transition-all flex flex-col justify-between shadow-lg"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h3 className="text-base font-bold text-white tracking-tight">
                    {skill.name}
                  </h3>
                  <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[10px] font-semibold text-slate-400">
                    {skill.category}
                  </span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80">
                <SkillRatingBar rating={skill.rating} levelLabel={skill.level_label} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
