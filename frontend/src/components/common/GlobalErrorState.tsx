import React from 'react';
import { AlertCircle, RefreshCw, WifiOff } from 'lucide-react';

interface GlobalErrorStateProps {
  message?: string;
  onRetry: () => void;
  isOffline?: boolean;
}

export const GlobalErrorState: React.FC<GlobalErrorStateProps> = ({
  message,
  onRetry,
  isOffline = false
}) => {
  return (
    <div className="max-w-2xl mx-auto py-20 px-4 sm:px-6 text-center space-y-6 animate-fadeIn">
      <div className="w-16 h-16 rounded-3xl bg-rose-500/10 border border-rose-500/20 text-rose-400 mx-auto flex items-center justify-center">
        {isOffline ? <WifiOff className="w-8 h-8" /> : <AlertCircle className="w-8 h-8" />}
      </div>

      <div className="space-y-2">
        <h2 className="text-2xl font-bold text-white tracking-tight">
          {isOffline ? 'You Appear to Be Offline' : 'Unable to Connect to Existence API'}
        </h2>
        <p className="text-sm text-slate-400 max-w-md mx-auto leading-relaxed">
          {isOffline
            ? 'Your internet connection was interrupted. Check your network connection and retry.'
            : message || 'The backend services could not be reached. Ensure the FastAPI REST server is running.'}
        </p>
      </div>

      <div className="pt-2">
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition-all cursor-pointer"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Retry Connection</span>
        </button>
      </div>
    </div>
  );
};
