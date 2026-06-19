# API Design Conventions

## URL Structure
- Use nouns, not verbs (HTTP methods are the verbs)
- Plural nouns for collections: `/users`, `/orders`
- Hyphens for multi-word segments: `/managed-devices`
- Lowercase consistently
- No trailing slashes, no file extensions
- Limit nesting depth to 3 levels max

## HTTP Methods
| Method | Purpose | Success Code |
|--------|---------|-------------|
| GET | Read resource | 200 |
| POST | Create resource | 201 (with Location header) |
| PUT | Full replace | 200, 201, 204 |
| PATCH | Partial update | 200, 204 |
| DELETE | Remove resource | 200, 204 |

- POST to collection → 201 Created + Location header
- PUT is idempotent, POST is not
- Use PATCH for partial updates, not PUT

## Status Codes
- 200: Generic success (GET, PUT, PATCH)
- 201: Resource created (POST) — always include Location header
- 204: Success with no body (DELETE)
- 400: Bad request / validation error
- 401: Not authenticated (missing/invalid credentials)
- 403: Not authorized (insufficient permissions)
- 404: Resource not found
- 409: Conflict (duplicate creation)
- 422: Semantically invalid input
- 429: Rate limited — include Retry-After header
- 500: Server error

401 ≠ 403: 401 = not logged in, 403 = logged in but no permission

## Request/Response Patterns
- Always use `Content-Type: application/json`
- Collection responses: `{ "data": [...], "meta": { "total", "page", "hasNext" } }`
- Single resource: `{ "id": 1, "name": "..." }`
- Creation response: 201 + Location header + resource body
- Error response: `{ "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [...] } }`
- Never expose stack traces or internal errors in production

## Pagination
- Offset-based: `?page=2&limit=25` (simple)
- Cursor-based: `?after=<cursor>&first=25` (preferred for large datasets)
- Always include: total, hasNext/hasPrev

## Filtering & Sorting
- Filter via query params: `?category=electronics&status=active`
- Sort: `sort=field` (asc), `sort=-field` (desc)
- Search: `?search=john`

## Authentication
- JWT: `Authorization: Bearer <token>` header
- API Key: `X-API-Key: <key>` header (never in URLs)
- Always use HTTPS
- Hash passwords with bcrypt/scrypt
- Token refresh: short-lived access + long-lived refresh

## Rate Limiting
- Return 429 with headers: `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`
- Implement per-user, per-IP, or per-API-key

## CORS
- Set explicit origins (never `*` with credentials)
- Handle OPTIONS preflight
- Return CORS headers on error responses too

## Folder Structure
```
api/
  routes/       # Route definitions (thin controllers)
  services/     # Business logic
  models/       # Database models
  schemas/      # Request/response schemas (Pydantic/Zod)
  middleware/    # Auth, rate limiting, CORS
```

## Anti-Patterns to Avoid
- Verbs in URIs: `/getUser` → use `GET /users/{id}`
- Returning 200 for errors → use proper 4xx/5xx
- Missing Location header on 201
- Exposing database internals in API responses
- No input validation
- Hardcoded credentials
- Missing CORS configuration
- No pagination on collection endpoints
- GET for write operations
- Not using dependency injection for DB connections
