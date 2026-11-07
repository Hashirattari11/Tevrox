# Catalogue API (Phase 3)

The catalogue API under `/api/v1` backs product discovery, barcode resolution, admin review, and ingredient management. It is the same contract web and mobile clients consume. Catalogue **reads require authentication**; **writes are admin-only** and audited.

## Authentication

All catalogue endpoints require a bearer access token:

```
Authorization: Bearer <access-token>
```

Obtain tokens with:

```
POST /api/v1/auth/signup
{"email":"user@example.com","password":"password123","full_name":"Test User"}

POST /api/v1/auth/login
{"email":"user@example.com","password":"password123"}
```

Tokens expire after 15 minutes by default. Admin routes return `403` with code `AUTH_FORBIDDEN` for non-admin users.

## Products

### `GET /api/v1/products`

Search the catalogue. Query parameters:

| Parameter | Type | Default | Notes |
| --- | --- | --- | --- |
| `q` | string | — | Free-text match on product name or brand name |
| `category` | string | — | One of `cleanser`, `toner`, `serum`, `moisturizer`, `sunscreen`, `mask`, `exfoliant`, `eye_care`, `treatment`, `other` |
| `brand` | string | — | Partial brand name match |
| `verified_only` | boolean | `true` | Set `false` to include unverified records (intended for admin/dev surfaces) |
| `limit` | int | `20` | 1–100 |
| `cursor` | string | — | Opaque cursor from the previous page |
| `offset` | int | — | Offset alternative for admin list UX (mutually usable with cursor) |

Response:

```json
{
  "items": [
    {
      "id": "…",
      "name": "Daily Renewal Serum",
      "barcode": "4006381000003",
      "category": "serum",
      "description": "[Development seed] Sample product for local and test environments.",
      "image_url": null,
      "verification_status": "verified",
      "brand": {"id": "…", "name": "Tevrox Development"},
      "source": {"id": "…", "name": "development_seed"},
      "ingredient_count": 7,
      "is_active": true
    }
  ],
  "total": 10,
  "limit": 20,
  "next_cursor": null,
  "verified_only": true
}
```

Errors: `400 INVALID_CURSOR`.

### `GET /api/v1/products/{product_id}`

Returns full product detail including ordered ingredients:

```json
{
  "id": "…",
  "name": "Daily Renewal Serum",
  "barcode": "4006381000003",
  "category": "serum",
  "description": "…",
  "verification_status": "verified",
  "brand": {"id": "…", "name": "Tevrox Development"},
  "source": {"id": "…", "name": "development_seed"},
  "ingredient_count": 7,
  "is_active": true,
  "verified_by": "…",
  "verified_at": "2026-…",
  "created_by": null,
  "ingredients_raw_text": "Aqua, Glycerin, …",
  "ingredients": [
    {
      "id": "…",
      "product_id": "…",
      "ingredient_id": "…",
      "name": "Aqua",
      "normalized_name": "aqua",
      "position": 0,
      "original_text": "Aqua",
      "concentration": null,
      "category_function": "solvent",
      "description": "[Development seed] Water."
    }
  ]
}
```

### `GET /api/v1/products/barcode/{code}`

Resolves a barcode with the internal-first / provider-second strategy:

1. **Internal database hit** → returns the product immediately.
2. **Open Beauty Facts hit** → product is saved as `unverified` and returned with `"source": {"name": "open_beauty_facts"}`.
3. **Not found / provider failure / malformed record** → `404`:

```json
{
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "Product not found in the Tevrox catalogue or the external provider.",
    "details": {
      "hint": "Use POST /api/v1/products/submissions (or the Add product screen) to submit this product for admin review."
    }
  }
}
```

Barcodes must contain 8–14 digits. Invalid input returns `400 INVALID_BARCODE`.

### `POST /api/v1/products/submissions`

User submission for review (rate-limited, barcode-deduplicated). Payload:

```json
{
  "name": "User Submitted Serum",
  "brand_name": "User Brand",
  "category": "serum",
  "barcode": "99990000",
  "ingredients_raw_text": "Aqua, Glycerin, Mystery Extract"
}
```

Rules:

- `name` and `ingredients_raw_text` cannot be blank.
- `barcode` is optional; if supplied it must be unique within the catalogue (returns `409 PRODUCT_ALREADY_EXISTS`).
- Rate limit: 5 submissions per 10 minutes per user (configurable); exceeding returns `429 RATE_LIMITED`.
- The product is created with `verification_status = "unverified"` and a `user_submitted` source.
- Every ingredient is parsed; unknown ingredients are created as `is_reviewed = false` for the admin queue. No ingredient is silently dropped.

Response is `201`:

```json
{
  "id": "…",
  "name": "User Submitted Serum",
  "barcode": "99990000",
  "category": "serum",
  "verification_status": "unverified",
  "message": "Product submitted for review. An admin will verify or reject it; until then it is clearly labelled as unverified."
}
```

### `GET /api/v1/products/categories`

Returns category counts. Requires auth.

### `GET /api/v1/brands?q=&limit=`

List/search brands. Requires auth.

## Admin endpoints (requires `admin` role)

### `GET /api/v1/admin/products`

Management list including unverified records. Accepts `verified_only`, `limit` (max 100), `offset`.

### `GET /api/v1/admin/products/review-queue?source=`

Unverified products awaiting review. `source`: `user_submitted` or `open_beauty_facts`.

### `POST /api/v1/admin/products`

Create a product. Barcode duplicates return `409 PRODUCT_ALREADY_EXISTS`. Payload accepts `name`, `category`, `barcode`, `brand_name`, `ingredients_raw_text`, `verification_status` (`unverified`, `verified`, `rejected`), `description`, `image_url`.

### `PUT /api/v1/admin/products/{product_id}`

Update name/category/barcode/brand/description/image/ingredients. Replacing ingredients re-parses and re-links the label. Audit logged.

### `DELETE /api/v1/admin/products/{product_id}`

Soft-delete (`is_active=false`). Audit logged.

### `POST /api/v1/admin/products/{product_id}/verify` / `/reject`

Sets `verification_status` and records `verified_by`/`verified_at`. Optional body `{"reason": string}` is stored in the audit log.

### `GET /api/v1/admin/ingredients?unreviewed=&q=&include_inactive=&limit=&offset=`

List ingredients; `unreviewed=true` shows only rows pending review. Unreviewed unknowns are created automatically during product parsing/submission.

### `GET /api/v1/admin/ingredients/unreviewed`

Convenience endpoint for the unreviewed queue.

### `POST /api/v1/admin/ingredients`

Create an ingredient:

```json
{
  "name": "Niacinamide",
  "description": "Brightening active",
  "reference_notes": "optional",
  "category_function": "active",
  "is_reviewed": false
}
```

Function must be one of `humectant`, `emollient`, `antioxidant`, `surfactant`, `preservative`, `active`, `uv_filter`, `fragrance`, `solvent`, `buffer`, `other`.

### `PUT /api/v1/admin/ingredients/{ingredient_id}`

Edit ingredient fields and toggle `is_reviewed`/`is_active`. Audit logged.

### `POST /api/v1/admin/ingredients/{ingredient_id}/aliases`

Add an alias; aliases are normalized and unique globally:

```json
{"ingredient_id": "…", "alias": "Vitamin B3"}
```

Path and body `ingredient_id` must match. Duplicates return `409`.

### `POST /api/v1/admin/ingredients/merge`

Merge a duplicate into a target:

```json
{"source_id": "…", "target_id": "…"}
```

Moves product ingredients and aliases; target is marked `is_reviewed = true`; source is deactivated (`is_active = false`). Duplicate links present on both rows for the same product are collapsed. Audit logged.

### `GET /api/v1/admin/audit-logs`

List admin actions with filters (`actor_id`, `action`, `entity_type`, `date_from`, `date_to`, `skip`, `limit`). Phase 3 catalogue actions include `product_create`, `product_update`, `product_soft_delete`, `product_verified`, `product_rejected`, `ingredient_create`, `ingredient_update`, `ingredient_alias_create`, `ingredient_merge`, plus Phase 2 user actions.

## Verification policy

- External provider products and user submissions are always `unverified`.
- Verified products are returned by default by the discovery endpoints; unverified records are included when `verified_only=false` (or via admin surfaces) and are clearly labelled `VerificationStatus.unverified`.
- Clients must never present unverified data as verified, and must surface the `source` (provider provenance) to admins during review.

## Development seed

`pnpm seed:phase3` inserts 51 development ingredients, their aliases, and 10 sample verified products (barcodes `4006381000001`–`4006381000010`), all prefixed `[Development seed]`. It is idempotent and is not usable as production catalogue data.
