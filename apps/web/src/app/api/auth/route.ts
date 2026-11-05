import { NextResponse } from "next/server"

export const dynamic = "force-dynamic"
export const revalidate = 0

// --- Signup ---
export async function POST(request: Request) {
  const body = await request.json()
  const { email, password, fullName } = body

  // Call FastAPI backend
  const backendRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, fullName }),
    credentials: "include", // forward cookies if any
  })

  const data = await backendRes.json()

  if (!backendRes.ok) {
    return NextResponse.json({ error: data.error?.message || "Signup failed" }, { status: backendRes.status })
  }

  // Set httpOnly refresh cookie (BFF pattern)
  const refreshToken = data.refresh_token
  const maxAge = 60 * 60 * 24 * 30 // 30 days

  const response = NextResponse.json(
    { access_token: data.access_token, user: data.user },
    { status: 200 }
  )

  response.cookies.set("refresh_token", refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge,
  })

  // Access token is NOT stored in cookie; kept in memory by the client
  return response
}

// --- Login ---
export async function POST_login(request: Request) {
  const body = await request.json()
  const { email, password } = body

  const backendRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
    credentials: "include",
  })

  const data = await backendRes.json()

  if (!backendRes.ok) {
    return NextResponse.json({ error: data.error?.message || "Login failed" }, { status: backendRes.status })
  }

  // Set httpOnly refresh cookie
  const refreshToken = data.refresh_token
  const maxAge = 60 * 60 * 24 * 30 // 30 days

  const response = NextResponse.json(
    { access_token: data.access_token, user: data.user },
    { status: 200 }
  )

  response.cookies.set("refresh_token", refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge,
  })

  return response
}

// --- Refresh ---
export async function POST_refresh(request: Request) {
  const cookie = request.cookies.refresh_token
  if (!cookie) {
    return NextResponse.json({ error: "No refresh token found" }, { status: 401 })
  }

  const backendRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: cookie }),
    credentials: "include",
  })

  const data = await backendRes.json()

  if (!backendRes.ok) {
    // Revoke cookie on failure
    const response = NextResponse.json({ error: data.error?.message || "Refresh failed" }, { status: backendRes.status })
    response.cookies.set("refresh_token", "", { httpOnly: true, secure: false, sameSite: "lax", path: "/", maxAge: 0 })
    return response
  }

  // Set new httpOnly refresh cookie
  const refreshToken = data.refresh_token
  const maxAge = 60 * 60 * 24 * 30 // 30 days

  const response = NextResponse.json(
    { access_token: data.access_token, user: data.user },
    { status: 200 }
  )

  response.cookies.set("refresh_token", refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge,
  })

  return response
}

// --- Logout ---
export async function POST_logout(request: Request) {
  const cookie = request.cookies.refresh_token

  if (cookie) {
    // Call backend to revoke the token
    await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: cookie }),
      credentials: "include",
    })
  }

  // Clear the cookie
  const response = NextResponse.json({ success: true }, { status: 200 })
  response.cookies.set("refresh_token", "", {
    httpOnly: true,
    secure: false,
    sameSite: "lax",
    path: "/",
    maxAge: 0,
  })
  return response
}

// --- Logout All ---
export async function POST_logout_all(request: Request) {
  const cookie = request.cookies.refresh_token

  if (cookie) {
    await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/logout-all`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: cookie }),
      credentials: "include",
    })
  }

  const response = NextResponse.json({ success: true }, { status: 200 })
  response.cookies.set("refresh_token", "", {
    httpOnly: true,
    secure: false,
    sameSite: "lax",
    path: "/",
    maxAge: 0,
  })
  return response
}

// --- Get Current User (me) ---
export async function GET_me(request: Request) {
  const cookie = request.cookies.refresh_token

  if (!cookie) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 })
  }

  const backendRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/me`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${cookie}`, // access token in header
    },
    credentials: "include",
  })

  const data = await backendRes.json()

  if (!backendRes.ok) {
    return NextResponse.json({ error: data.error?.message || "Auth failed" }, { status: backendRes.status })
  }

  return NextResponse.json({ user: data.user }, { status: 200 })
}

// --- Change Password ---
export async function POST_change_password(request: Request) {
  const body = await request.json()
  const { currentPassword, newPassword } = body
  const cookie = request.cookies.refresh_token

  if (!cookie) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 })
  }

  const backendRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/change-password`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${cookie}`, // access token in header
    },
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    credentials: "include",
  })

  const data = await backendRes.json()

  if (!backendRes.ok) {
    return NextResponse.json({ error: data.error?.message || "Change password failed" }, { status: backendRes.status })
  }

  // Revoke all other refresh tokens after successful password change
  await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/logout-all`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: cookie }),
    credentials: "include",
  })

  return NextResponse.json({ success: true }, { status: 200 })
}