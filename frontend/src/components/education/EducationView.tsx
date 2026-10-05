import React from 'react';
import { GraduationCap, Calendar, Building, Sparkles, Award, ArrowRight } from 'lucide-react';
import { Education, PublicTabType } from '../../types';
import { EmptyState } from '../common/EmptyState';

interface EducationViewProps {
  educations: Education[];
  onNavigate: (tab: PublicTabType) => void;
}

export const EducationView: React.FC<EducationViewProps> = ({ educations, onNavigate }) => {
  if (educations.length === 0) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6">
        <EmptyState
          icon={GraduationCap}
          title="No education records yet"
          description="Academic degrees, university credentials, and study programs have not been populated yet."
          actionText="Back to Home"
          onAction={() => onNavigate('home')}
        />
      </div>
    );
  }

  // Level hierarchy: Doctorate -> Post Graduate -> Graduate -> Diploma -> High School -> Matriculation
  const LEVEL_ORDER: Record<string, number> = {
    'Doctorate': 1,
    'Post Graduate': 2,
    'Graduate': 3,
    'Diploma': 4,
    'Undergraduate': 4,
    'High School': 5,
    'Matriculation': 6
  };

  const sortedEducations = [...educations].sort((a, b) => {
    const orderA = LEVEL_ORDER[a.level] ?? 99;
    const orderB = LEVEL_ORDER[b.level] ?? 99;
    if (orderA !== orderB) return orderA - orderB;
    if (a.ordering !== b.ordering) return a.ordering - b.ordering;
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  return (
    <div className="max-w-4xl mx-auto py-8 sm:py-16 px-4 sm:px-6 space-y-10 animate-fadeIn">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-purple-400 uppercase tracking-wider">
          <GraduationCap className="w-4 h-4" />
          <span>Academic Lineage & Degrees</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Education & Credentials
        </h1>
        <p className="text-xs sm:text-sm text-slate-400">
          Formal academic institutions, fields of study, degree levels, and enrollment history.
        </p>
      </div>

      {/* Timeline of Education Records */}
      <div className="relative pl-6 sm:pl-8 space-y-8 before:absolute before:left-2.5 sm:before:left-3.5 before:top-4 before:bottom-4 before:w-0.5 before:bg-slate-800">
        {sortedEducations.map((edu) => (
          <div key={edu.id} className="relative group">
            {/* Timeline node */}
            <div className={`absolute -left-6 sm:-left-8 top-3 w-4 h-4 rounded-full bg-slate-950 border-2 transition-transform duration-200 group-hover:scale-125 ${
              edu.currently_studying
                ? 'border-purple-400 shadow-md shadow-purple-500/50'
                : 'border-slate-600'
            }`} />

            <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 hover:border-purple-500/30 transition-all shadow-xl space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-purple-500/10 text-purple-300 border border-purple-500/20 w-fit">
                    {edu.level}
                  </span>
                  {edu.score_type && edu.score_value != null && (
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/20 flex items-center gap-1.5">
                      <Award className="w-3.5 h-3.5 text-amber-400" />
                      {edu.score_type === 'Percentage'
                        ? `${edu.score_value}%`
                        : `${edu.score_value} / ${edu.score_type === 'CGPA 10' ? '10' : '5'} CGPA`}
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  {edu.currently_studying ? (
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      Present · Currently Enrolled
                    </span>
                  ) : (
                    <span className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-slate-500" />
                      {edu.starting_month_year} – {edu.ending_month_year}
                    </span>
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight">
                  {edu.stream || `${edu.level} Education`}
                </h3>
                {edu.institution && (
                  <p className="text-xs sm:text-sm text-slate-400 flex items-center gap-1.5 mt-1 font-medium">
                    <Building className="w-3.5 h-3.5 text-slate-500" />
                    {edu.institution}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
