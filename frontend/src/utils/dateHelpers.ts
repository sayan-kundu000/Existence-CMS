import { Experience } from '../types';

const MONTH_MAP: Record<string, number> = {
  jan: 0,
  feb: 1,
  mar: 2,
  apr: 3,
  may: 4,
  jun: 5,
  jul: 6,
  aug: 7,
  sep: 8,
  oct: 9,
  nov: 10,
  dec: 11
};

/**
 * Parses month & year from various date string formats:
 * - "Jan 2024", "January 2024"
 * - "2024-01", "2024/01"
 * - "2024"
 * Returns { year, month: 0-11 } or null.
 */
export function parseMonthYear(val?: string | null): { year: number; month: number } | null {
  if (!val || !val.trim()) return null;
  const clean = val.trim();

  // "Month YYYY" e.g. "Jan 2024", "January 2024"
  const matchNamed = clean.match(/^([a-zA-Z]+)\s+([0-9]{4})$/);
  if (matchNamed) {
    const prefix = matchNamed[1].substring(0, 3).toLowerCase();
    const month = MONTH_MAP[prefix] ?? 0;
    const year = parseInt(matchNamed[2], 10);
    return { year, month };
  }

  // "YYYY-MM" or "YYYY/MM"
  const matchIso = clean.match(/^([0-9]{4})[-/]([0-9]{1,2})$/);
  if (matchIso) {
    const year = parseInt(matchIso[1], 10);
    const month = Math.max(0, Math.min(11, parseInt(matchIso[2], 10) - 1));
    return { year, month };
  }

  // Year only "2024"
  const matchYear = clean.match(/^[0-9]{4}$/);
  if (matchYear) {
    return { year: parseInt(matchYear[0], 10), month: 0 };
  }

  return null;
}

export interface ExperienceDurationResult {
  years: number;
  months: number;
  totalMonths: number;
  formatted: string;
}

/**
 * Formats a given number of months into human-readable years and months.
 * e.g. 26 months -> "2 years 2 months"
 *      12 months -> "1 year"
 *      1 month   -> "1 month"
 *      5 months  -> "5 months"
 */
export function formatYearsAndMonths(totalMonths: number): string {
  if (totalMonths <= 0) return '0 months';
  const years = Math.floor(totalMonths / 12);
  const remainingMonths = totalMonths % 12;

  const yearPart = years > 0 ? `${years} ${years === 1 ? 'year' : 'years'}` : '';
  const monthPart = remainingMonths > 0 ? `${remainingMonths} ${remainingMonths === 1 ? 'month' : 'months'}` : '';

  if (yearPart && monthPart) return `${yearPart} ${monthPart}`;
  if (yearPart) return yearPart;
  return monthPart || '1 month';
}

/**
 * Calculates duration for an individual experience record.
 * Handles `currently_working: true` dynamically up to the current date.
 */
export function calculateExperienceDuration(
  startingMonthYear: string,
  endingMonthYear: string | null,
  currentlyWorking: boolean
): ExperienceDurationResult {
  const start = parseMonthYear(startingMonthYear);
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth(); // 0-11

  let end = currentlyWorking
    ? { year: currentYear, month: currentMonth }
    : parseMonthYear(endingMonthYear);

  if (!start) {
    return { years: 0, months: 0, totalMonths: 0, formatted: '0 months' };
  }

  if (!end) {
    end = { year: currentYear, month: currentMonth };
  }

  const startMonthIndex = start.year * 12 + start.month;
  let endMonthIndex = end.year * 12 + end.month;

  if (endMonthIndex < startMonthIndex) {
    endMonthIndex = startMonthIndex;
  }

  // Inclusive month calculation (e.g. Jan 2024 to Dec 2024 = 12 months)
  const totalMonths = endMonthIndex - startMonthIndex + 1;
  const years = Math.floor(totalMonths / 12);
  const months = totalMonths % 12;

  return {
    years,
    months,
    totalMonths,
    formatted: formatYearsAndMonths(totalMonths)
  };
}

export interface OverallExperienceResult {
  totalYears: number;
  totalMonths: number;
  netMonths: number;
  formatted: string;
}

/**
 * Calculates overall cumulative experience across all experience records.
 * Uses interval merging so concurrent/overlapping roles do not double-count months,
 * accurately reflecting true calendar career duration.
 */
export function calculateOverallExperience(experiences: Experience[]): OverallExperienceResult {
  if (!experiences || experiences.length === 0) {
    return { totalYears: 0, totalMonths: 0, netMonths: 0, formatted: '0 months' };
  }

  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth();

  interface Interval {
    start: number;
    end: number;
  }

  const intervals: Interval[] = [];

  for (const exp of experiences) {
    const start = parseMonthYear(exp.starting_month_year);
    if (!start) continue;

    const end = exp.currently_working
      ? { year: currentYear, month: currentMonth }
      : parseMonthYear(exp.ending_month_year);

    const startIdx = start.year * 12 + start.month;
    let endIdx = end ? end.year * 12 + end.month : currentYear * 12 + currentMonth;

    if (endIdx < startIdx) {
      endIdx = startIdx;
    }

    intervals.push({ start: startIdx, end: endIdx });
  }

  if (intervals.length === 0) {
    return { totalYears: 0, totalMonths: 0, netMonths: 0, formatted: '0 months' };
  }

  // Sort intervals by start ascending
  intervals.sort((a, b) => a.start - b.start);

  // Merge overlapping or adjacent intervals
  const merged: Interval[] = [intervals[0]];
  for (let i = 1; i < intervals.length; i++) {
    const current = intervals[i];
    const last = merged[merged.length - 1];

    if (current.start <= last.end + 1) {
      last.end = Math.max(last.end, current.end);
    } else {
      merged.push({ ...current });
    }
  }

  // Sum total net months across merged intervals
  let netMonths = 0;
  for (const interval of merged) {
    netMonths += interval.end - interval.start + 1;
  }

  const totalYears = Math.floor(netMonths / 12);
  const totalMonths = netMonths % 12;

  return {
    totalYears,
    totalMonths,
    netMonths,
    formatted: formatYearsAndMonths(netMonths)
  };
}

/**
 * Sorts experiences in descending order of timelines:
 * 1. Active roles (`currently_working: true`) on top, sorted by start date descending.
 * 2. Completed roles sorted by end date descending (most recently ended first).
 * 3. Ties broken by start date descending.
 */
export function sortExperiencesByTimelineDesc(experiences: Experience[]): Experience[] {
  if (!experiences || experiences.length === 0) return [];

  const now = new Date();
  const currentIdx = now.getFullYear() * 12 + now.getMonth();

  const getStartIdx = (exp: Experience): number => {
    const parsed = parseMonthYear(exp.starting_month_year);
    return parsed ? parsed.year * 12 + parsed.month : 0;
  };

  const getEndIdx = (exp: Experience): number => {
    if (exp.currently_working) {
      return currentIdx + 99999; // active roles on top
    }
    const parsed = parseMonthYear(exp.ending_month_year);
    return parsed ? parsed.year * 12 + parsed.month : getStartIdx(exp);
  };

  return [...experiences].sort((a, b) => {
    // 1. Active vs Completed
    if (a.currently_working && !b.currently_working) return -1;
    if (!a.currently_working && b.currently_working) return 1;

    // 2. Both currently working: most recent start date first
    if (a.currently_working && b.currently_working) {
      const startDiff = getStartIdx(b) - getStartIdx(a);
      if (startDiff !== 0) return startDiff;
    }

    // 3. Both completed: most recent end date first
    const endDiff = getEndIdx(b) - getEndIdx(a);
    if (endDiff !== 0) return endDiff;

    // 4. If end date same: most recent start date first
    const startDiff = getStartIdx(b) - getStartIdx(a);
    if (startDiff !== 0) return startDiff;

    // 5. Fallback: ID descending
    return b.id - a.id;
  });
}
