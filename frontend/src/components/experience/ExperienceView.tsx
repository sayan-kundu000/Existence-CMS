import React, { useState, useMemo } from 'react';
import { Briefcase, Calendar, MapPin, Building, Clock, CheckCircle2 } from 'lucide-react';
import { Experience, PublicTabType } from '../../types';
import { EmptyState } from '../common/EmptyState';
import {
  calculateExperienceDuration,
  calculateOverallExperience,
  sortExperiencesByTimelineDesc
} from '../../utils/dateHelpers';

interface ExperienceViewProps {
  experiences: Experience[];
  onNavigate: (tab: PublicTabType) => void;
}

export const ExperienceView: React.FC<ExperienceViewProps> = ({ experiences, onNavigate }) => {
  const [filterMode, setFilterMode] = useState<string>('all');

  // Overall experience calculated across all positions (handling currently working dynamically)
  const overallExperience = useMemo(() => {
    return calculateOverallExperience(experiences);
  }, [experiences]);

  // Sort strictly in descending order of timelines
  const sortedExperiences = useMemo(() => {
    return sortExperiencesByTimelineDesc(experiences);
  }, [experiences]);

  if (experiences.length === 0) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6">
        <EmptyState
          icon={Briefcase}
          title="No work experience yet"
          description="Professional appointments, employment history, and career trajectory have not been recorded yet."
          actionText="Back to Home"
          onAction={() => onNavigate('home')}
        />
      </div>
    );
  }

  // Filter sorted experiences by work mode
  const filteredExperiences = sortedExperiences.filter((exp) => {
    if (filterMode === 'all') return true;
    return exp.work_mode.toLowerCase() === filterMode.toLowerCase();
  });

  const activeRolesCount = experiences.filter((e) => e.currently_working).length;

  return (
    <div className="max-w-4xl mx-auto py-8 sm:py-16 px-4 sm:px-6 space-y-10 animate-fadeIn">
      {/* Header and Filter */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider">
            <Briefcase className="w-4 h-4" />
            <span>Professional Appointments & Roles</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Work Experience
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Chronological employment history sorted in descending timeline order with verified durations.
          </p>
        </div>

        {/* Work Mode filter */}
        <div className="flex items-center gap-1.5 bg-slate-900/80 p-1 rounded-2xl border border-slate-800 text-xs">
          {['all', 'on-site', 'remote', 'hybrid'].map((mode) => (
            <button
              key={mode}
              onClick={() => setFilterMode(mode)}
              className={`px-3 py-1.5 rounded-xl font-medium capitalize transition-all cursor-pointer ${
                filterMode === mode
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      {/* OVERALL EXPERIENCE SUMMARY STATS PANEL */}
      <div className="glass-panel p-6 sm:p-7 rounded-3xl border border-slate-800 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 relative z-10">
          {/* Total Overall Experience */}
          <div className="space-y-1.5">
            <div className="flex items-center gap-1.5 text-xs text-indigo-400 font-bold uppercase tracking-wider">
              <Clock className="w-3.5 h-3.5" />
              <span>Total Career Experience</span>
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold text-white font-mono tracking-tight">
              {overallExperience.formatted}
            </div>
            <p className="text-[11px] text-slate-400">
              Net cumulative duration across all appointments
            </p>
          </div>

          {/* Active Appointments */}
          <div className="space-y-1.5 sm:border-l sm:border-slate-800/80 sm:pl-6">
            <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-bold uppercase tracking-wider">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Current Status</span>
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold text-white font-mono tracking-tight">
              {activeRolesCount > 0 ? `${activeRolesCount} Active` : 'Alumnus'}
            </div>
            <p className="text-[11px] text-slate-400">
              {activeRolesCount > 0 ? 'Currently serving in active appointment' : 'All appointments completed'}
            </p>
          </div>

          {/* Total Appointments Count */}
          <div className="space-y-1.5 sm:border-l sm:border-slate-800/80 sm:pl-6">
            <div className="flex items-center gap-1.5 text-xs text-purple-400 font-bold uppercase tracking-wider">
              <Briefcase className="w-3.5 h-3.5" />
              <span>Total Recorded Roles</span>
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold text-white font-mono tracking-tight">
              {experiences.length} {experiences.length === 1 ? 'Role' : 'Roles'}
            </div>
            <p className="text-[11px] text-slate-400">
              Chronologically sorted, most recent first
            </p>
          </div>
        </div>
      </div>

      {/* Timeline of Experience (Sorted Descending) */}
      {filteredExperiences.length === 0 ? (
        <div className="p-12 text-center text-xs text-slate-500">
          No experience records match the selected work mode filter.
        </div>
      ) : (
        <div className="relative pl-6 sm:pl-8 space-y-8 before:absolute before:left-2.5 sm:before:left-3.5 before:top-4 before:bottom-4 before:w-0.5 before:bg-slate-800">
          {filteredExperiences.map((exp) => {
            const duration = calculateExperienceDuration(
              exp.starting_month_year,
              exp.ending_month_year,
              exp.currently_working
            );

            return (
              <div key={exp.id} className="relative group">
                {/* Timeline node */}
                <div
                  className={`absolute -left-6 sm:-left-8 top-3 w-4 h-4 rounded-full bg-slate-950 border-2 transition-transform duration-200 group-hover:scale-125 ${
                    exp.currently_working
                      ? 'border-indigo-400 shadow-md shadow-indigo-500/50'
                      : 'border-slate-600'
                  }`}
                />

                <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 hover:border-indigo-500/30 transition-all shadow-xl space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight">
                      {exp.role}
                    </h3>

                    {/* Timeline dates & Individual Duration */}
                    <div className="flex flex-wrap items-center gap-2">
                      {exp.currently_working ? (
                        <>
                          <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                            Present · Active Role
                          </span>
                          <span className="px-2.5 py-1 rounded-full text-xs font-bold font-mono bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 flex items-center gap-1" title="Duration calculated up to present date">
                            <Clock className="w-3.5 h-3.5 text-indigo-400" />
                            {duration.formatted}
                          </span>
                        </>
                      ) : (
                        <>
                          <span className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
                            <Calendar className="w-3.5 h-3.5 text-slate-500" />
                            {exp.starting_month_year} – {exp.ending_month_year}
                          </span>
                          <span className="px-2.5 py-1 rounded-full text-xs font-bold font-mono bg-slate-900 text-indigo-300 border border-slate-800 flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5 text-indigo-400" />
                            {duration.formatted}
                          </span>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-300">
                    <span className="flex items-center gap-1.5 font-semibold text-indigo-300">
                      <Building className="w-3.5 h-3.5 text-indigo-400" />
                      {exp.employer}
                    </span>
                    <span className="text-slate-600">•</span>
                    <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[11px] font-medium text-slate-300">
                      {exp.work_mode}
                    </span>
                    {exp.location && exp.work_mode !== 'Remote' && (
                      <>
                        <span className="text-slate-600">•</span>
                        <span className="flex items-center gap-1 text-slate-400">
                          <MapPin className="w-3.5 h-3.5 text-slate-500" />
                          {exp.location}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
