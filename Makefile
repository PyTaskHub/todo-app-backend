.PHONY: help setup run test test-cov clean format lint migration migrate \
        db-up db-down db-restart \
        docker-build docker-up docker-down docker-restart \
        docker-logs docker-logs-backend docker-logs-db \
        docker-shell docker-shell-db docker-clean docker-ps \
        docker-migrate docker-migration docker-test docker-test-cov \
        dev dev-stop dev-restart

# Default target
.DEFAULT_GOAL := help

help:  ## Show this help message
	@echo "PyTaskHub - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# Development Commands
# ============================================================================

setup:  ## Setup project (install dependencies, create .env)
	@echo "Setting up PyTaskHub..."
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	cp .env.example .env
	@echo "Setup complete. Edit .env file with your settings."

run:  ## Run development server
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run tests
	pytest -v

test-cov:  ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term -v

clean:  ## Clean cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage

# ============================================================================
# Code Quality
# ============================================================================

format:  ## Format code with black and isort
	black app/ tests/
	isort app/ tests/

lint:  ## Lint code with flake8
	flake8 app/ tests/

# ============================================================================
# Database Commands (Local)
# ============================================================================

migration:  ## Create new migration (usage: make migration message="your message")
	alembic revision --autogenerate -m "$(message)"

migrate:  ## Apply migrations
	alembic upgrade head

db-up:  ## Start PostgreSQL in Docker (local development)
	docker run -d \
		--name pytaskhub-db \
		-e POSTGRES_USER=postgres \
		-e POSTGRES_PASSWORD=postgres \
		-e POSTGRES_DB=pytaskhub \
		-p 5432:5432 \
		postgres:15

db-down:  ## Stop PostgreSQL
	docker stop pytaskhub-db 2>/dev/null || true
	docker rm pytaskhub-db 2>/dev/null || true

db-restart:  ## Restart PostgreSQL
	$(MAKE) db-down
	$(MAKE) db-up

# ============================================================================
# Docker Compose Commands
# ============================================================================

docker-build:  ## Build Docker images
	docker-compose build

docker-up:  ## Start all services with Docker Compose
	docker-compose up -d

docker-down:  ## Stop all services
	docker-compose down

docker-restart:  ## Restart all services
	docker-compose restart

docker-logs:  ## Show logs from all services
	docker-compose logs -f

docker-logs-backend:  ## Show backend logs only
	docker-compose logs -f backend

docker-logs-db:  ## Show database logs only
	docker-compose logs -f db

docker-shell:  ## Open shell in backend container
	docker-compose exec backend /bin/sh

docker-shell-db:  ## Open PostgreSQL shell
	docker-compose exec db psql -U postgres -d pytaskhub

docker-clean:  ## Remove all containers, volumes, and images
	docker-compose down -v
	docker system prune -f

docker-ps:  ## Show running containers
	docker-compose ps

docker-migrate:  ## Run migrations in Docker
	docker-compose exec backend alembic upgrade head

docker-migration:  ## Create migration in Docker
	docker-compose exec backend alembic revision --autogenerate -m "$(message)"

docker-test:  ## Run tests in Docker
	docker-compose exec backend pytest -v

docker-test-cov:  ## Run tests with coverage in Docker
	docker-compose exec backend pytest --cov=app --cov-report=html --cov-report=term -v

# ============================================================================
# Combined Commands
# ============================================================================

dev:  ## Start development environment (Docker Compose)
	$(MAKE) docker-up
	@echo ""
	@echo "Development environment started."
	@echo "API Documentation: http://localhost:8000/api/docs"
	@echo "Database: postgresql://postgres:postgres@localhost:5432/pytaskhub"
	@echo ""
	@echo "Useful commands:"
	@echo "  make docker-logs        - View logs"
	@echo "  make docker-shell       - Open backend shell"
	@echo "  make docker-migrate     - Run migrations"
	@echo "  make docker-test        - Run tests"

dev-stop:  ## Stop development environment
	$(MAKE) docker-down
	@echo "Development environment stopped."

dev-restart:  ## Restart development environment
	$(MAKE) docker-restart
	@echo "Development environment restarted."
