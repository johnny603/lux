# API

Base URL: `http://127.0.0.1:5050`. JSON errors use `{ "ok": false, "error": "..." }`.

## Public catalog

- `GET /api/v1/levels` returns puzzle metadata.
- `GET /api/v1/level/<id>` returns one puzzle.
- `GET /api/v1/achievements` returns local achievements.
- `GET /api/v1/contributors` returns the contributor manifest.
- `GET /health` and `GET /ready` return service status.

## Submit

`POST /api/v1/submit` is the versioned equivalent of `/submit`.

```json
{"level_id": "1", "attempt": "-a"}
```

A successful request returns `correct: true|false`. Script puzzles accept a `files` object instead of, or alongside, `attempt`:

```json
{"level_id": "5", "files": {"answer.c": "int main(void) { return 0; }"}}
```

Submissions are currently validated without an account and progress is local JSON state. Clients must not assume completion is synchronized across devices.

## Authentication contract for hosted v1.0

Authentication is not enabled in the current local-first server. Before hosted multi-user use, add:

- `POST /api/v1/auth/register` -> access and refresh tokens
- `POST /api/v1/auth/login` -> access and refresh tokens
- `POST /api/v1/auth/refresh` -> rotated access token
- `POST /api/v1/auth/logout` -> revoke refresh token

Authenticated requests should send `Authorization: Bearer <access-token>`. `POST /api/v1/submit`, profile, progress, and sync endpoints must require authentication. Passwords must use a maintained password-hashing library, refresh tokens must be stored hashed, and login/submit endpoints need rate limits.

## Planned sync

`POST /api/v1/sync` should accept idempotent attempt events with client IDs and return the server cursor plus conflict decisions. The database repository should support SQLite for single-instance installs and PostgreSQL for hosted deployments.
