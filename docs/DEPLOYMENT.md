# Deployment

## Container deployment

Copy `.env.example` to `.env`, replace every secret, then start the stack:

```bash
docker compose up --build -d
curl http://127.0.0.1:5050/health
curl http://127.0.0.1:5050/ready
```

The app is served by Gunicorn on port `5050`. The image health check uses `/ready`; `/health` is a basic liveness check. The Compose PostgreSQL service is infrastructure for the planned database backend; the current release still reads local JSON state.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `LUX_PORT` | `5050` | Host port in Compose |
| `LUX_SECRET_KEY` | none in production | Flask session signing |
| `LUX_CSRF_SECRET_KEY` | none in production | CSRF signing |
| `DATABASE_URL` | local state today | Future SQLite/PostgreSQL repository |
| `LUX_DOCKER_RUNTIME` | `runc` | Docker runtime, such as `runsc` |
| `LUX_SANDBOX_AUDIT_LOG` | `/tmp/lux-sandbox-audit.jsonl` | JSONL audit destination |
| `LUX_OLLAMA_MODEL` | application default | Hint model |

Production operators must provide strong secret values, terminate TLS at a reverse proxy, restrict Docker access, configure backups, and run database migrations before enabling hosted accounts.

## Gunicorn

```bash
gunicorn --bind 0.0.0.0:5050 --workers 2 --access-logfile - server:app
```

Scale workers based on memory and workload. Sandbox jobs should eventually move to a separate worker service so untrusted execution cannot consume web workers.

## Release checklist

- Run `pytest -q`, `ruff check .`, and `bandit -r .`.
- Build and scan the image.
- Set non-default secrets and configure TLS.
- Confirm `/health` and `/ready` from the deployment network.
- Apply migrations and verify backup/restore.
- Confirm audit log retention and alerting.
- Verify authentication, rate limits, upload limits, and authorization before public launch.
