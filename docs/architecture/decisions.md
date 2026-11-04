# Architecture decisions

- **One shared API, separate clients:** Keeps domain rules and data access centralized while allowing web and native experiences to evolve independently.
- **Supabase PostgreSQL as persistence:** Use standard PostgreSQL through SQLAlchemy; Supabase-specific client SDKs are not required for database access.
- **Database health is informational:** Health returns HTTP 200 with `database: unreachable` if the DB cannot be contacted, so deployment checks can distinguish process health from dependency health.
- **Portable UUID + JSONB schema:** UUIDs are generated in the application; structured analysis and preferences use PostgreSQL JSONB.
- **Placeholder APIs only:** No authentication, analysis, catalog integration, or product/routine behavior ships in this foundation.
- **OpenAPI generated from FastAPI:** `pnpm openapi` refreshes the committed API contract. Typed clients can later be generated with `openapi-typescript` and a small fetch wrapper.
- **Expo SDK alignment:** Mobile uses Expo SDK 58 with its matching React Native 0.88 and React 19.3 versions; the `doctor` script checks Expo package compatibility.
- **Migration portability limitation:** The initial revision calls `Base.metadata.create_all/drop_all` to keep one source of schema truth at foundation stage. Before schema evolution in production, replace it with explicit Alembic operations and review generated migrations.
