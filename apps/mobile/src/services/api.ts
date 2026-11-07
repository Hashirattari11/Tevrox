import { apiBaseUrl } from "@/constants/config";
import type { Health } from "@/types/health";
import { tokens } from "@/services/tokenStorage";

type AuthResult = { access_token: string; refresh_token: string; user: { id:string; email:string; role:string } };
export async function auth(path: "login" | "signup", body: Record<string,string>): Promise<AuthResult> { const r=await fetch(`${apiBaseUrl}/api/v1/auth/${path}`,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(body)}); const x=await r.json(); if(!r.ok) throw new Error(x.error?.message??"Authentication failed"); await tokens.set(x.access_token,x.refresh_token); return x; }
export async function authorized(path:string, init:RequestInit={}) { let t=await tokens.get(); let r=await fetch(`${apiBaseUrl}${path}`,{...init,headers:{...init.headers,authorization:`Bearer ${t.access}`}}); if(r.status===401 && t.refresh){ const rr=await fetch(`${apiBaseUrl}/api/v1/auth/refresh`,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({refresh_token:t.refresh})}); if(rr.ok){const x=await rr.json(); await tokens.set(x.access_token,x.refresh_token); r=await fetch(`${apiBaseUrl}${path}`,{...init,headers:{...init.headers,authorization:`Bearer ${x.access_token}`}});} else await tokens.clear(); } return r; }

export async function getHealth(): Promise<Health> {
  const response = await fetch(`${apiBaseUrl}/api/v1/health`);
  if (!response.ok) throw new Error(`Backend returned HTTP ${response.status}`);
  return response.json() as Promise<Health>;
}
