#!/bin/bash
set -e

echo "🧪 Running tests..."
pytest -q

echo "🔍 Linting with ruff..."
ruff check .

echo "🔒 Security scan (Bandit)..."
# The '|| true' allows the script to continue; remove it if you want to fail on findings
bandit -r . -ll -f custom || true

echo "🐳 Building Docker image (smoke test)..."
docker build -t lux-test . --no-cache > /dev/null 2>&1
echo "   ✅ Docker build passed"

echo "✅ All local checks passed!"
