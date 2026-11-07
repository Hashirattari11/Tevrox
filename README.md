# Tevrox

Tevrox is a skincare and nutrition platform. Web, Android, and iOS use separate clients over one versioned FastAPI API, Supabase PostgreSQL for relational data, and a secondary MongoDB document service.

**Status:** Phase 3 (product and ingredient database, discovery, and admin review) is implemented. Phase 1 set up the foundation, Phase 2 added authentication and profiles, and Phase 3 added the shared catalogue, barcode scanning/lookup, product search, submissions, and admin review tooling. Authentication is required for catalogue routes; AI analysis, conflict detection, and routines remain planned.

## Requirements

- Git, Node.js current LTS, pnpm 12.6, Python 3.11+, and uv
- A Supabase PostgreSQL project for real database health and migrations
- A MongoDB deployment (Atlas or local) for MongoDB health reporting
- Docker Desktop with Compose if you want to run the local MongoDB service
- Android Studio emulator, Xcode simulator (macOS), or Expo Go for mobile

## First-time setup

```sh
pnpm install
uv sync --project backend --dev
cp backend/.env.example .env
cp apps/web/.env.example apps/web/.env.local
cp apps/mobile/.env.example apps/mobile/.env
```

Set `DATABASE_URL` in root `.env` to your Supabase connection string. The sample MongoDB URI and credentials are for local development only; `MONGODB_URL` must match the Compose credentials, or be replaced with your Atlas URI. Use the direct database connection or transaction pooler with the correct PostgreSQL driver/port. Never commit `.env` files.

## Run the apps

Start each in its own terminal from the repository root:

```sh
pnpm dev:backend
pnpm dev:web
pnpm dev:mobile
```

Start the local MongoDB service first with `pnpm mongo:up`. Its database files persist in the `mongo_data` Docker volume. Stop the service without deleting its data with `pnpm mongo:down`.

- Web: http://localhost:3000
- API: http://localhost:8010/api/v1/health
- API docs: http://localhost:8010/docs

The mobile client can reach the host as `10.0.2.2` on the Android emulator or `localhost` on the iOS simulator. For a physical device, set `EXPO_PUBLIC_API_URL` to `http://<computer-LAN-IP>:8010`, keep both devices on the same network, and allow port 8010 through the firewall. CORS origins are for browser clients; Expo native networking does not enforce browser CORS.

- Android emulator: start an emulator in Android Studio, then run `pnpm --filter @tevrox/mobile android`.
- iOS simulator: on macOS with Xcode installed, run `pnpm --filter @tevrox/mobile ios`.
- Physical device: run `pnpm dev:mobile`, open the project in Expo Go using the QR code, and set `EXPO_PUBLIC_API_URL` as noted above.

## Environment variables

| Variable | Used by | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | backend | PostgreSQL connection string (`postgresql+psycopg://...`) |
| `MONGODB_URL` | backend | MongoDB connection URI |
| `MONGODB_DATABASE` | backend | MongoDB database name (`tevrox` by default) |
| `MONGO_INITDB_ROOT_USERNAME` | local MongoDB | Compose-only local root username |
| `MONGO_INITDB_ROOT_PASSWORD` | local MongoDB | Compose-only local root password; change for shared machines |
| `SUPABASE_URL` | backend | Supabase project URL |
| `SUPABASE_ANON_KEY` | backend | Public Supabase key, reserved for future integrations |
| `SUPABASE_SERVICE_ROLE_KEY` | backend | Server-only service key; never expose to clients |
| `JWT_SECRET` | backend | Long random secret used to sign access tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | backend | Access JWT lifetime; default 15 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | backend | Refresh-token lifetime; default 30 |
| `ALLOWED_ORIGINS` | backend | Comma-separated browser origins |
| `ENVIRONMENT` | backend | Environment name (development by default) |
| `AI_PROVIDER_API_KEY` | backend | API key for the selected AI provider (Anthropic) |
| `AI_PROVIDER` | backend | `fake` (default), `anthropic`, or `openrouter` |
| `AI_MODEL` | backend | Model name, e.g. `claude-3-haiku-20240307` |
| `AI_MAX_TOKENS` | backend | Max tokens per analysis; default 1500 |
| `AI_TIMEOUT_SECONDS` | backend | Provider timeout; default 30.0 |
| `OPENROUTER_API_KEY` | backend | OpenRouter API key (only for `AI_PROVIDER=openrouter`) |
| `OPENROUTER_MODEL` | backend | Free OpenRouter model; default `nvidia/nemotron-3-ultra-550b-a55b:free` |
| `OPENROUTER_FALLBACK_MODELS` | backend | Comma-separated free models tried when the primary is rate-limited |
| `OPENROUTER_TIMEOUT_SECONDS` | backend | OpenRouter request timeout; default 60.0 |
| `ANALYSIS_DAILY_LIMIT` | backend | Per-user daily analysis limit; default 20 |
| `PRODUCT_API_KEY` | backend | Reserved for future providers; the default Open Beauty Facts integration needs no key |
| `OPEN_BEAUTY_FACTS_BASE_URL` | backend | Base URL for the provisional Open Beauty Facts provider |
| `PRODUCT_PROVIDER_TIMEOUT_SECONDS` | backend | External provider timeout; default 8.0 |
| `PRODUCT_PROVIDER_CACHE_TTL_SECONDS` | backend | In-memory cache TTL for provider responses; default 3600 |
| `PRODUCT_SUBMISSION_RATE_LIMIT` | backend | Max user product submissions per window; default 5 |
| `PRODUCT_SUBMISSION_RATE_WINDOW_SECONDS` | backend | Rate-limit window; default 600 |
| `PRODUCT_USER_AGENT` | backend | User-Agent sent to the external provider |
| `NEXT_PUBLIC_API_URL` | web | API origin, normally `http://localhost:8010` |
| `EXPO_PUBLIC_API_URL` | mobile | API origin; physical devices must use the computer's LAN IP |

## Database and backend

```sh
pnpm migrate
pnpm test:backend
pnpm lint
pnpm openapi
pnpm seed:phase3   # idempotent development seed (51 ingredients, 10 sample products)
```

Backend-specific commands:

```sh
uv run --project backend uvicorn app.main:app --app-dir backend --reload
uv run --project backend pytest backend/tests
uv run --project backend alembic -c backend/alembic.ini upgrade head
uv run --project backend alembic -c backend/alembic.ini downgrade base
uv run --project backend ruff check backend
```

Run with the fake AI provider (default, no API key needed):

```sh
# Backend uses AI_PROVIDER=fake by default; no network calls are made
uv run --project backend uvicorn app.main:app --app-dir backend --reload

# Run all backend tests (including 14 analysis tests)
uv run --project backend pytest backend/tests --cov=app --cov-report=term-missing
```

Run with Anthropic (requires API key):

```sh
# Set in .env:
# AI_PROVIDER=anthropic
# AI_PROVIDER_API_KEY=sk-ant-...
# AI_MODEL=claude-3-haiku-20240307
uv run --project backend uvicorn app.main:app --app-dir backend --reload
```

Run with OpenRouter (free model, requires a free OpenRouter key):

```sh
# Set in .env:
# AI_PROVIDER=openrouter
# OPENROUTER_API_KEY=sk-or-v1-...
# OPENROUTER_MODEL=google/gemma-4-31b-it:free
uv run --project backend uvicorn app.main:app --app-dir backend --reload
```

The development seed is explicit opt-in and safe to re-run. Seeded rows are prefixed with `[Development seed]` and the script refuses to run against `ENVIRONMENT=production` without `--i-know-what-i-am-doing`.

## Testing

```sh
cd backend
.venv/Scripts/python.exe -m pytest tests --cov=app --cov-report=term-missing
```

The suite covers ingredient normalization and parsing, search/filter/pagination, barcode lookup (internal DB, external provider, timeout, not found, malformed payloads), submissions (dedupe, rate limiting), admin route enforcement (403 for non-admins), verify/reject, audit logs, ingredient merges, and the full AI analysis pipeline (pipeline happy path, no-ingredients error, cache hit, skin-profile hash change, unverified flag, prompt injection, banned phrases, retry/fallback, provider timeout/429, daily limit, owner-only access, delete, pagination). It never calls the network: external provider calls are mocked.

## Structure

```text
apps/web/       Next.js App Router web client
apps/mobile/    Expo Router mobile client
backend/        FastAPI, SQLAlchemy models, Alembic, tests
backend/scripts/  Seed and admin tooling
compose.yaml    Local MongoDB service for development
docs/           Architecture, schema, API conventions and contract
```

## Authentication and roles

- Signup/login return a bearer access token and a rotating refresh token.
- Signup/login endpoints: `POST /api/v1/auth/signup` and `POST /api/v1/auth/login`; payloads use `email`, `password`, and `full_name`.
- Catalogue routes require `Authorization: Bearer <access token>`.
- Admin routes require the `admin` role and return `403` for regular users.
- Web stores tokens in `localStorage`; mobile uses Expo SecureStore. All external catalogue data, whether from submissions or Open Beauty Facts, is stored as `unverified` and must not be displayed as verified until an admin verifies it.

Create the first administrator from the CLI:

```sh
uv run --project backend python backend/scripts/create_admin.py admin@example.com "strong-password"
```

## Troubleshooting

- `database: unreachable`: check the root `.env` `DATABASE_URL`, Supabase network access, and SSL settings from the Supabase connection panel.
- `mongodb: unreachable`: check `MONGODB_URL`, Atlas IP access rules or local MongoDB service availability, and database credentials.
- Web cannot reach the API: run the backend, set `NEXT_PUBLIC_API_URL`, and add the web origin to `ALLOWED_ORIGINS`.
- Device cannot reach the API: `localhost` points at the device. Use the development computer's LAN IP.
- Migration connection fails: verify the URL and that the Supabase database accepts connections from your network. Migrations need a direct connection or session pooler.
- Seed/migration errors on SQLite: use the checked-in Alembic revisions; `upgrade head` / `downgrade -1` are tested for the Phase 3 migration.
- iOS simulator requires macOS/Xcode; Android emulator requires Android Studio and an installed emulator image.

## Dependencies

- Backend runtime: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `alembic`, `psycopg[binary]`, `pymongo`, `pydantic-settings`, `python-multipart` if required by future form routes.
- Backend development: `pytest`, `pytest-cov`, `httpx`, `ruff`.
- Web runtime: `next`, `react`, `react-dom`, `tailwindcss`, `@tailwindcss/postcss`, `typescript`. Client-side fetching uses small typed wrappers under `src/services`.
- Mobile runtime: `expo`, `expo-router`, `expo-camera`, `react-native`, `react`, `react-dom`, `@react-native/metro-config`.

## Next steps (Week 6+)

AI analysis of products and ingredients, conflict detection, routines, nutrition integration, and the full admin dashboard are planned. Suggested Week 6 work is listed in [docs/architecture/decisions.md](docs/architecture/decisions.md) and the project plan.
