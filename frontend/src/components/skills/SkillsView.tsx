import React, { useState, useMemo } from 'react';
import { Sparkles, Search, Filter, Layers, Cpu, ChevronDown, ChevronUp, LayoutGrid, List } from 'lucide-react';
import { Skill, PublicTabType } from '../../types';
import { LEVEL_NAMES } from './SkillRatingBar';
import { SkillCard } from './SkillCard';
import { EmptyState } from '../common/EmptyState';

interface SkillsViewProps {
  skills: Skill[];
  onNavigateToCms?: () => void;
  onNavigate?: (tab: PublicTabType) => void;
}

export const SkillsView: React.FC<SkillsViewProps> = ({ skills, onNavigateToCms, onNavigate }) => {
  const [selectedDomain, setSelectedDomain] = useState<string>('all');
  const [domainSearch, setDomainSearch] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedLevel, setSelectedLevel] = useState<number | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [expandedAccordions, setExpandedAccordions] = useState<Record<string, boolean>>({});
  const [viewStyle, setViewStyle] = useState<'list-to-grid' | 'accordion'>('list-to-grid');

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

  // Extract all unique domains (supporting skills with multiple domains)
  const { domains, domainCounts, skillsByDomain } = useMemo(() => {
    const counts: Record<string, number> = { all: skills.length };
    const byDom: Record<string, Skill[]> = {};
    const uniqueDomsSet = new Set<string>();

    skills.forEach((s) => {
      const skillDoms = s.domains && s.domains.length > 0
        ? s.domains
        : (s.domain || s.metadata_info?.domain
            ? String(s.domain || s.metadata_info?.domain).split(',').map((d) => d.trim()).filter(Boolean)
            : []);

      if (skillDoms.length === 0) {
        counts['General'] = (counts['General'] || 0) + 1;
        if (!byDom['General']) byDom['General'] = [];
        byDom['General'].push(s);
      } else {
        skillDoms.forEach((dom) => {
          uniqueDomsSet.add(dom);
          counts[dom] = (counts[dom] || 0) + 1;
          if (!byDom[dom]) byDom[dom] = [];
          byDom[dom].push(s);
        });
      }
    });

    const domList = Array.from(uniqueDomsSet).sort((a, b) => a.localeCompare(b));
    const hasUnassigned = skills.some((s) => {
      const d = s.domains && s.domains.length > 0
        ? s.domains
        : (s.domain ? s.domain.split(',').map((x) => x.trim()).filter(Boolean) : []);
      return d.length === 0;
    });
    if (hasUnassigned && !domList.includes('General')) {
      domList.push('General');
    }

    return {
      domains: ['all', ...domList],
      domainCounts: counts,
      skillsByDomain: byDom
    };
  }, [skills]);

  // Multi-category extraction across all skills
  const allExtractedCategories = useMemo(() => {
    return skills.flatMap((s) =>
      s.categories && s.categories.length > 0
        ? s.categories
        : (s.category ? s.category.split(',').map((c) => c.trim()).filter(Boolean) : ['Technical'])
    );
  }, [skills]);
  const categories = ['all', ...Array.from(new Set(allExtractedCategories))];

  // Rating level counts across all 7 levels
  const levelCounts: Record<number, number> = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0 };
  skills.forEach((s) => {
    if (s.rating >= 1 && s.rating <= 7) {
      levelCounts[s.rating] = (levelCounts[s.rating] || 0) + 1;
    }
  });

  // Filter skills based on Domain, Category, Level, and Search Query
  const filterAndSortSkills = (skillList: Skill[]) => {
    return skillList
      .filter((skill) => {
        const skillDoms = skill.domains && skill.domains.length > 0
          ? skill.domains
          : (skill.domain || skill.metadata_info?.domain
              ? String(skill.domain || skill.metadata_info?.domain).split(',').map((d) => d.trim()).filter(Boolean)
              : ['General']);

        const matchesDomain =
          selectedDomain === 'all' ||
          skillDoms.some((d) => d.toLowerCase() === selectedDomain.toLowerCase());

        const skillCats = skill.categories && skill.categories.length > 0
          ? skill.categories
          : (skill.category ? skill.category.split(',').map((c) => c.trim()).filter(Boolean) : ['Technical']);

        const matchesCat = selectedCategory === 'all' || skillCats.includes(selectedCategory);
        const matchesLevel = selectedLevel === 'all' || skill.rating === selectedLevel;
        const matchesQuery =
          skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          skillDoms.some((d) => d.toLowerCase().includes(searchQuery.toLowerCase())) ||
          skillCats.some((c) => c.toLowerCase().includes(searchQuery.toLowerCase())) ||
          (skill.description && skill.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
          skill.level_label.toLowerCase().includes(searchQuery.toLowerCase());

        return matchesDomain && matchesCat && matchesLevel && matchesQuery;
      })
      .sort((a, b) => {
        // 1. Mastery Rating descending (Level 7 down to Level 1)
        if (b.rating !== a.rating) {
          return b.rating - a.rating;
        }
        // 2. Display order ascending
        const orderA = a.ordering ?? a.display_order ?? 0;
        const orderB = b.ordering ?? b.display_order ?? 0;
        if (orderA !== orderB) {
          return orderA - orderB;
        }
        // 3. Name alphabetically
        return a.name.localeCompare(b.name);
      });
  };

  const filteredSkills = filterAndSortSkills(skills);

  const toggleAccordion = (dom: string) => {
    setExpandedAccordions((prev) => ({
      ...prev,
      [dom]: !prev[dom]
    }));
  };

  return (
    <div className="max-w-6xl mx-auto py-8 sm:py-16 px-4 sm:px-6 space-y-10 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-amber-400 uppercase tracking-wider">
            <Sparkles className="w-4 h-4" />
            <span>7-Level Competency Benchmark & Domain Segregation</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Skills & Mastery Framework
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
            Calibrated technical competencies categorized by domain, ranked strictly from Level 7 (Master) down to Level 1 (Beginner).
          </p>
        </div>

        {/* Search */}
        <div className="relative min-w-[260px]">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search skills, domain, category..."
            aria-label="Search skills"
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
          {[7, 6, 5, 4, 3, 2, 1].map((lvl) => {
            const count = levelCounts[lvl] || 0;
            const isSelected = selectedLevel === lvl;
            return (
              <button
                key={lvl}
                type="button"
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

      {/* DOMAIN SELECTION LIST SECTION */}
      {domains.length > 1 && (() => {
        const visibleDomains = domains.filter(
          (d) => d === 'all' || d.toLowerCase().includes(domainSearch.toLowerCase())
        );
        return (
          <div className="glass-panel p-6 rounded-3xl border border-amber-500/20 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-amber-500/20">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-amber-400">
                <Layers className="w-4 h-4 text-amber-400" />
                <span>Domain Segregation List ({domains.length - 1} Domains)</span>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                {/* Domain Search Bar */}
                <div className="relative w-full sm:w-56">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-amber-400/70" />
                  <input
                    type="text"
                    value={domainSearch}
                    onChange={(e) => setDomainSearch(e.target.value)}
                    placeholder="Search domains..."
                    className="w-full pl-8 pr-3 py-1.5 bg-slate-950/90 border border-amber-500/30 focus:border-amber-400 rounded-xl text-xs text-white placeholder-slate-500 outline-none"
                  />
                </div>

                <div className="flex items-center bg-slate-950 border border-amber-500/25 rounded-xl p-0.5 text-xs">
                  <button
                    type="button"
                    onClick={() => setViewStyle('list-to-grid')}
                    className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                      viewStyle === 'list-to-grid' ? 'bg-amber-600 text-slate-950 font-bold shadow-sm' : 'text-slate-400 hover:text-white'
                    }`}
                    title="List with Grid below"
                  >
                    <LayoutGrid className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => setViewStyle('accordion')}
                    className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                      viewStyle === 'accordion' ? 'bg-amber-600 text-slate-950 font-bold shadow-sm' : 'text-slate-400 hover:text-white'
                    }`}
                    title="Collapsible Accordion List"
                  >
                    <List className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Interactive Domain List */}
            <div className="flex flex-wrap items-center gap-2 max-h-56 overflow-y-auto pr-1">
              {visibleDomains.map((dom) => {
                const isSelected = selectedDomain === dom;
                const count = dom === 'all' ? skills.length : (domainCounts[dom] || 0);
                const label = dom === 'all' ? 'All Domains' : dom;
                return (
                  <button
                    key={dom}
                    type="button"
                    onClick={() => setSelectedDomain(dom)}
                    className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer border ${
                      isSelected
                        ? 'bg-gradient-to-r from-amber-600 via-orange-500 to-amber-500 border-amber-400 text-slate-950 font-black shadow-lg shadow-amber-600/30 scale-[1.03]'
                        : 'bg-slate-950/80 border-amber-500/20 text-amber-200 hover:text-white hover:border-amber-500/50 hover:bg-amber-950/40'
                    }`}
                  >
                    <Cpu className={`w-3.5 h-3.5 ${isSelected ? 'text-slate-950' : 'text-amber-400'}`} />
                    <span>{label}</span>
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                        isSelected ? 'bg-slate-950/20 text-slate-950' : 'bg-amber-500/15 text-amber-300'
                      }`}
                    >
                      {count}
                    </span>
                  </button>
                );
              })}
              {visibleDomains.length === 0 && (
                <p className="text-xs text-slate-500 py-3">No domain found matching "{domainSearch}".</p>
              )}
            </div>
          </div>
        );
      })()}

      {/* Category Filter Pills (if multiple categories present) */}
      {categories.length > 2 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          <span className="text-xs text-slate-500 flex items-center gap-1 font-medium mr-1 shrink-0">
            <Filter className="w-3.5 h-3.5" /> Category:
          </span>
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
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

      {/* ACCORDION VIEW: Domains in a list, clicking opens grid directly below each item */}
      {viewStyle === 'accordion' && domains.filter((d) => d !== 'all').length > 0 ? (
        <div className="space-y-4">
          {domains
            .filter((dom) => dom !== 'all')
            .map((dom) => {
              const domSkills = filterAndSortSkills(skillsByDomain[dom] || []);
              const isExpanded = expandedAccordions[dom] ?? (selectedDomain === 'all' || selectedDomain === dom);

              return (
                <div
                  key={dom}
                  className="glass-panel rounded-3xl border border-slate-800 overflow-hidden transition-all shadow-md"
                >
                  {/* Domain List Row (Clickable) */}
                  <button
                    type="button"
                    onClick={() => toggleAccordion(dom)}
                    className="w-full p-4 sm:p-5 flex items-center justify-between bg-slate-900/70 hover:bg-slate-900 transition-colors cursor-pointer text-left"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
                        <Cpu className="w-4 h-4" />
                      </div>
                      <div>
                        <h3 className="text-sm sm:text-base font-bold text-white tracking-tight flex items-center gap-2">
                          <span>{dom}</span>
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-slate-800 text-indigo-300 font-semibold border border-slate-700">
                            {domSkills.length} {domSkills.length === 1 ? 'Skill' : 'Skills'}
                          </span>
                        </h3>
                        <p className="text-[11px] text-slate-400">
                          Click to {isExpanded ? 'collapse' : 'open'} skills grid below
                        </p>
                      </div>
                    </div>
                    <div className="p-2 rounded-xl bg-slate-950/60 border border-slate-800 text-slate-400">
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </div>
                  </button>

                  {/* Skills Grid Open Below the Domain item */}
                  {isExpanded && (
                    <div className="p-5 sm:p-6 border-t border-slate-800/80 bg-slate-950/30">
                      {domSkills.length === 0 ? (
                        <div className="p-8 text-center text-xs text-slate-500">
                          No skills found in domain "{dom}" matching active filters.
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 animate-fadeIn">
                          {domSkills.map((skill) => (
                            <SkillCard key={skill.id} skill={skill} isAdmin={false} />
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
        </div>
      ) : (
        /* STANDARD LIST-TO-GRID VIEW: Domain active selection opens skills grid below */
        <div className="space-y-4">
          {/* Active Domain Info Bar */}
          <div className="flex items-center justify-between text-xs text-slate-400 px-1">
            <span className="flex items-center gap-1.5 font-medium">
              <span className="text-indigo-400 font-semibold">Active Domain Grid:</span>{' '}
              {selectedDomain === 'all' ? 'All Technical Domains' : selectedDomain}
            </span>
            <span className="font-mono text-indigo-400">
              {filteredSkills.length} {filteredSkills.length === 1 ? 'Competency' : 'Competencies'}
            </span>
          </div>

          {/* Skills Grid */}
          {filteredSkills.length === 0 ? (
            <div className="glass-panel p-12 text-center text-slate-400 text-xs rounded-3xl border border-slate-800">
              No skills match your active filter criteria for domain: {selectedDomain === 'all' ? 'All' : selectedDomain}.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 animate-fadeIn">
              {filteredSkills.map((skill) => (
                <SkillCard key={skill.id} skill={skill} isAdmin={false} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
