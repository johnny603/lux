# Security Policy

## Supported Versions

Only the latest version on the `main` branch receives security updates.

## Reporting a Vulnerability

Please report suspected vulnerabilities through a
[GitHub private security advisory](https://github.com/johnny603/lux/security/advisories/new).
Do not disclose vulnerabilities in a public issue.

You can expect an acknowledgement within 72 hours. We will keep you informed
as we investigate, validate the report, and plan a fix or explain why the
report is not accepted.

## Scope

Security reports are welcome for:

- sandbox execution in `sandbox.py`;
- execution audit handling in `sandbox_audit.py`;
- the Ollama-backed agent in `agent.py`; and
- session handling in `server.py`.

The following are out of scope:

- rate limiting that is only relevant to local development;
- attacks that require a pre-existing shell on the host; and
- vulnerabilities in third-party dependencies, which are monitored through
  Dependabot and Snyk.
