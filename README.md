# Tevrox

Tevrox is a skincare and nutrition platform foundation. Web, Android, and iOS use separate clients over one versioned FastAPI API and one PostgreSQL database hosted on Supabase. This milestone provides status screens, schema, and service boundaries only; it does not implement authentication, product discovery, or AI workflows.

## Requirements

- Git, Node.js current LTS, pnpm 10, Python 3.11+, and uv
- A Supabase PostgreSQL project for real database health and migrations
- Android Studio emulator, Xcode simulator (macOS), or Expo Go for mobile

## First-time setup

```sh
pnpm install
uv sync --project backend --dev
cp backend/.env.example .env
cp apps/web/.env.example apps/web/.env.local
cp apps/mobile/.env.example apps/mobile/.env
```

Set `DATABASE_URL` in root `.env` to your Supabase connection string. Use the direct database connection or transaction pooler with the correct driver/port. Never commit `.env` files. The sample URLs and key values are placeholders.

## Run the apps

Start each in its own terminal from the repository root:

```sh
pnpm dev:backend
pnpm dev:web
pnpm dev:mobile
```

The web status page is at http://localhost:3000 and the API at http://localhost:8000/api/v1/health. Android emulator can reach the host as `10.0.2.2`; the mobile fallback is configured accordingly. For iOS simulator use `localhost`. For a physical device, set `EXPO_PUBLIC_API_URL` to `http://<computer-LAN-IP>:8000`, keep both devices on the same network, and allow the backend port through the host firewall. CORS origins are for browser clients; Expo native networking does not enforce browser CORS.

## Environment variables

| Variable | Used by | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | backend | PostgreSQL connection string (`postgresql+psycopg://...`) |
| `SUPABASE_URL` | backend | Supabase project URL |
| `SUPABASE_ANON_KEY` | backend | Public Supabase key, reserved for future integrations |
| `SUPABASE_SERVICE_ROLE_KEY` | backend | Server-only service key; never expose to clients |
| `JWT_SECRET` | backend | Secret to configure before JWT work in Week 2–3 |
| `ALLOWED_ORIGINS` | backend | Comma-separated browser origins |
| `ENVIRONMENT` | backend | Environment name (development by default) |
| `AI_PROVIDER_API_KEY` | backend | Empty until an AI provider is selected |
| `PRODUCT_API_KEY` | backend | Empty until a product data provider is selected |
| `NEXT_PUBLIC_API_URL` | web | API origin, normally `http://localhost:8000` |
| `EXPO_PUBLIC_API_URL` | mobile | API origin; physical devices must use the computer's LAN IP |

## Database and backend

```sh
pnpm migrate
pnpm test:backend
pnpm lint
pnpm openapi
```

The backend-specific commands are:

```sh
uv run --project backend uvicorn app.main:app --app-dir backend --reload
uv run --project backend pytest backend/tests
uv run --project backend alembic -c backend/alembic.ini upgrade head
uv run --project backend alembic -c backend/alembic.ini downgrade base
uv run --project backend ruff check backend
```

## Structure

```text
apps/web/       Next.js App Router status client
apps/mobile/    Expo Router status client
backend/        FastAPI, SQLAlchemy models, Alembic, tests
docs/           Architecture, schema, API conventions, OpenAPI contract
```

## Troubleshooting

- `database: unreachable`: check the root `.env` `DATABASE_URL`, Supabase network access, and SSL settings from the Supabase connection panel.
- Web cannot reach the API: run the backend and set `NEXT_PUBLIC_API_URL`; add the web origin to `ALLOWED_ORIGINS`.
- Device cannot reach the API: `localhost` points at the device. Use the development computer's LAN IP and ensure port 8000 is reachable.
- Migration connection fails: verify the URL and that the Supabase database accepts connections from your network. Migrations need a direct connection or session pooler, not the transaction pooler for all DDL workflows.
- iOS simulator requires macOS/Xcode; Android emulator requires Android Studio and an installed emulator image.

## Dependencies

- Backend runtime: FastAPI (HTTP API), Uvicorn (ASGI server), SQLAlchemy (ORM), Alembic (migrations), psycopg (PostgreSQL driver), Pydantic Settings (environment configuration).
- Backend development: pytest and HTTPX (API tests), Ruff (lint/format).
- Web runtime: Next.js and React; Tailwind CSS for minimal styling. TypeScript, ESLint, and Next ESLint config support strict checking and linting.
- Mobile runtime: Expo, Expo Router, React Native, Expo Metro runtime, linking, constants, status bar, safe-area and screens packages. TypeScript and Expo ESLint config support type safety and linting.

## Week 2 authentication starting points

Decide account lifecycle and email verification, choose password hashing and JWT expiry/refresh policy, implement registration/login schemas and services, add authorization dependencies/role checks, add migration for verification/refresh state if needed, and cover token expiry, invalid credentials, and access control with tests. Keep provider secrets server-side.
