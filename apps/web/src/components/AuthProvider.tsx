"use client";
import { createContext, useContext, useEffect, useState } from "react";

type User = { id: string; email: string; role: string };
type Auth = { user: User | null; accessToken: string | null; loading: boolean; login: (email: string, password: string) => Promise<void>; logout: () => Promise<void> };
const Context = createContext<Auth | null>(null);
export const useAuth = () => { const value = useContext(Context); if (!value) throw new Error("AuthProvider missing"); return value; };
async function refresh(): Promise<{ access_token: string; user: User } | null> { const r = await fetch("/api/auth/refresh", { method: "POST" }); return r.ok ? r.json() : null; }
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null); const [accessToken, setAccessToken] = useState<string | null>(null); const [loading, setLoading] = useState(true);
  useEffect(() => { refresh().then((x) => { if (x) { setUser(x.user); setAccessToken(x.access_token); } }).finally(() => setLoading(false)); }, []);
  async function login(email: string, password: string) { const r = await fetch("/api/auth/login", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ email, password }) }); const x = await r.json(); if (!r.ok) throw new Error(x.error?.message ?? "Login failed"); setUser(x.user); setAccessToken(x.access_token); }
  async function logout() { await fetch("/api/auth/logout", { method: "POST" }); setUser(null); setAccessToken(null); }
  return <Context.Provider value={{ user, accessToken, loading, login, logout }}>{children}</Context.Provider>;
}
