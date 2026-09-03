# Mentorship Issue Starters

These four issues are intentionally scoped for first-time contributors. Apply the labels listed with each issue and link the relevant file paths in the issue body.

## Add contributor recognition

Labels: `good first issue`, `mentorship`, `documentation`

Add entries to `contributors.json`, expose them through `contributors.py`, and render them at `/contributors` and `/api/v1/contributors`.

Acceptance criteria:

- Invalid or missing manifests return an empty contributor list.
- The HTML page shows names, GitHub handles, contributions, and badges.
- API output is JSON with a `contributors` list.
- `pytest -q tests/test_contributors.py` passes.

## Create the Flutter catalog client

Labels: `good first issue`, `mentorship`, `mobile`

Create a minimal Flutter client that fetches `/api/v1/levels`, parses level metadata, and displays loading, error, empty, and success states.

Acceptance criteria:

- Base URL is configurable.
- Network failures are actionable and do not crash the app.
- Models have unit tests for the current API response.
- A short README explains local server setup and `flutter test`.

## Document the versioned API

Labels: `good first issue`, `mentorship`, `documentation`

Document the existing `/api/v1` read endpoints and identify the proposed authenticated submit and sync endpoints.

Acceptance criteria:

- Add `docs/API.md` or `docs/api/openapi.yaml`.
- Include request and response examples, error codes, and local setup.
- Verify examples against Flask test-client tests.
- Link the document from `README.md`.

## Add sandbox execution audit records

Labels: `help wanted`, `mentorship`, `security`

Record a privacy-conscious audit event for each sandbox execution in `sandbox.py`.

Acceptance criteria:

- Each event has job ID, puzzle ID, runtime, duration, exit code, timeout, and result.
- Raw submitted source is not logged by default.
- Docker failures and timeouts are represented distinctly.
- Tests verify event fields and cleanup behavior.
