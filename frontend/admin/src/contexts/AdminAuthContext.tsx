import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import type { UserResponse } from "../types/api";
import * as api from "../services/api";

interface AdminAuthState {
  user: UserResponse | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AdminAuthContext = createContext<AdminAuthState | undefined>(undefined);

export function AdminAuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshProfile = useCallback(async () => {
    try {
      const profile = await api.getProfile();
      if (profile.role !== "admin") {
        throw new Error("Acesso negado: apenas administradores podem acessar este painel.");
      }
      setUser(profile);
    } catch (err) {
      setUser(null);
      localStorage.removeItem("admin_access_token");
      localStorage.removeItem("admin_refresh_token");
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("admin_access_token");
    if (token) {
      refreshProfile().finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [refreshProfile]);

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await api.login({ email, password });
    localStorage.setItem("admin_access_token", tokens.access_token);
    localStorage.setItem("admin_refresh_token", tokens.refresh_token);
    
    try {
      const profile = await api.getProfile();
      if (profile.role !== "admin") {
        throw new Error("Acesso negado: apenas administradores podem acessar este painel.");
      }
      setUser(profile);
    } catch (err) {
      localStorage.removeItem("admin_access_token");
      localStorage.removeItem("admin_refresh_token");
      throw err;
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("admin_access_token");
    localStorage.removeItem("admin_refresh_token");
    setUser(null);
  }, []);

  return (
    <AdminAuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AdminAuthContext.Provider>
  );
}

export function useAdminAuth() {
  const ctx = useContext(AdminAuthContext);
  if (!ctx) throw new Error("useAdminAuth must be used within AdminAuthProvider");
  return ctx;
}
