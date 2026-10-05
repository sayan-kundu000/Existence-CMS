import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, PinStatus } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  pinStatus: PinStatus | null;
  activePin: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  lockPin: () => Promise<void>;
  refreshPinStatus: () => Promise<void>;
  verifyPin: (pin: string) => Promise<boolean>;
  setupPin: (pin: string) => Promise<boolean>;
  changePin: (currentPin: string, newPin: string) => Promise<boolean>;
  setActivePin: (pin: string | null) => void;
  hasRole: (role: string) => boolean;
  hasPermission: (permission: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [pinStatus, setPinStatus] = useState<PinStatus | null>(null);
  const [activePin, setActivePinState] = useState<string | null>(api.getActivePin());

  const refreshPinStatus = async () => {
    try {
      if (api.getToken()) {
        const status = await api.getPinStatus();
        setPinStatus(status);
        if (status.is_locked) {
          setActivePinState(null);
          api.setActivePin(null);
        }
      }
    } catch {
      // Ignored if unauthenticated or locked
    }
  };

  const loadUser = async () => {
    setLoading(true);
    try {
      if (api.getToken()) {
        const u = await api.getMe();
        setUser(u);
        await refreshPinStatus();
      } else {
        setUser(null);
      }
    } catch {
      await api.logout();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUser();
  }, []);

  const login = async (username: string, password: string) => {
    await api.login(username, password);
    await loadUser();
  };

  const logout = async () => {
    await api.logout();
    setUser(null);
    setPinStatus(null);
    setActivePinState(null);
  };

  const lockPin = async () => {
    await api.lockPin();
    setActivePinState(null);
    await refreshPinStatus();
  };

  const verifyPin = async (pin: string): Promise<boolean> => {
    try {
      const res = await api.verifyPin(pin);
      const tokenToUse = res.pin_token || pin;
      setActivePinState(tokenToUse);
      api.setActivePin(tokenToUse);
      await refreshPinStatus();
      return true;
    } catch (err) {
      setActivePinState(null);
      api.setActivePin(null);
      await refreshPinStatus();
      throw err;
    }
  };

  const setupPin = async (pin: string): Promise<boolean> => {
    await api.setupPin(pin);
    setActivePinState(pin);
    await refreshPinStatus();
    if (user) {
      setUser({ ...user, pin_configured: true });
    }
    return true;
  };

  const changePin = async (currentPin: string, newPin: string): Promise<boolean> => {
    await api.changePin(currentPin, newPin);
    setActivePinState(newPin);
    await refreshPinStatus();
    return true;
  };

  const setActivePin = (pin: string | null) => {
    api.setActivePin(pin);
    setActivePinState(pin);
  };

  const hasRole = (role: string): boolean => {
    if (!user) return false;
    return user.role.toLowerCase() === role.toLowerCase();
  };

  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    if (user.role === 'admin') return true;
    if (user.permissions && Array.isArray(user.permissions)) {
      return user.permissions.includes('*') || user.permissions.includes(permission);
    }
    return false;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        isAdmin: user?.role === 'admin',
        pinStatus,
        activePin,
        login,
        logout,
        lockPin,
        refreshPinStatus,
        verifyPin,
        setupPin,
        changePin,
        setActivePin,
        hasRole,
        hasPermission
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
