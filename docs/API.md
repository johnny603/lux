# Lux API reference (`/api/v1`)

Base URL (local default): `http://127.0.0.1:5050`.

All JSON error responses use:

```json
{ "ok": false, "error": "human-readable message" }
```

Successful payloads are plain JSON objects (some routes wrap with `"ok": true`).

## Service health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness probe |
| `GET` | `/ready` | Readiness probe |

## Public catalog (read)

### `GET /api/v1/levels`

Returns puzzle metadata for the catalog.

**Example response (shape):**

```json
[
  {
    "id": "1",
    "title": "…",
    "difficulty": "easy",
    "category": "…"
  }
]
```

### `GET /api/v1/level/<id>`

Returns one puzzle by id. Missing ids return an error payload.

### `GET /api/v1/achievements`

Returns local achievement state from the on-disk progress store.

### `GET /api/v1/contributors`

```json
{ "contributors": [ /* manifest entries */ ] }
```

### `GET /api/v1/progress`

Aggregate progress for the local learner profile:

```json
{
  "progress": { },
  "solved": ["1", "2"],
  "achievements": { },
  "profile": {
    "display_name": "Learner",
    "preferences": { }
  }
}
```

### `GET /api/v1/profile` / `PUT /api/v1/profile`

Read or update the local display name and preferences (no account auth yet).

### `GET /api/v1/leaderboard`

Local leaderboard snapshot.

### `GET /api/v1/learning-path`

Suggested next puzzles for the local profile.

### Game helpers

| Method | Path | Notes |
|--------|------|--------|
| `GET` | `/api/v1/game/adventure` | Adventure mode payload |
| `GET` | `/api/v1/game/daily` | Daily puzzle payload |
| `POST` | `/api/v1/puzzles/generate` | Experimental generator (may require flags) |

## Submit

### `POST /api/v1/submit`

Versioned equivalent of `POST /submit`.

**Shell / CLI style attempt:**

```json
{ "level_id": "1", "attempt": "-a" }
```

**Script puzzle with files:**

```json
{
  "level_id": "5",
  "files": {
    "answer.c": "int main(void) { return 0; }"
  }
}
```

**Success shape:** includes `correct: true|false`. Validation is local-first; there is no cross-device sync yet.

## Local setup

```bash
# from repo root — see README for exact install
python server.py
# or the project’s documented entrypoint on port 5050
curl -s http://127.0.0.1:5050/health
curl -s http://127.0.0.1:5050/api/v1/levels | head
```

## Future: authentication (not shipped)

Authentication is **not** enabled on the current local-first server. Before hosted multi-user use, planned endpoints:

- `POST /api/v1/auth/register` → access + refresh tokens  
- `POST /api/v1/auth/login` → access + refresh tokens  
- `POST /api/v1/auth/refresh` → rotated access token  
- `POST /api/v1/auth/logout` → revoke refresh token  

Authenticated requests should send `Authorization: Bearer <access-token>`. Submit, profile, progress, and sync should require auth. Use a maintained password hasher, store refresh tokens hashed, and rate-limit login/submit.

## Future: sync

`POST /api/v1/sync` should accept idempotent attempt events with client IDs and return a server cursor plus conflict decisions. Storage should support SQLite (single instance) and PostgreSQL (hosted).
