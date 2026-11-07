# Architecture overview

```mermaid
flowchart LR
  Web[Next.js Web] -->|HTTPS / JSON| API[FastAPI /api/v1]
  Mobile[Expo iOS and Android] -->|HTTPS / JSON| API
  API --> ORM[SQLAlchemy 2]
  ORM --> DB[(Supabase PostgreSQL)]
  API -->|Async PyMongo; future document workloads| Mongo[(MongoDB)]
  API -->|HTTPS / JSON| OBF[Open Beauty Facts (provisional)]
  Mobile -.->|expo-camera| Camera[Barcode scanner]
```

The clients are separate because web and native mobile have different navigation, rendering, and deployment needs. They share one API contract so validation and business rules remain centralized. Relational records use PostgreSQL through SQLAlchemy; MongoDB is configured as a secondary document service for future unstructured workloads. Both are reported by the health endpoint. Request flow is client → versioned FastAPI router → service layer → PostgreSQL and, where needed, MongoDB. Phase 3 adds the catalogue: product search, barcode resolution, product submissions, and admin review. Web and mobile expose the same catalogue journeys over the API.

## Decisions

- UUID identifiers and timezone-aware server timestamps are used throughout the relational schema.
- The same FastAPI API serves all clients; clients never connect to PostgreSQL directly.
- The health route degrades gracefully and reports database reachability instead of failing the whole endpoint.
- Phase 1/2 deliver the foundation, schema, and bearer-token authentication with role-based authorization.
- The catalogue provider is an abstract interface; Open Beauty Facts is an unverified-by-default provisional integration. No credentials are needed to run without it.
- See [decisions](decisions.md) and [database schema](../database/schema.md).
