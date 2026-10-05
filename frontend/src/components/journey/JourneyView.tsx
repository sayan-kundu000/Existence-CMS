import React, { useMemo } from 'react';
import { GraduationCap, Briefcase, Calendar, MapPin, Building, Sparkles, Award, Clock } from 'lucide-react';
import { Education, Experience } from '../../types';
import { EmptyState } from '../common/EmptyState';
import { calculateExperienceDuration, sortExperiencesByTimelineDesc } from '../../utils/dateHelpers';

interface JourneyViewProps {
  educations: Education[];
  experiences: Experience[];
  onNavigateToCms: () => void;
}

export const JourneyView: React.FC<JourneyViewProps> = ({
  educations,
  experiences,
  onNavigateToCms
}) => {
  const sortedExperiences = useMemo(() => {
    return sortExperiencesByTimelineDesc(experiences);
  }, [experiences]);
  return (
    <div className="max-w-5xl mx-auto py-8 sm:py-12 px-4 sm:px-6 space-y-12 animate-fadeIn">
      {/* Page Title */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Professional Journey & Academic Lineage
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Chronological record of roles, institutions, work modes, and academic credentials.
        </p>
      </div>

      {/* Work Experience Section */}
      <section className="space-y-6">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <h2 className="text-lg font-bold text-white flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Briefcase className="w-5 h-5" />
            </div>
            Work Experience
          </h2>
          <span className="text-xs font-mono text-slate-500">
            {experiences.length} {experiences.length === 1 ? 'Record' : 'Records'}
          </span>
        </div>

        {experiences.length === 0 ? (
          <EmptyState
            icon={Briefcase}
            title="No work experience yet"
            description="Professional appointments, roles, and employment history have not been added yet."
            actionText="Add Experience via CMS"
            onAction={onNavigateToCms}
          />
        ) : (
          <div className="relative pl-6 sm:pl-8 space-y-8 before:absolute before:left-2 sm:before:left-3 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
            {sortedExperiences.map((exp) => {
              const duration = calculateExperienceDuration(
                exp.starting_month_year,
                exp.ending_month_year,
                exp.currently_working
              );
              return (
              <div key={exp.id} className="relative group">
                {/* Timeline node */}
                <div className="absolute -left-6 sm:-left-8 top-1.5 w-4 h-4 rounded-full bg-slate-950 border-2 border-indigo-500 shadow-md shadow-indigo-500/50 group-hover:scale-125 transition-transform" />

                <div className="glass-card p-5 sm:p-6 rounded-2xl border border-slate-800/80 hover:border-slate-700 transition-all shadow-lg">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                    <h3 className="text-base sm:text-lg font-bold text-white tracking-tight">
                      {exp.role}
                    </h3>
                    <div className="flex items-center gap-2 flex-wrap">
                      {exp.currently_working ? (
                        <>
                          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            Currently Working
                          </span>
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 flex items-center gap-1">
                            <Clock className="w-3 h-3 text-indigo-400" />
                            {duration.formatted}
                          </span>
                        </>
                      ) : (
                        <>
                          <span className="text-xs font-medium text-slate-400 flex items-center gap-1">
                            <Calendar className="w-3.5 h-3.5 text-slate-500" />
                            {exp.starting_month_year} – {exp.ending_month_year}
                          </span>
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-slate-900 text-indigo-300 border border-slate-800 flex items-center gap-1">
                            <Clock className="w-3 h-3 text-indigo-400" />
                            {duration.formatted}
                          </span>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-300 mb-3">
                    <span className="flex items-center gap-1.5 font-medium text-indigo-300">
                      <Building className="w-3.5 h-3.5" />
                      {exp.employer}
                    </span>
                    <span className="text-slate-600">•</span>
                    <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[11px] font-medium text-slate-300">
                      {exp.work_mode}
                    </span>
                    {exp.location && (
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
      </section>

      {/* Education Section */}
      <section className="space-y-6 pt-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <h2 className="text-lg font-bold text-white flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <GraduationCap className="w-5 h-5" />
            </div>
            Education & Academic Lineage
          </h2>
          <span className="text-xs font-mono text-slate-500">
            {educations.length} {educations.length === 1 ? 'Record' : 'Records'}
          </span>
        </div>

        {educations.length === 0 ? (
          <EmptyState
            icon={GraduationCap}
            title="No education records yet."
            description="Add your degrees, institutions, and areas of study securely from the CMS."
            actionText="Add Education via CMS"
            onAction={onNavigateToCms}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            {(() => {
              const LEVEL_ORDER: Record<string, number> = {
                'Doctorate': 1,
                'Post Graduate': 2,
                'Graduate': 3,
                'Diploma': 4,
                'Undergraduate': 4,
                'High School': 5,
                'Matriculation': 6
              };
              const sorted = [...educations].sort((a, b) => {
                const orderA = LEVEL_ORDER[a.level] ?? 99;
                const orderB = LEVEL_ORDER[b.level] ?? 99;
                if (orderA !== orderB) return orderA - orderB;
                if (a.ordering !== b.ordering) return a.ordering - b.ordering;
                return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
              });
              return sorted.map((edu) => (
              <div
                key={edu.id}
                className="glass-card p-5 sm:p-6 rounded-2xl border border-slate-800/80 hover:border-purple-500/30 transition-all shadow-lg flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2 flex-wrap">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wider uppercase bg-purple-500/10 text-purple-300 border border-purple-500/20">
                        {edu.level}
                      </span>
                      {edu.score_type && edu.score_value != null && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/20 flex items-center gap-1">
                          <Award className="w-3 h-3 text-amber-400" />
                          {edu.score_type === 'Percentage'
                            ? `${edu.score_value}%`
                            : `${edu.score_value} / ${edu.score_type === 'CGPA 10' ? '10' : '5'} CGPA`}
                        </span>
                      )}
                    </div>
                    {edu.currently_studying && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        Currently Enrolled
                      </span>
                    )}
                  </div>
                  <h3 className="text-base sm:text-lg font-bold text-white tracking-tight mb-1">
                    {edu.stream || `${edu.level} Education`}
                  </h3>
                  {edu.institution && (
                    <p className="text-xs text-slate-400 font-medium flex items-center gap-1.5 mb-3">
                      <Building className="w-3.5 h-3.5 text-slate-500" />
                      {edu.institution}
                    </p>
                  )}
                </div>

                <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-slate-500" />
                    {edu.starting_month_year} – {edu.currently_studying ? 'Present' : edu.ending_month_year}
                  </span>
                </div>
              </div>
            ));
            })()}
          </div>
        )}
      </section>
    </div>
  );
};
