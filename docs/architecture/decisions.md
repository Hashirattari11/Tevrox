# Architecture decisions

- **One shared API, separate clients:** Keeps domain rules and data access centralized while allowing web and native experiences to evolve independently.
- **Supabase PostgreSQL as persistence:** Use standard PostgreSQL through SQLAlchemy; Supabase-specific client SDKs are not required for database access.
- **MongoDB as a secondary document service:** Keep PostgreSQL for relational records and initialize an async PyMongo client. MongoDB connection health is exposed now; collection ownership and document schemas will be added with the feature that needs them.
- **Custom authentication:** FastAPI owns Argon2 password hashes, short-lived HS256 JWT access tokens, and hashed rotating refresh tokens; Supabase only hosts PostgreSQL.
- **Phase 2 authentication:** Signup, login, refresh, logout, change-password, profile management, and role-based authorization are implemented in the FastAPI backend. Access tokens are 15-minute JWTs; refresh tokens are hashed opaque strings with rotation and reuse detection. Web stores tokens in `localStorage`; mobile stores them in Expo SecureStore. Redis-backed rate limits, email verification, reset emails, social login, and 2FA are deferred.
- **Phase 3 product database:** PostgreSQL handles products, ingredients, brands, aliases, sources, and user submissions. External product data comes from **Open Beauty Facts as a provisional provider** behind an abstract provider interface (`ProductProvider`) with a validated DTO (`ExternalProductDTO`). The provider choice is provisional and should be revisited before public launch; a paid/licensed catalogue such as Open Food Facts alternatives or PureDb can be swapped in without touching the application services.
- **External data is untrusted, always:** Products from Open Beauty Facts or from users are stored as `unverified` until an administrator verifies them. External images are not accepted unless they are http(s) URLs. Ingredient parsing never silently drops entries; unknown ingredients are created as `unreviewed` for admin resolution. Unverified products must not be displayed as verified in any client.
- **Barcode resolution order:** internal database first, then the external provider, storing the external product as `unverified`. If the provider returns a malformed or incomplete record, or is unreachable/timed out, the API returns `404 PRODUCT_NOT_FOUND` with a submission hint rather than exposing partial data or failing with a 500.
- **Verification workflow:** Admins review the queue, verify or reject products (with optional reasons), merge duplicate ingredients, and edit ingredients/aliases. Every admin catalogue write creates an `admin_audit_logs` row with before/after summaries and the actor id.
- **Search strategy:** Product and ingredient search uses parameterized ILIKE queries. PostgreSQL gains `pg_trgm` GIN indexes in migration `0003_phase3_catalog`; SQLite development/tests scan. This is a deliberate provisional choice: if the product catalogue grows past low tens of thousands of rows, evaluate full-text search or a dedicated search service.
- **Pagination contract:** Catalogue collection endpoints paginate with `limit` (default 20, max 100) and return `{ items, total, limit, next_cursor, verified_only }`. `next_cursor` is an opaque base64 offset cursor. The admin list endpoints use `offset` because they exist for management screens rather than public discovery.
- **Provider caching and rate limits:** Provider responses are cached in memory with a 1h TTL; production should replace this with Redis. User submissions are rate-limited (5 per 10 minutes, configurable) and de-duplicated by unique barcode. Both limits are per-process and therefore only approximate in multi-worker deployments; a shared Redis counter is required before horizontal scaling.
- **Seed data policy:** `backend/scripts/seed_phase3.py` inserts 51 development ingredients plus 10 sample products, all prefixed `[Development seed]` and linked to a `development_seed` source. It is idempotent and refuses to run in production without an explicit flag. It must never be used as production catalogue data.
- **Token storage decision:** Web (current) uses `localStorage` for access/refresh tokens because the web app calls the API directly. A future hardening step can move to same-origin httpOnly cookies with a BFF proxy. Mobile uses Expo SecureStore.
- **Database health is informational:** Health returns HTTP 200 with `database: unreachable` if the DB cannot be contacted, so deployment checks can distinguish process health from dependency health.
- **Portable UUID + JSONB schema:** UUIDs are generated in the application; structured analysis and preferences use PostgreSQL JSONB. Alembic migrations are explicit `op.` operations, including the Phase 3 follow-up revision.
- **OpenAPI generated from FastAPI:** `pnpm openapi` refreshes the committed API contract. Typed clients can later be generated with `openapi-typescript` and a small fetch wrapper.
- **Phase 3 catalogue API shape:** Endpoints are grouped under `/api/v1/products`, `/api/v1/brands`, `/api/v1/ingredients`, and `/api/v1/admin/*`. Catalogue reads require an authenticated user; catalogue writes are admin-only and audited. OpenAPI is the canonical contract; see `docs/api/products.md`.
- **Expo SDK alignment:** Mobile uses Expo SDK 58 with its matching React Native and React versions; the `doctor` script checks package compatibility.

- **Rules engine:** Deterministic Python rules engine with versioned rules stored in data files (Python dicts/YAML) so they can be reviewed by non-developers. Each rule has an id, description, severity, and documented source note. The rules engine produces findings that are merged into the AI validation layer. This is a deliberate choice: rules are auditable and explainable, unlike pure LLM output.

- **Prompt versioning:** System prompts live in versioned files under `backend/app/modules/analysis/prompts/`. Every analysis row stores `prompt_version` and `rules_version` so results are reproducible and auditable.

- **No personal data to LLM:** Only product name, ingredients, reference data, rule findings, skin_type, and skin_concerns are sent. Email, name, user id are never included. Prompts and model outputs are not logged in full.

- **Fallback behavior:** If LLM validation fails twice, a rules-only fallback report is returned with `model_used="fallback"` — never a raw 500.

- **Caching:** Analyses are cached by `input_hash` (product ingredients + reference versions + skin profile + prompt_version + rules_version). Cached results don't count toward daily limits.

- **Cost controls:** Per-user daily limit (default 20) returning `ANALYSIS_LIMIT_REACHED`, plus per-minute rate limiting. Admin stats endpoint for cost monitoring.

- **Provider choice:** `AI_PROVIDER` selects the provider. `FakeAIProvider`
  (deterministic, no network) is the default for tests and local dev without a
  key. `AnthropicProvider` uses the official anthropic SDK. `OpenRouterProvider`
  calls OpenRouter's OpenAI-compatible chat-completions endpoint with a **free**
  model (`google/gemma-4-31b-it:free` by default, verified against OpenRouter's
  live model list). Free models still need `OPENROUTER_API_KEY`; the provider
  tolerates JSON wrapped in markdown fences and walks a retry/backoff loop.

- **Expert review needed:** All rules and ingredient reference data (function_tags, safety_notes, irritation_potential) must be reviewed by a qualified person before public launch; seed data is marked development-only.

## Pending decisions / known limitations

- Final product data provider (Open Beauty Facts is provisional).
- Shared Redis cache and rate limiter for multi-worker production.
- Web token storage hardening (httpOnly + BFF) versus direct API calls.
- Email verification, password reset, social login, and 2FA for account security.
- Full-text/trigram search upgrades beyond ILIKE for larger catalogues.
- Admin dashboard UX details; region rules for usable cosmetics data.
