# API Reference

Base URL: `http://127.0.0.1:5050`.

All API endpoints return JSON payloads. Standard error responses use the format:
```json
{
  "ok": false,
  "error": "<error message>"
}
```

---

## Local Setup & Quick Start

1. **Set up Python environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Start the Lux server**:
   ```bash
   python3 server.py
   ```
   The server will listen at `http://127.0.0.1:5050`.

3. **Verify server readiness**:
   ```bash
   curl -s http://127.0.0.1:5050/health
   curl -s http://127.0.0.1:5050/ready
   ```

---

## Service Health Endpoints

### `GET /health`
Returns the operational health of the Lux server.

- **Status Code**: `200 OK`
- **Response Example**:
  ```json
  {
    "ok": true,
    "service": "ok"
  }
  ```

### `GET /ready`
Returns the readiness state of the Lux server to accept requests.

- **Status Code**: `200 OK`
- **Response Example**:
  ```json
  {
    "ok": true,
    "service": "ready"
  }
  ```

---

## Public Catalog & Content Endpoints

### `GET /api/v1/levels`
Retrieves the complete catalog of puzzles with metadata.

- **Status Code**: `200 OK`
- **Response Example**:
  ```json
  [
    {
      "id": "1",
      "category": "Linux",
      "title": "Linux: List hidden files",
      "description": "What ls flag shows hidden files?",
      "hint": "Think dotfiles",
      "difficulty": "easy",
      "tags": ["linux", "filesystem"]
    },
    {
      "id": "5",
      "category": "Programming",
      "title": "C: Main function return",
      "description": "Write a minimal C program whose main function returns 0.",
      "difficulty": "easy",
      "tags": ["c", "compilation"]
    }
  ]
  ```

### `GET /api/v1/level/<id>`
Retrieves metadata for a specific level by its identifier.

- **URL Parameters**:
  - `id` (string/integer): The unique identifier of the puzzle (e.g. `1`).
- **Response (Success)**:
  - **Status Code**: `200 OK`
  - **Example**:
    ```json
    {
      "id": "1",
      "category": "Linux",
      "title": "Linux: List hidden files",
      "description": "What ls flag shows hidden files?",
      "hint": "Think dotfiles",
      "difficulty": "easy",
      "tags": ["linux", "filesystem"]
    }
    ```
- **Response (Not Found)**:
  - **Status Code**: `404 Not Found`
  - **Example**:
    ```json
    {
      "ok": false,
      "error": "not found"
    }
    ```

### `GET /api/v1/achievements`
Returns the dictionary of achievements and unlock statuses from the current state.

- **Status Code**: `200 OK`
- **Response Example**:
  ```json
  {
    "first_solve": {
      "unlocked": true,
      "unlocked_at": "2026-09-04T12:00:00Z"
    }
  }
  ```

### `GET /api/v1/contributors`
Returns normalized contributor entries loaded from the project manifest (`contributors.json`).

- **Status Code**: `200 OK`
- **Response Example**:
  ```json
  {
    "contributors": [
      {
        "login": "ada",
        "name": "Ada Lovelace",
        "contributions": ["documentation"],
        "badges": ["founding-contributor"]
      }
    ]
  }
  ```

---

## User Progress & State Endpoints

### `GET /api/v1/progress`
Retrieves a summary of user progress across categories, completed levels, achievements, and profile info.

- **Status Code**: `200 OK`
- **Response Example**:
  ```json
  {
    "progress": {
      "total_levels": 20,
      "solved_count": 2,
      "percent_complete": 10.0,
      "by_category": {
        "Linux": {
          "total": 5,
          "solved": 1
        }
      }
    },
    "solved": ["1", "5"],
    "achievements": {},
    "profile": {
      "display_name": "Learner",
      "preferences": {}
    }
  }
  ```

### `GET /api/v1/profile`
Retrieves profile details including display name and preferences.

- **Status Code**: `200 OK`
- **Response Example**:
  ```json
  {
    "display_name": "Learner",
    "preferences": {
      "difficulty_preference": "any",
      "favorite_categories": [],
      "hint_strictness": "standard"
    },
    "created_at": "2026-09-04T10:00:00Z"
  }
  ```

### `GET /api/v1/leaderboard`
Returns calculated rankings across learners.

- **Query Parameters**:
  - `metric` (optional string): Metric to rank by (default: `solved_count`).
- **Status Code**: `200 OK`
- **Response Example**:
  ```json
  {
    "metric": "solved_count",
    "entries": [
      {
        "name": "Learner",
        "score": 2.0,
        "solved_count": 2,
        "streak": 1,
        "xp": 50
      }
    ]
  }
  ```

### `GET /api/v1/learning-path`
Generates recommended levels tailored to the user's current progress.

- **Query Parameters**:
  - `limit` (optional integer): Maximum recommended items (default: `5`).
- **Status Code**: `200 OK`
- **Response Example**:
  ```json
  {
    "limit": 5,
    "recommended_levels": [
      {
        "id": "2",
        "category": "Linux",
        "difficulty": "easy",
        "title": "Linux: File permissions"
      }
    ]
  }
  ```

### `GET /api/v1/game/adventure`
Retrieves current campaign progression and unlocked worlds.

- **Status Code**: `200 OK`
- **Response Example**:
  ```json
  {
    "xp": 0,
    "current_world": null,
    "unlocked_worlds": [],
    "campaign_progress": {}
  }
  ```

### `GET /api/v1/game/daily`
Retrieves daily challenge status and today's featured puzzle.

- **Status Code**: `200 OK`
- **Response Example**:
  ```json
  {
    "completed_today": false,
    "date": "2026-09-05",
    "level": {
      "id": "1",
      "category": "Linux",
      "difficulty": "easy",
      "title": "Linux: List hidden files"
    }
  }
  ```

---

## Submission & Generation Endpoints

### `POST /api/v1/submit`
Validates an answer or script submission for a puzzle.

- **Request Body (String Attempt)**:
  ```json
  {
    "level_id": "1",
    "attempt": "-a"
  }
  ```
- **Request Body (Script Submission)**:
  ```json
  {
    "level_id": "5",
    "files": {
      "answer.c": "int main(void) { return 0; }"
    }
  }
  ```
- **Response (Success - Correct Attempt)**:
  - **Status Code**: `200 OK`
  - **Example**:
    ```json
    {
      "ok": true,
      "correct": true
    }
    ```
- **Response (Success - Incorrect Attempt)**:
  - **Status Code**: `200 OK`
  - **Example**:
    ```json
    {
      "ok": true,
      "correct": false,
      "expected": "-a"
    }
    ```
- **Response (Validation Error - Missing `level_id`)**:
  - **Status Code**: `400 Bad Request`
  - **Example**:
    ```json
    {
      "ok": false,
      "error": "missing level_id"
    }
    ```
- **Response (Validation Error - Invalid Level)**:
  - **Status Code**: `404 Not Found`
  - **Example**:
    ```json
    {
      "ok": false,
      "error": "invalid level"
    }
    ```

### `POST /api/v1/puzzles/generate`
Generates a new puzzle on-demand using the configured local AI model.

- **Request Body**:
  ```json
  {
    "category": "Programming",
    "difficulty": "easy",
    "topic": "recursion"
  }
  ```
- **Response**:
  - **Status Code**: `200 OK`
  - **Example**:
    ```json
    {
      "ok": true,
      "puzzle": {
        "id": "31",
        "category": "Programming",
        "difficulty": "easy",
        "title": "Recursion: Base Case",
        "description": "...",
        "answer": "..."
      }
    }
    ```

---

## Authentication Contract for Hosted v1.0 (Planned / Proposed)

> **Note**: Authentication is not enabled in the current local-first standalone server. Before deploying multi-user hosted environments, the following authentication endpoints will be introduced:

- `POST /api/v1/auth/register` — Register a new user account with credentials. Returns access and refresh tokens.
- `POST /api/v1/auth/login` — Authenticate existing credentials. Returns access and refresh tokens.
- `POST /api/v1/auth/refresh` — Exchange a valid refresh token for a rotated short-lived access token.
- `POST /api/v1/auth/logout` — Revoke the current refresh token session.

### Proposed Authentication Requirements:
- Authenticated requests must include the HTTP header: `Authorization: Bearer <access-token>`.
- Endpoints modifying or retrieving user-specific data (`POST /api/v1/submit`, profile management, sync) will require valid bearer tokens.
- Secrets and passwords must use argon2id or bcrypt hashing; refresh tokens stored hashed in the persistence layer.

---

## Synchronization Protocol (Planned / Proposed)

> **Note**: Cross-device sync is planned for upcoming releases.

- `POST /api/v1/sync` — Accepts a batch of idempotent client attempt and progression events. Returns server-side cursors and conflict resolution results.
- Persistence architecture will support SQLite for single-node instances and PostgreSQL for multi-tenant deployments.
