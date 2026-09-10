# CambioBot Makefile
# Common development commands

.PHONY: help install dev-install test lint format typecheck clean migrate seed run-api run-worker docker-up docker-down docker-logs docker-build

# Default target
help:
	@echo "CambioBot - Available commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install       Install production dependencies"
	@echo "  dev-install   Install all dependencies (including dev)"
	@echo ""
	@echo "Development:"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage"
	@echo "  lint          Run ruff linter"
	@echo "  format        Format code with ruff"
	@echo "  typecheck     Run mypy type checking"
	@echo "  check         Run all checks (lint + format + typecheck + test)"
	@echo ""
	@echo "Database:"
	@echo "  migrate       Run database migrations"
	@echo "  migrate-create Create new migration"
	@echo "  seed          Seed database with reference data"
	@echo "  db-reset      Reset database (drop + migrate + seed)"
	@echo ""
	@echo "Run:"
	@echo "  run-api       Start FastAPI server (dev)"
	@echo "  run-worker    Start background worker"
	@echo "  run-cli       Show CLI help"
	@echo ""
	@echo "Docker:"
	@echo "  docker-up     Start all services"
	@echo "  docker-down   Stop all services"
	@echo "  docker-logs   View logs"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-push   Push Docker image"
	@echo ""
	@echo "Utilities:"
	@echo "  clean         Clean build artifacts"
	@echo "  pre-commit    Install pre-commit hooks"
	@echo "  security      Run security scans"

# Installation
install:
	poetry install --only=main --no-interaction

dev-install:
	poetry install --with=dev,tradingagents --no-interaction

# Testing
test:
	poetry run pytest -v

test-cov:
	poetry run pytest --cov=cambiobot --cov-report=term-missing --cov-report=html

test-unit:
	poetry run pytest tests/unit -v

test-integration:
	poetry run pytest tests/integration -v

test-e2e:
	poetry run pytest tests/e2e -v

# Code Quality
lint:
	poetry run ruff check .

format:
	poetry run ruff format .

typecheck:
	poetry run mypy cambiobot --ignore-missing-imports

check: lint format typecheck test

# Database
migrate:
	poetry run alembic upgrade head

migrate-create:
	@read -p "Migration message: " msg; \
	poetry run alembic revision --autogenerate -m "$$msg"

seed:
	poetry run python -m scripts.seed_database

db-reset:
	poetry run alembic downgrade base
	poetry run alembic upgrade head
	poetry run python -m scripts.seed_database

# Run
run-api:
	poetry run uvicorn cambiobot.api.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	poetry run python -m cambiobot.worker

run-cli:
	poetry run cambiobot --help

# Docker
docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-build:
	docker build -t cambiobot:latest .

docker-push:
	docker tag cambiobot:latest $(DOCKERHUB_USERNAME)/cambiobot:latest
	docker push $(DOCKERHUB_USERNAME)/cambiobot:latest

# Utilities
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ *.egg-info/

pre-commit:
	poetry run pre-commit install
	poetry run pre-commit run --all-files

security:
	poetry run pip-audit
	poetry run bandit -r cambiobot -f json -o bandit-report.json || true
	trufflehog filesystem --directory . --no-verification || true

# Development helpers
shell:
	poetry run ipython

notebook:
	poetry run jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root

# FX Data helpers
fx-rates:
	poetry run cambiobot rates multi --targets USD,EUR,GBP,JPY,ARS

fx-dca:
	poetry run cambiobot dca simulate --target USD --amount 5000 --installments 8

fx-analysis:
	poetry run cambiobot analysis fx --targets USD,EUR --budget USD=5000,EUR=3000

# TradingAgents
ta-analysis:
	poetry run cambiobot analysis tradingagents --targets USD,EUR

# CI/CD simulation
ci: check
	@echo "CI checks passed!"