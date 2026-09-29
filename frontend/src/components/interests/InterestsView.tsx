import React from 'react';
import { Heart, Compass, Sparkles, Tag, ArrowRight } from 'lucide-react';
import { HobbyInterest, Hobby, Interest, PublicTabType } from '../../types';
import { EmptyState } from '../common/EmptyState';

interface InterestsViewProps {
  hobbies: (Hobby | HobbyInterest)[];
  interests: (Interest | HobbyInterest)[];
  onNavigate: (tab: PublicTabType) => void;
}

export const InterestsView: React.FC<InterestsViewProps> = ({
  hobbies,
  interests,
  onNavigate
}) => {
  const hasHobbies = hobbies && hobbies.length > 0;
  const hasInterests = interests && interests.length > 0;

  if (!hasHobbies && !hasInterests) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6">
        <EmptyState
          icon={Compass}
          title="No hobbies or interests added yet"
          description="Personal pastimes, creative pursuits, and intellectual curiosities have not been recorded yet."
          actionText="Back to Home"
          onAction={() => onNavigate('home')}
        />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8 sm:py-16 px-4 sm:px-6 space-y-12 animate-fadeIn">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-rose-400 uppercase tracking-wider">
          <Heart className="w-4 h-4" />
          <span>Curiosities & Personal Ethos</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Hobbies & Intellectual Interests
        </h1>
        <p className="text-xs sm:text-sm text-slate-400">
          Exploration of creative pastimes, intellectual pursuits, and non-vocational curiosities.
        </p>
      </div>

      {/* Hobbies Section */}
      <section className="space-y-6">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-800">
          <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <Heart className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">Personal Hobbies</h2>
            <p className="text-xs text-slate-400">Activities pursued for recreation, mastery, and creative flow.</p>
          </div>
        </div>

        {hasHobbies ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {hobbies.map((h) => (
              <div
                key={h.id}
                className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-rose-500/30 transition-all shadow-lg flex items-start gap-4"
              >
                <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center shrink-0 text-lg">
                  {h.icon ? <span>{h.icon}</span> : <Heart className="w-5 h-5 text-rose-400" />}
                </div>
                <div>
                  <h3 className="text-base font-bold text-white tracking-tight">{h.name}</h3>
                  {h.category && (
                    <span className="inline-block mt-1 px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[10px] font-semibold text-rose-300">
                      {h.category}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-slate-500 rounded-2xl border border-slate-800/60">
            No personal hobbies configured yet.
          </div>
        )}
      </section>

      {/* Intellectual Interests Section */}
      <section className="space-y-6 pt-6">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-800">
          <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">Intellectual & Technical Interests</h2>
            <p className="text-xs text-slate-400">Topics of theoretical inquiry, technical research, and academic fascination.</p>
          </div>
        </div>

        {hasInterests ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {interests.map((it) => (
              <div
                key={it.id}
                className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-purple-500/30 transition-all shadow-lg flex items-start gap-4"
              >
                <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center shrink-0 text-lg">
                  {it.icon ? <span>{it.icon}</span> : <Compass className="w-5 h-5 text-purple-400" />}
                </div>
                <div>
                  <h3 className="text-base font-bold text-white tracking-tight">{it.name}</h3>
                  {it.category && (
                    <span className="inline-block mt-1 px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[10px] font-semibold text-purple-300">
                      {it.category}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-slate-500 rounded-2xl border border-slate-800/60">
            No intellectual interests configured yet.
          </div>
        )}
      </section>
    </div>
  );
};
