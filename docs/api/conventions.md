# API conventions

- Prefix all routes with `/api/v1`; breaking changes require a new version prefix.
- Use JSON request/response bodies and conventional HTTP status codes.
- `GET /api/v1/health` reports API status plus PostgreSQL (`database`) and MongoDB (`mongodb`) reachability; an unavailable database is reported without making the health route fail.
- Errors have the shape `{ "error": { "code": "...", "message": "...", "details": ... } }`. Structured client-facing codes used by the catalogue in Phase 3 include `INVALID_BARCODE`, `PRODUCT_NOT_FOUND` (with a submission `hint`), `PRODUCT_ALREADY_EXISTS`, `INVALID_CURSOR`, `RATE_LIMITED`, `AUTH_FORBIDDEN`, `AUTH_TOKEN_INVALID`, and `AUTH_INVALID_CREDENTIALS`.
- Authentication uses bearer access tokens (15-minute JWTs). Send `Authorization: Bearer <token>`. Refresh tokens are opaque, hashed at rest, and rotate on use.
- Catalogue read endpoints require authentication. Catalogue write endpoints require the `admin` role and return `403` with code `AUTH_FORBIDDEN` for regular users.
- Collection endpoints paginate with `limit` (default 20, maximum 100). Public discovery endpoints return `next_cursor` (base64 offset, opaque); admin list endpoints accept `offset` and are intended for management screens.
- The Open Beauty Facts product provider is queried only after the internal database misses. External data is stored as `unverified` and must never be rendered as verified.
- OpenAPI is served at `/openapi.json` and checked in at `docs/api/openapi.json`. Regenerate with `pnpm openapi`. For typed clients, generate TypeScript definitions from the spec with `openapi-typescript`, then use the existing web/mobile fetch wrappers; do not duplicate schemas by hand.
