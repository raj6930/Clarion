/**
 * Auth Context
 * Manages JWT authentication state, role detection, and view mode toggle.
 * Phase 2: Real JWT auth with in-memory backend. Phase 3: PostgreSQL.
 */
import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { login as apiLogin, register as apiRegister, logout as apiLogout, getMe, type AuthUser } from '@/services/auth';
import { loadTokens, getAccessToken, clearTokens } from '@/services/api';

type ViewMode = 'team' | 'account';

interface AuthContextType {
  user: AuthUser | null;
  loading: boolean;
  error: string | null;
  viewMode: ViewMode;
  setViewMode: (mode: ViewMode) => void;
  isManager: boolean;
  isCSM: boolean;
  isAdmin: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string, domain: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null, loading: true, error: null,
  viewMode: 'team', setViewMode: () => {},
  isManager: false, isCSM: false, isAdmin: false, isAuthenticated: false,
  login: async () => {}, register: async () => {}, logout: async () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('team');

  // Hydrate from stored token on mount
  useEffect(() => {
    loadTokens();
    if (getAccessToken()) {
      getMe()
        .then(setUser)
        .catch(() => { clearTokens(); })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setError(null);
    try {
      const u = await apiLogin(email, password);
      setUser(u);
    } catch (e: any) {
      setError(e.message || 'Login failed');
      throw e;
    }
  }, []);

  const register = useCallback(async (email: string, password: string, name: string, domain: string) => {
    setError(null);
    try {
      const u = await apiRegister(email, password, name, domain);
      setUser(u);
    } catch (e: any) {
      setError(e.message || 'Registration failed');
      throw e;
    }
  }, []);

  const logout = useCallback(async () => {
    await apiLogout();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{
      user, loading, error, viewMode, setViewMode,
      isManager: user?.role === 'manager' || user?.role === 'admin',
      isCSM: user?.role === 'csm',
      isAdmin: user?.role === 'admin',
      isAuthenticated: !!user,
      login, register, logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
