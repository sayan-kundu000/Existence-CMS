import React, { useState } from 'react';
import { ShieldAlert, KeyRound, Lock, AlertCircle, CheckCircle2, X } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export interface PinModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (pin: string) => void;
  title?: string;
  description?: string;
}

export const PinModal: React.FC<PinModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  title = "Security Verification Required",
  description = "Enter your security PIN to authorize this sensitive content change."
}) => {
  const { pinStatus, verifyPin, setupPin } = useAuth();
  const [pin, setPin] = useState('');
  const [confirmPin, setConfirmPin] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const isConfigured = pinStatus?.is_configured ?? false;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (pin.length < 4 || pin.length > 8) {
      setError("PIN must be between 4 and 8 digits.");
      return;
    }

    if (!isConfigured && pin !== confirmPin) {
      setError("PIN confirmation does not match.");
      return;
    }

    setLoading(true);
    try {
      if (!isConfigured) {
        await setupPin(pin);
      } else {
        await verifyPin(pin);
      }
      onSuccess(pin);
      onClose();
      setPin('');
      setConfirmPin('');
    } catch (err: any) {
      setError(err.message || "Failed to verify PIN");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-md p-6 bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl shadow-black/80">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-2xl">
            {isConfigured ? <KeyRound className="w-6 h-6" /> : <ShieldAlert className="w-6 h-6" />}
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">{title}</h3>
            <p className="text-xs text-slate-400">
              {isConfigured ? description : "Initial setup: Please configure your security PIN (4-8 digits)."}
            </p>
          </div>
        </div>

        {error && (
          <div className="flex items-start gap-2.5 p-3.5 mb-4 text-xs font-medium text-rose-300 bg-rose-950/40 border border-rose-800/50 rounded-xl">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              {isConfigured ? "Enter PIN" : "Create Security PIN"}
            </label>
            <div className="relative">
              <input
                type="password"
                maxLength={8}
                value={pin}
                onChange={(e) => setPin(e.target.value)}
                placeholder="••••"
                className="w-full px-4 py-3 bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-center text-xl tracking-widest text-white placeholder-slate-600 outline-none transition-all"
                autoFocus
                required
              />
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            </div>
          </div>

          {!isConfigured && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Confirm Security PIN
              </label>
              <div className="relative">
                <input
                  type="password"
                  maxLength={8}
                  value={confirmPin}
                  onChange={(e) => setConfirmPin(e.target.value)}
                  placeholder="••••"
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-center text-xl tracking-widest text-white placeholder-slate-600 outline-none transition-all"
                  required
                />
                <CheckCircle2 className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              </div>
            </div>
          )}

          {isConfigured && pinStatus && (
            <div className="text-[11px] text-slate-500 flex justify-between">
              <span>Remaining attempts:</span>
              <span className="font-semibold text-slate-400">{pinStatus.attempts_remaining}</span>
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2.5 rounded-xl border border-slate-800 hover:bg-slate-800 text-slate-300 text-sm font-medium transition-all"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium shadow-lg shadow-indigo-600/30 transition-all cursor-pointer"
            >
              {loading ? "Verifying..." : isConfigured ? "Authorize" : "Set PIN"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
