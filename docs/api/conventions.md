# API conventions

- Prefix all routes with `/api/v1`; breaking changes require a new version prefix.
- Use JSON request/response bodies and conventional HTTP status codes.
- Errors have the shape `{ "error": { "code": "...", "message": "...", "details": null } }`.
- Authentication is not implemented. Week 2–3 will add bearer JWT access tokens, refresh policy, and role-based authorization; secrets remain backend-only.
- Future collection endpoints should paginate with `limit` (default 20, maximum 100) and opaque `cursor`, returning `{ "items": [], "next_cursor": null }`.
- OpenAPI is served at `/openapi.json` and checked in at `docs/api/openapi.json`. Regenerate with `pnpm openapi`. For typed clients, generate TypeScript definitions from the spec with `openapi-typescript`, then use the existing web/mobile fetch wrappers; do not duplicate schemas by hand.
