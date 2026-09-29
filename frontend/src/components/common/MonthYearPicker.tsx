import React, { useMemo } from 'react';
import { Calendar } from 'lucide-react';

interface MonthYearPickerProps {
  label: string;
  value: string;
  onChange: (val: string) => void;
  disabled?: boolean;
  disabledPlaceholder?: string;
  required?: boolean;
  minYear?: number;
  maxYear?: number;
  className?: string;
}

const MONTHS = [
  { code: 'Jan', name: 'Jan - January' },
  { code: 'Feb', name: 'Feb - February' },
  { code: 'Mar', name: 'Mar - March' },
  { code: 'Apr', name: 'Apr - April' },
  { code: 'May', name: 'May - May' },
  { code: 'Jun', name: 'Jun - June' },
  { code: 'Jul', name: 'Jul - July' },
  { code: 'Aug', name: 'Aug - August' },
  { code: 'Sep', name: 'Sep - September' },
  { code: 'Oct', name: 'Oct - October' },
  { code: 'Nov', name: 'Nov - November' },
  { code: 'Dec', name: 'Dec - December' }
];

export const MonthYearPicker: React.FC<MonthYearPickerProps> = ({
  label,
  value,
  onChange,
  disabled = false,
  disabledPlaceholder = 'Present / Active (Disabled)',
  required = false,
  minYear = 1800,
  maxYear = 3000,
  className = ''
}) => {
  // Parse month and year from incoming string (supports 'Sep 2024', 'September 2024', '2024-09', etc.)
  const { currentMonth, currentYear } = useMemo(() => {
    if (!value || !value.trim()) {
      return { currentMonth: 'Jan', currentYear: 2024 };
    }

    const clean = value.trim();
    // Try "Month YYYY"
    const matchNamed = clean.match(/^([a-zA-Z]+)\s+([0-9]{4})$/);
    if (matchNamed) {
      const prefix = matchNamed[1].substring(0, 3).toLowerCase();
      const capitalized = prefix.charAt(0).toUpperCase() + prefix.slice(1);
      const foundMonth = MONTHS.find((m) => m.code.toLowerCase() === prefix);
      const mCode = foundMonth ? foundMonth.code : capitalized;
      const yr = parseInt(matchNamed[2], 10);
      return { currentMonth: mCode, currentYear: isNaN(yr) ? 2024 : Math.min(maxYear, Math.max(minYear, yr)) };
    }

    // Try "YYYY-MM"
    const matchIso = clean.match(/^([0-9]{4})[-/]([0-9]{1,2})$/);
    if (matchIso) {
      const yr = parseInt(matchIso[1], 10);
      const mNum = parseInt(matchIso[2], 10);
      const mCode = MONTHS[Math.min(11, Math.max(0, mNum - 1))].code;
      return { currentMonth: mCode, currentYear: isNaN(yr) ? 2024 : Math.min(maxYear, Math.max(minYear, yr)) };
    }

    // Fallback: year only or unknown
    const yrMatch = clean.match(/([0-9]{4})/);
    const yr = yrMatch ? parseInt(yrMatch[1], 10) : 2024;
    return { currentMonth: 'Jan', currentYear: isNaN(yr) ? 2024 : Math.min(maxYear, Math.max(minYear, yr)) };
  }, [value, minYear, maxYear]);

  // Generate Year options (1800 to 3000)
  // Presenting in descending order (3000 down to 1800) makes recent professional years (1990-2030) easily accessible
  const years = useMemo(() => {
    const list: number[] = [];
    for (let y = maxYear; y >= minYear; y--) {
      list.push(y);
    }
    return list;
  }, [minYear, maxYear]);

  const handleMonthChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newMonth = e.target.value;
    onChange(`${newMonth} ${currentYear}`);
  };

  const handleYearChange = (newYear: number) => {
    const clampedYear = Math.min(maxYear, Math.max(minYear, newYear));
    onChange(`${currentMonth} ${clampedYear}`);
  };

  if (disabled) {
    return (
      <div className={`space-y-1.5 ${className}`}>
        <label className="block text-xs font-medium text-slate-400">
          {label} {required && <span className="text-rose-400">*</span>}
        </label>
        <div className="px-3 py-2 bg-slate-950/60 border border-slate-800/80 rounded-xl text-xs text-slate-500 italic">
          {disabledPlaceholder}
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-1.5 ${className}`}>
      <div className="flex items-center justify-between">
        <label className="block text-xs font-medium text-slate-300">
          {label} {required && <span className="text-rose-400">*</span>}
        </label>
        <span className="text-[10px] font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-lg border border-indigo-500/20">
          {value || `${currentMonth} ${currentYear}`}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {/* Month Selector */}
        <select
          value={currentMonth}
          onChange={handleMonthChange}
          className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500 transition-colors cursor-pointer"
        >
          {MONTHS.map((m) => (
            <option key={m.code} value={m.code}>
              {m.name}
            </option>
          ))}
        </select>

        {/* Year Dropdown (1800 to 3000) */}
        <select
          value={currentYear}
          onChange={(e) => handleYearChange(parseInt(e.target.value, 10))}
          className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500 transition-colors cursor-pointer font-mono"
        >
          {years.map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
      </div>

      {/* Year Bar Slider (1800 to 3000) with quick controls */}
      <div className="pt-1 space-y-1">
        <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
          <span>{minYear}</span>
          <span className="text-slate-400">Year Bar ({minYear} – {maxYear})</span>
          <span>{maxYear}</span>
        </div>
        <input
          type="range"
          min={minYear}
          max={maxYear}
          value={currentYear}
          onChange={(e) => handleYearChange(parseInt(e.target.value, 10))}
          className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
          title={`Year: ${currentYear}`}
        />
      </div>
    </div>
  );
};
