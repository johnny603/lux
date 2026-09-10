.PHONY: install lint test test-v run agent docker-up docker-down ci clean

install:
	python3 -m pip install -r requirements.txt -r requirements-dev.txt

lint:
	ruff check .
	ruff format --check .

test:
	pytest

test-v:
	pytest -v --tb=short

run:
	python3 server.py

agent:
	python3 agent.py

docker-up:
	docker compose up --build

docker-down:
	docker compose down

ci:
	bash scripts/ci.sh

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
