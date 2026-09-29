import React from 'react';

export const GlobalLoadingState: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8 space-y-8 animate-pulse">
      {/* Hero skeleton */}
      <div className="glass-panel p-8 sm:p-12 rounded-3xl border border-slate-800 space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
          <div className="w-24 h-24 rounded-3xl bg-slate-800/80 shrink-0" />
          <div className="space-y-3 flex-1">
            <div className="w-32 h-5 rounded-full bg-slate-800" />
            <div className="w-64 h-8 rounded-xl bg-slate-800" />
            <div className="w-full max-w-xl h-4 rounded bg-slate-800/60" />
            <div className="w-3/4 max-w-lg h-4 rounded bg-slate-800/60" />
          </div>
        </div>

        <div className="pt-8 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/60 space-y-2">
              <div className="w-16 h-3 rounded bg-slate-800" />
              <div className="w-8 h-6 rounded bg-slate-800" />
            </div>
          ))}
        </div>
      </div>

      {/* Cards skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="glass-card p-6 rounded-3xl border border-slate-800/80 space-y-4">
            <div className="w-10 h-10 rounded-2xl bg-slate-800" />
            <div className="w-40 h-5 rounded bg-slate-800" />
            <div className="w-full h-12 rounded bg-slate-800/50" />
          </div>
        ))}
      </div>
    </div>
  );
};
