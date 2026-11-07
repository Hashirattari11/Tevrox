"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

export type TevroxUser = {
  id: string;
  email: string;
  role: "user" | "admin";
  is_active?: boolean;
  is_email_verified?: boolean;
  last_login_at?: string | null;
};

type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: TevroxUser;
};

type AuthContextValue = {
  user: TevroxUser | null;
  accessToken: string | null;
  loading: boolean;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
  authFetch: (path: string, init?: RequestInit) => Promise<Response>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8010";

const KEYS = {
  accessToken: "tevrox_access_token",
  refreshToken: "tevrox_refresh_token",
  user: "tevrox_user",
} as const;

function readStoredUser(): TevroxUser | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(KEYS.user);
    return raw ? (JSON.parse(raw) as TevroxUser) : null;
  } catch {
    return null;
  }
}

function readStoredAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(KEYS.accessToken);
}

function readStoredRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(KEYS.refreshToken);
}

async function parseTokenResponse(response: Response, fallback: string): Promise<TokenResponse> {
  const data = await response.json().catch(() => null);
  if (!response.ok || !data) {
    throw new Error(
      data?.error?.message ?? data?.error?.code ?? `${fallback} (${response.status})`
    );
  }
  return data as TokenResponse;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  // The server and the first client render must match. Reading localStorage
  // during the initial render (e.g. in a useState initializer) makes the
  // client tree differ from the server HTML and causes hydration errors.
  // Start from the same "no session" state on both sides and hydrate after
  // mount instead.
  const [user, setUser] = useState<TevroxUser | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      setUser(readStoredUser());
      setAccessToken(readStoredAccessToken());
      setLoading(false);
    }, 0);
    return () => window.clearTimeout(handle);
  }, []);

  const persistSession = useCallback((data: TokenResponse) => {
    window.localStorage.setItem(KEYS.accessToken, data.access_token);
    window.localStorage.setItem(KEYS.refreshToken, data.refresh_token);
    window.localStorage.setItem(KEYS.user, JSON.stringify(data.user));
    setAccessToken(data.access_token);
    setUser(data.user);
  }, []);

  const clearSession = useCallback(() => {
    window.localStorage.removeItem(KEYS.accessToken);
    window.localStorage.removeItem(KEYS.refreshToken);
    window.localStorage.removeItem(KEYS.user);
    setAccessToken(null);
    setUser(null);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await parseTokenResponse(response, "Login failed");
    persistSession(data);
  }, [persistSession]);

  const signup = useCallback(
    async (email: string, password: string, fullName: string) => {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, full_name: fullName }),
      });
      const data = await parseTokenResponse(response, "Could not create account");
      persistSession(data);
    },
    [persistSession]
  );

  const logout = useCallback(async () => {
    const refreshToken = readStoredRefreshToken();
    if (refreshToken) {
      try {
        await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      } catch {
        // Ignore network errors on logout; local session is still cleared.
      }
    }
    clearSession();
  }, [clearSession]);

  const authFetch = useCallback(
    async (path: string, init: RequestInit = {}) => {
      const token = accessToken ?? readStoredAccessToken();
      const headers = new Headers(init.headers);
      if (token) headers.set("Authorization", `Bearer ${token}`);
      if (!headers.has("Content-Type") && init.body) {
        headers.set("Content-Type", "application/json");
      }
      const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
      if (response.status === 401) {
        clearSession();
      }
      return response;
    },
    [accessToken, clearSession]
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      accessToken,
      loading,
      isAdmin: user?.role === "admin",
      login,
      signup,
      logout,
      authFetch,
    }),
    [user, accessToken, loading, login, signup, logout, authFetch]
  );

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
