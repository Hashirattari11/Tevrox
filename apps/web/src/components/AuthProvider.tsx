"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";

type User = {
  id: string;
  email: string;
  role: "user" | "admin";
  is_active?: boolean;
  is_email_verified?: boolean;
  last_login_at?: string | null;
};

type AuthContextValue = {
  user: User | null;
  accessToken: string | null;
  loading: boolean;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
  authFetch: (path: string, init?: RequestInit) => Promise<Response>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8010";

const KEYS = {
  accessToken: "tevrox_access_token",
  refreshToken: "tevrox_refresh_token",
  user: "tevrox_user",
};

function readStoredUser(): User | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(KEYS.user);
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Restore session on mount
  useEffect(() => {
    const storedAccess = window.localStorage.getItem(KEYS.accessToken);
    const storedUser = readStoredUser();
    if (storedAccess && storedUser) {
      setAccessToken(storedAccess);
      setUser(storedUser);
    }
    setLoading(false);
  }, []);

  const persistSession = (data: { access_token: string; refresh_token: string; user: User }) => {
    window.localStorage.setItem(KEYS.accessToken, data.access_token);
    window.localStorage.setItem(KEYS.refreshToken, data.refresh_token);
    window.localStorage.setItem(KEYS.user, JSON.stringify(data.user));
    setAccessToken(data.access_token);
    setUser(data.user);
  };

  const clearSession = () => {
    window.localStorage.removeItem(KEYS.accessToken);
    window.localStorage.removeItem(KEYS.refreshToken);
    window.localStorage.removeItem(KEYS.user);
    setAccessToken(null);
    setUser(null);
  };

  const login = async (email: string, password: string) => {
    const response = await fetch(`${baseUrl}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data?.error?.message ?? "Login failed");
    persistSession(data);
  };

  const signup = async (email: string, password: string, fullName: string) => {
    const response = await fetch(`${baseUrl}/api/v1/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data?.error?.message ?? "Could not create account");
    persistSession(data);
  };

  const logout = async () => {
    const refreshToken = window.localStorage.getItem(KEYS.refreshToken);
    if (refreshToken) {
      try {
        await fetch(`${baseUrl}/api/v1/auth/logout`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      } catch {
        // ignore network errors on logout
      }
    }
    clearSession();
  };

  const authFetch = (path: string, init: RequestInit = {}) => {
    const token = accessToken ?? (typeof window !== "undefined" ? window.localStorage.getItem(KEYS.accessToken) : null);
    const headers = new Headers(init.headers);
    if (token) headers.set("Authorization", `Bearer ${token}`);
    if (!headers.has("Content-Type") && init.body) headers.set("Content-Type", "application/json");
    return fetch(`${baseUrl}${path}`, { ...init, headers });
  };

  if (loading) {
    return (
      <AuthContext.Provider
        value={{
          user,
          accessToken,
          loading,
          isAdmin: false,
          login,
          signup,
          logout,
          authFetch,
        }}
      >
        {children}
      </AuthContext.Provider>
    );
  }
}

export function useAuth(): AuthContextValue {
  const context = React.useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
