'use client';

import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { api } from './api';

interface User {
  id: number;
  username: string;
  role: 'admin' | 'checker';
}

interface AuthContextValue {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem('auth');
    if (stored) {
      const parsed = JSON.parse(stored);
      setUser(parsed.user);
      setToken(parsed.access);
      api.defaults.headers.common.Authorization = `Bearer ${parsed.access}`;
    }
  }, []);

  const login = async (username: string, password: string) => {
    const res = await api.post('/auth/token/', { username, password });
    const payload = res.data;
    setUser(payload.user);
    setToken(payload.access);
    api.defaults.headers.common.Authorization = `Bearer ${payload.access}`;
    localStorage.setItem('auth', JSON.stringify(payload));
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    delete api.defaults.headers.common.Authorization;
    localStorage.removeItem('auth');
  };

  const value = useMemo(() => ({ user, token, login, logout }), [user, token]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
};
