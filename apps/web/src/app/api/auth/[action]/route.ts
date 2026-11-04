import { NextRequest, NextResponse } from "next/server";

const backend = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const cookieName = "tevrox_refresh";

export async function POST(request: NextRequest, { params }: { params: Promise<{ action: string }> }) {
  const { action } = await params;
  const body = action === "refresh" || action === "logout"
    ? { refresh_token: request.cookies.get(cookieName)?.value }
    : await request.json();
  const endpoint = action === "logout" ? "logout" : action;
  const response = await fetch(`${backend}/api/v1/auth/${endpoint}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  if (response.status === 204) { const result = new NextResponse(null, { status: 204 }); result.cookies.delete(cookieName); return result; }
  const data = await response.json();
  const refreshToken = data.refresh_token as string | undefined;
  if (response.ok && (action === "login" || action === "signup" || action === "refresh")) {
    delete data.refresh_token;
  }
  const result = NextResponse.json(data, { status: response.status });
  if (response.ok && refreshToken && (action === "login" || action === "signup" || action === "refresh")) result.cookies.set(cookieName, refreshToken, { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", path: "/api/auth", maxAge: 60 * 60 * 24 * 30 });
  return result;
}
