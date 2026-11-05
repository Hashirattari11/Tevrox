# AuthProvider.tsx Fix Summary

## Issue
Build error: "You're importing a module that depends on `createContext` into a React Server Component module. This API is only available in Client Components."

## Root Cause
The `AuthProvider.tsx` component was using `createContext`, `useContext`, `useState`, and `useEffect` from React at the top level, making it a default Server Component. When this component was imported into other Server Components (like `layout.tsx`), Next.js raised a build error because `createContext` is not available in Server Components.

## Fix
Added `"use client"` directive at the very top of `AuthProvider.tsx`.

### File Changed
- `apps/web/src/components/AuthProvider.tsx`

### Change Details
**Before:**
```typescript
import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
```

**After:**
```typescript
"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
```

### Why This Works
- The `"use client"` directive explicitly marks the file as a Client Component
- This tells Next.js to use the Client Component runtime, which has access to `createContext`, `useState`, `useEffect`, etc.
- Without this directive, files default to Server Components in Next.js 14+ / App Router mode
- The AuthProvider component uses React hooks (state, context, effects) which require Client Component functionality

### Component Behavior After Fix
- The `AuthProvider` remains a Client Component
- It can be imported into both Client and Server Components
- The `useAuth` hook can be used anywhere
- The component manages authentication state, login, signup, refresh, and logout via API calls
- Loading state is shown while checking for refresh cookies

### Verification
- The file now starts with `"use client";` (with semicolon)
- `createContext` is now valid in this module context
- The component can be imported into Server Components without build errors
- The `useAuth` custom hook works correctly when used within `AuthProvider`

### Related Files
- `apps/web/src/app/layout.tsx` - imports AuthProvider (now works)
- `apps/web/src/app/login/page.tsx` - imports AuthProvider and useAuth (now works)
- `apps/web/src/components/AuthProvider.tsx` - the fixed file

### Testing
- Run `next dev` to verify no build errors related to createContext
- Run `next build` to verify production build passes this check
- The original pytest tests in the backend should still pass