import React, { useState, useMemo } from 'react';
import { Search, Plus, X, Check, Globe, Layers, Filter } from 'lucide-react';
import {
  DOMAIN_TAXONOMY,
  DOMAIN_FIELDS,
  DomainField,
  DomainItem,
  filterDomainsByQuery
} from '../../data/domainTaxonomy';

interface SkillDomainSelectorProps {
  selectedDomains: string[];
  onChange: (domains: string[]) => void;
  label?: string;
}

export const SkillDomainSelector: React.FC<SkillDomainSelectorProps> = ({
  selectedDomains,
  onChange,
  label = 'Select Domain(s) *'
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedField, setSelectedField] = useState<DomainField>('All Fields');
  const [isExpanded, setIsExpanded] = useState(false);

  const filteredDomains = useMemo(() => {
    return filterDomainsByQuery(searchQuery, selectedField);
  }, [searchQuery, selectedField]);

  const toggleDomain = (domainName: string) => {
    const trimmed = domainName.trim();
    if (!trimmed) return;
    if (selectedDomains.includes(trimmed)) {
      onChange(selectedDomains.filter((d) => d !== trimmed));
    } else {
      onChange([...selectedDomains, trimmed]);
    }
  };

  const removeDomain = (domainName: string) => {
    onChange(selectedDomains.filter((d) => d !== domainName));
  };

  const handleAddCustomDomain = () => {
    const trimmed = searchQuery.trim();
    if (!trimmed) return;
    if (!selectedDomains.includes(trimmed)) {
      onChange([...selectedDomains, trimmed]);
    }
    setSearchQuery('');
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="block text-xs font-semibold text-amber-200/90 flex items-center gap-1.5">
          <Globe className="w-3.5 h-3.5 text-amber-400" />
          <span>{label}</span>
          <span className="text-[10px] text-amber-400/80 font-normal">
            (Multi-select allowed)
          </span>
        </label>
        <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300">
          {selectedDomains.length} Selected
        </span>
      </div>

      {/* Selected Domain Badges */}
      {selectedDomains.length > 0 && (
        <div className="flex flex-wrap gap-1.5 p-2.5 rounded-xl bg-amber-950/30 border border-amber-500/20 max-h-28 overflow-y-auto">
          {selectedDomains.map((dom) => (
            <span
              key={dom}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-amber-600/25 border border-amber-500/40 text-amber-200 shadow-sm"
            >
              <span>{dom}</span>
              <button
                type="button"
                onClick={() => removeDomain(dom)}
                className="p-0.5 hover:bg-amber-500/30 rounded-md transition-colors text-amber-300 hover:text-white cursor-pointer"
                title={`Remove ${dom}`}
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
          <button
            type="button"
            onClick={() => onChange([])}
            className="text-[11px] text-amber-400 hover:text-amber-200 hover:underline px-2 py-1 cursor-pointer font-medium"
          >
            Clear all
          </button>
        </div>
      )}

      {/* Search Bar & Expansion Toggle */}
      <div className="relative">
        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-amber-400/70" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            if (!isExpanded) setIsExpanded(true);
          }}
          onFocus={() => setIsExpanded(true)}
          placeholder="Search 70+ domains (Mechanical, Software, Petroleum, Biotechnology, Medical, Legal, AIML...)"
          className="w-full pl-9 pr-24 py-2.5 bg-slate-950/90 border border-amber-500/30 focus:border-amber-500 rounded-xl text-xs text-white placeholder-slate-500 outline-none transition-all shadow-inner"
        />
        {searchQuery.trim() && (
          <button
            type="button"
            onClick={handleAddCustomDomain}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-2.5 py-1 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-[10px] font-semibold flex items-center gap-1 shadow transition-all cursor-pointer"
          >
            <Plus className="w-3 h-3" />
            Add Custom
          </button>
        )}
      </div>

      {/* Field Filter Buttons */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px] scrollbar-thin">
        {DOMAIN_FIELDS.map((field) => (
          <button
            key={field}
            type="button"
            onClick={() => setSelectedField(field)}
            className={`px-2.5 py-1 rounded-lg whitespace-nowrap transition-all cursor-pointer font-medium ${
              selectedField === field
                ? 'bg-amber-500 text-slate-950 font-bold shadow-sm'
                : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800'
            }`}
          >
            {field}
          </button>
        ))}
      </div>

      {/* Domains Dropdown / List */}
      <div className="max-h-56 overflow-y-auto rounded-xl border border-amber-500/20 bg-slate-950/95 p-2 space-y-1 divide-y divide-slate-900 shadow-xl">
        {filteredDomains.map((item) => {
          const isSelected = selectedDomains.includes(item.name);
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => toggleDomain(item.name)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left text-xs transition-all cursor-pointer ${
                isSelected
                  ? 'bg-amber-600/20 border border-amber-500/40 text-amber-200'
                  : 'hover:bg-slate-900 text-slate-200'
              }`}
            >
              <div className="flex-1 pr-2">
                <div className="flex items-center gap-2">
                  <span className="font-semibold">{item.name}</span>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-medium bg-amber-500/10 border border-amber-500/20 text-amber-400">
                    {item.field}
                  </span>
                </div>
                {item.keywords && item.keywords.length > 0 && (
                  <p className="text-[10px] text-slate-500 mt-0.5 truncate">
                    {item.keywords.slice(0, 5).join(' • ')}
                  </p>
                )}
              </div>
              <div
                className={`w-4 h-4 rounded border flex items-center justify-center shrink-0 transition-colors ${
                  isSelected
                    ? 'bg-amber-500 border-amber-400 text-slate-950'
                    : 'border-slate-700 bg-slate-900 text-transparent'
                }`}
              >
                <Check className="w-3 h-3 stroke-[3]" />
              </div>
            </button>
          );
        })}

        {filteredDomains.length === 0 && (
          <div className="py-6 text-center text-xs text-slate-400">
            <p>No predefined domain matches "{searchQuery}".</p>
            <button
              type="button"
              onClick={handleAddCustomDomain}
              className="mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-semibold cursor-pointer shadow"
            >
              <Plus className="w-3.5 h-3.5" />
              Add "{searchQuery.trim()}" as a new domain
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
