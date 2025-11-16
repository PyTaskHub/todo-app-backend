.PHONY: help setup install run test format lint clean db-up db-down db-restart migration migrate env-create

help:
	@echo "PyTaskHub Backend - Available commands:"
	@echo ""
	@echo "Setup:"
	@echo "  make setup        - Complete project setup (first time)"
	@echo "  make env-create   - Create .env from .env.example"
	@echo "  make install      - Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run          - Run development server"
	@echo "  make test         - Run tests with coverage"
	@echo "  make format       - Format code with black and isort"
	@echo "  make lint         - Lint code with flake8"
	@echo "  make clean        - Clean cache files"
	@echo ""
	@echo "Database:"
	@echo "  make db-up        - Start PostgreSQL in Docker"
	@echo "  make db-down      - Stop PostgreSQL"
	@echo "  make db-restart   - Restart PostgreSQL"
	@echo "  make migration    - Create new migration (usage: make migration message='description')"
	@echo "  make migrate      - Apply migrations"
	@echo ""

setup: env-create install db-up
	@echo " Project setup complete!"
	@echo "Next steps:"
	@echo "  1. Edit .env and set your SECRET_KEY"
	@echo "  2. Run: make migrate"
	@echo "  3. Run: make run"

env-create:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo " Created .env from .env.example"; \
		echo "️  Don't forget to set SECRET_KEY in .env!"; \
	else \
		echo "️  .env already exists, skipping..."; \
	fi

install:
	@echo " Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo " Dependencies installed"

run:
	@echo " Starting development server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo " Running tests..."
	pytest -v --cov=app --cov-report=html --cov-report=term
	@echo " Tests complete. Coverage report: htmlcov/index.html"

format:
	@echo " Formatting code..."
	black app tests
	isort app tests
	@echo " Code formatted"

lint:
	@echo " Linting code..."
	flake8 app tests --max-line-length=100
	@echo " Linting complete"

clean:
	@echo " Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	rm -rf htmlcov 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	rm -rf dist 2>/dev/null || true
	rm -rf build 2>/dev/null || true
	@echo " Cache cleaned"

db-up:
	@echo " Starting PostgreSQL..."
	@docker ps -a --format '{{.Names}}' | grep -q pytaskhub-db && \
		(echo "️  Container pytaskhub-db already exists. Use 'make db-restart' to restart.") || \
		(docker run -d \
			--name pytaskhub-db \
			-e POSTGRES_USER=postgres \
			-e POSTGRES_PASSWORD=postgres \
			-e POSTGRES_DB=pytaskhub \
			-p 5432:5432 \
			postgres:15 && \
		echo " PostgreSQL started on port 5432")

db-down:
	@echo " Stopping PostgreSQL..."
	@docker stop pytaskhub-db 2>/dev/null || true
	@docker rm pytaskhub-db 2>/dev/null || true
	@echo " PostgreSQL stopped"

db-restart: db-down db-up
	@echo " PostgreSQL restarted"

migration:
	@if [ -z "$(message)" ]; then \
		echo " Error: message is required"; \
		echo "Usage: make migration message='Your migration description'"; \
		echo "Example: make migration message='Add email column to users'"; \
		exit 1; \
	fi
	@echo " Creating migration: $(message)"
	alembic revision --autogenerate -m "$(message)"
	@echo " Migration created"

migrate:
	@echo "️  Applying migrations..."
	alembic upgrade head
	@echo " Migrations applied"