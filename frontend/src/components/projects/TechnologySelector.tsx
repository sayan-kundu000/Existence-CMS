import React, { useState } from 'react';
import { Plus, X, Tag, Search, Check } from 'lucide-react';
import { TechCategory } from '../../types';

export const TECH_CATEGORIES: TechCategory[] = [
  'Programming Language',
  'Framework',
  'Database',
  'Cloud/Deployment',
  'Frontend',
  'Backend',
  'DevOps',
  'Testing',
  'Data/AI',
  'Other'
];

export interface TechItem {
  name: string;
  category?: TechCategory;
}

interface TechnologySelectorProps {
  value: TechItem[];
  onChange: (items: TechItem[]) => void;
  availableTechnologies?: string[];
}

export const TechnologySelector: React.FC<TechnologySelectorProps> = ({
  value,
  onChange,
  availableTechnologies = []
}) => {
  const [inputName, setInputName] = useState('');
  const [inputCategory, setInputCategory] = useState<TechCategory>('Programming Language');
  const [error, setError] = useState<string | null>(null);

  const handleAdd = () => {
    setError(null);
    const clean = inputName.trim();
    if (!clean) {
      setError('Please enter a technology name.');
      return;
    }

    // Check duplicate
    const exists = value.some(t => t.name.toLowerCase() === clean.toLowerCase());
    if (exists) {
      setError(`'${clean}' has already been added.`);
      return;
    }

    onChange([...value, { name: clean, category: inputCategory }]);
    setInputName('');
  };

  const handleRemove = (nameToRemove: string) => {
    onChange(value.filter(t => t.name.toLowerCase() !== nameToRemove.toLowerCase()));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAdd();
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
        {/* Name input */}
        <div className="relative flex-1">
          <input
            type="text"
            value={inputName}
            onChange={(e) => {
              setInputName(e.target.value);
              if (error) setError(null);
            }}
            onKeyDown={handleKeyDown}
            placeholder="Add technology (e.g. Python, React, PostgreSQL)..."
            className="w-full px-3.5 py-2 rounded-xl text-xs bg-slate-950/80 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {/* Category selector */}
        <select
          value={inputCategory}
          onChange={(e) => setInputCategory(e.target.value as TechCategory)}
          className="px-3 py-2 rounded-xl text-xs bg-slate-900 border border-slate-700 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
        >
          {TECH_CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>

        {/* Add button */}
        <button
          type="button"
          onClick={handleAdd}
          className="inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors cursor-pointer shrink-0"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Tech</span>
        </button>
      </div>

      {error && (
        <div className="text-xs text-rose-400 font-medium">
          {error}
        </div>
      )}

      {/* Selected chips */}
      {value.length > 0 ? (
        <div className="flex flex-wrap gap-2 pt-1">
          {value.map((item) => (
            <span
              key={item.name}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium bg-slate-800 text-slate-200 border border-slate-700/80 shadow-sm"
            >
              <span>{item.name}</span>
              {item.category && (
                <span className="text-[10px] text-slate-400 font-normal">
                  ({item.category})
                </span>
              )}
              <button
                type="button"
                onClick={() => handleRemove(item.name)}
                className="text-slate-400 hover:text-rose-400 transition-colors cursor-pointer ml-0.5"
                title={`Remove ${item.name}`}
                aria-label={`Remove ${item.name}`}
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </span>
          ))}
        </div>
      ) : (
        <div className="text-xs text-slate-400 italic font-light">
          No technologies added yet. Type a technology name above.
        </div>
      )}
    </div>
  );
};
