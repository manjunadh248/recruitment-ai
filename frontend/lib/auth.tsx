"use client";

/**
 * ═══════════════════════════════════════════════════════════
 * RecruitAI — Auth Context & Provider
 * ═══════════════════════════════════════════════════════════
 * React context for managing authentication state across the
 * application. Provides login, register, logout, and user
 * state with localStorage persistence.
 */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import {
  apiLogin,
  apiRegister,
  apiGetProfile,
  setTokens,
  clearTokens,
  getAccessToken,
  getStoredUser,
  setStoredUser,
  APIError,
  type UserData,
} from "@/lib/api";

// ─── Types ───────────────────────────────────────────────

interface AuthContextType {
  user: UserData | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

// ─── Context ─────────────────────────────────────────────

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ─── Provider ────────────────────────────────────────────

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Restore session on mount
  useEffect(() => {
    const token = getAccessToken();
    const storedUser = getStoredUser();

    if (token && storedUser) {
      setUser(storedUser);
      // Optionally refresh profile in background
      apiGetProfile()
        .then((freshUser) => {
          setUser(freshUser);
          setStoredUser(freshUser);
        })
        .catch(() => {
          // Token might be expired
          clearTokens();
          setUser(null);
        });
    }

    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const result = await apiLogin(email, password);
    setTokens(result.access_token, result.refresh_token);
    setStoredUser(result.user);
    setUser(result.user);
  }, []);

  const register = useCallback(
    async (name: string, email: string, password: string) => {
      const result = await apiRegister(name, email, password);
      setTokens(result.access_token, result.refresh_token);
      setStoredUser(result.user);
      setUser(result.user);
    },
    []
  );

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const freshUser = await apiGetProfile();
      setUser(freshUser);
      setStoredUser(freshUser);
    } catch {
      // Ignore refresh errors
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// ─── Hook ────────────────────────────────────────────────

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
