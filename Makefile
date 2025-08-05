# Variables
PYTHON_VERSION := 3.11
VENV_NAME := saas-platform-venv

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: help setup setup-backend setup-frontend dev dev-backend dev-frontend test test-backend test-frontend build build-backend build-frontend docker-up docker-down docker-build clean

help: ## Show this help message
	@echo "$(BLUE)SaaS Platform - Available Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

setup: ## Setup the entire project (backend + frontend)
	@echo "$(BLUE)Setting up SaaS Platform...$(NC)"
	@$(MAKE) setup-backend
	@$(MAKE) setup-frontend
	@echo "$(GREEN)Setup completed!$(NC)"

setup-backend: ## Setup backend environment
	@echo "$(BLUE)Setting up backend...$(NC)"
	@cd backend && $(MAKE) create-venv
	@cd backend && cp env.example .env
	@echo "$(YELLOW)Please edit backend/.env with your configuration$(NC)"

setup-frontend: ## Setup frontend environment
	@echo "$(BLUE)Setting up frontend...$(NC)"
	@cd frontend && npm install
	@echo "$(GREEN)Frontend setup completed!$(NC)"

dev: ## Start development servers (backend + frontend)
	@echo "$(BLUE)Starting development servers...$(NC)"
	@$(MAKE) dev-backend & $(MAKE) dev-frontend

dev-backend: ## Start backend development server
	@echo "$(BLUE)Starting backend development server...$(NC)"
	@cd backend && $(MAKE) dev

dev-frontend: ## Start frontend development server
	@echo "$(BLUE)Starting frontend development server...$(NC)"
	@cd frontend && npm run dev

test: ## Run all tests (backend + frontend)
	@echo "$(BLUE)Running all tests...$(NC)"
	@$(MAKE) test-backend
	@$(MAKE) test-frontend

test-docker: ## Run tests with Docker services
	@echo "$(BLUE)Starting test services...$(NC)"
	@docker-compose -f docker-compose.test.yml up -d
	@echo "$(BLUE)Waiting for services to be ready...$(NC)"
	@sleep 10
	@$(MAKE) test-backend
	@$(MAKE) test-frontend
	@echo "$(BLUE)Stopping test services...$(NC)"
	@docker-compose -f docker-compose.test.yml down

test-backend: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	@cd backend && $(MAKE) test

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	@cd frontend && npm run test

test-coverage: ## Run tests with coverage (backend + frontend)
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@$(MAKE) test-backend-coverage
	@$(MAKE) test-frontend-coverage

test-backend-coverage: ## Run backend tests with coverage
	@echo "$(BLUE)Running backend tests with coverage...$(NC)"
	@cd backend && $(MAKE) test-coverage

test-frontend-coverage: ## Run frontend tests with coverage
	@echo "$(BLUE)Running frontend tests with coverage...$(NC)"
	@cd frontend && npm run test:coverage

build: ## Build all applications (backend + frontend)
	@echo "$(BLUE)Building applications...$(NC)"
	@$(MAKE) build-backend
	@$(MAKE) build-frontend

build-backend: ## Build backend application
	@echo "$(BLUE)Building backend...$(NC)"
	@cd backend && docker build -t saas-platform-backend .

build-frontend: ## Build frontend application
	@echo "$(BLUE)Building frontend...$(NC)"
	@cd frontend && docker build -t saas-platform-frontend .

docker-up: ## Start all services with Docker Compose
	@echo "$(BLUE)Starting all services...$(NC)"
	@docker-compose up -d

docker-down: ## Stop all services
	@echo "$(BLUE)Stopping all services...$(NC)"
	@docker-compose down

docker-build: ## Build and start all services
	@echo "$(BLUE)Building and starting all services...$(NC)"
	@docker-compose up -d --build

docker-logs: ## Show Docker Compose logs
	@echo "$(BLUE)Showing Docker Compose logs...$(NC)"
	@docker-compose logs -f

docker-dev-up: ## Start development services (database, redis, kafka)
	@echo "$(BLUE)Starting development services...$(NC)"
	@docker-compose -f docker-compose.dev.yml up -d

docker-dev-down: ## Stop development services
	@echo "$(BLUE)Stopping development services...$(NC)"
	@docker-compose -f docker-compose.dev.yml down

docker-dev-logs: ## Show development services logs
	@echo "$(BLUE)Showing development services logs...$(NC)"
	@docker-compose -f docker-compose.dev.yml logs -f

docker-local-up: ## Start local services (database, redis, kafka)
	@echo "$(BLUE)Starting local services...$(NC)"
	@docker-compose -f docker-compose.local.yml up -d

docker-local-down: ## Stop local services
	@echo "$(BLUE)Stopping local services...$(NC)"
	@docker-compose -f docker-compose.local.yml down

docker-local-logs: ## Show local services logs
	@echo "$(BLUE)Showing local services logs...$(NC)"
	@docker-compose -f docker-compose.local.yml logs -f

docker-prod: ## Start production services
	@echo "$(BLUE)Starting production services...$(NC)"
	@docker-compose -f docker-compose.prod.yml up -d

docker-prod-build: ## Build and start production services
	@echo "$(BLUE)Building and starting production services...$(NC)"
	@docker-compose -f docker-compose.prod.yml up -d --build

lint: ## Run linting (backend + frontend)
	@echo "$(BLUE)Running linting...$(NC)"
	@$(MAKE) lint-backend
	@$(MAKE) lint-frontend

lint-backend: ## Run backend linting
	@echo "$(BLUE)Running backend linting...$(NC)"
	@cd backend && $(MAKE) ruff

lint-frontend: ## Run frontend linting
	@echo "$(BLUE)Running frontend linting...$(NC)"
	@cd frontend && npm run lint

format: ## Format code (backend + frontend)
	@echo "$(BLUE)Formatting code...$(NC)"
	@$(MAKE) format-backend
	@$(MAKE) format-frontend

format-backend: ## Format backend code
	@echo "$(BLUE)Formatting backend code...$(NC)"
	@cd backend && $(MAKE) format

format-frontend: ## Format frontend code
	@echo "$(BLUE)Formatting frontend code...$(NC)"
	@cd frontend && npm run format

clean: ## Clean all generated files
	@echo "$(YELLOW)Cleaning generated files...$(NC)"
	@cd backend && $(MAKE) clean
	@cd frontend && rm -rf node_modules dist .vite
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -delete
	@find . -name ".pytest_cache" -delete
	@find . -name "htmlcov" -delete
	@find . -name ".coverage" -delete
	@echo "$(GREEN)Clean completed!$(NC)"

migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	@cd backend && $(MAKE) migrate

migrate-create: ## Create new migration
	@echo "$(BLUE)Creating new migration...$(NC)"
	@cd backend && $(MAKE) migrate-revision MESSAGE="$(MESSAGE)"

shell: ## Open backend Python shell
	@echo "$(BLUE)Opening Python shell...$(NC)"
	@cd backend && $(MAKE) shell

logs: ## Show application logs
	@echo "$(BLUE)Showing application logs...$(NC)"
	@cd backend && $(MAKE) logs

install-deps: ## Install all dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@cd backend && $(MAKE) install-deps
	@cd frontend && npm install

check-all: ## Run all checks (lint, test, format)
	@echo "$(BLUE)Running all checks...$(NC)"
	@$(MAKE) lint
	@$(MAKE) test
	@$(MAKE) format

monitoring-up: ## Start monitoring services
	@echo "$(BLUE)Starting monitoring services...$(NC)"
	@docker-compose -f docker-compose.monitoring.yml up -d

monitoring-down: ## Stop monitoring services
	@echo "$(BLUE)Stopping monitoring services...$(NC)"
	@docker-compose -f docker-compose.monitoring.yml down

monitoring-logs: ## Show monitoring services logs
	@echo "$(BLUE)Showing monitoring services logs...$(NC)"
	@docker-compose -f docker-compose.monitoring.yml logs -f

docker-full-up: ## Start all services with full monitoring
	@echo "$(BLUE)Starting all services with full monitoring...$(NC)"
	@docker-compose -f docker-compose.full.yml up -d

docker-full-down: ## Stop all services with full monitoring
	@echo "$(BLUE)Stopping all services with full monitoring...$(NC)"
	@docker-compose -f docker-compose.full.yml down

docker-full-logs: ## Show all services logs with full monitoring
	@echo "$(BLUE)Showing all services logs with full monitoring...$(NC)"
	@docker-compose -f docker-compose.full.yml logs -f

docker-simple-up: ## Start simple development services (database, redis, kafka)
	@echo "$(BLUE)Starting simple development services...$(NC)"
	@docker-compose -f docker-compose.dev-simple.yml up -d

docker-simple-down: ## Stop simple development services
	@echo "$(BLUE)Stopping simple development services...$(NC)"
	@docker-compose -f docker-compose.dev-simple.yml down

docker-simple-logs: ## Show simple development services logs
	@echo "$(BLUE)Showing simple development services logs...$(NC)"
	@docker-compose -f docker-compose.dev-simple.yml logs -f

docker-prod-simple: ## Start simple production services
	@echo "$(BLUE)Starting simple production services...$(NC)"
	@docker-compose -f docker-compose.prod-simple.yml up -d

docker-prod-simple-down: ## Stop simple production services
	@echo "$(BLUE)Stopping simple production services...$(NC)"
	@docker-compose -f docker-compose.prod-simple.yml down

docker-prod-simple-logs: ## Show simple production services logs
	@echo "$(BLUE)Showing simple production services logs...$(NC)"
	@docker-compose -f docker-compose.prod-simple.yml logs -f

docker-hot-up: ## Start development services with hot reload
	@echo "$(BLUE)Starting development services with hot reload...$(NC)"
	@docker-compose -f docker-compose.dev-hot.yml up -d

docker-hot-down: ## Stop development services with hot reload
	@echo "$(BLUE)Stopping development services with hot reload...$(NC)"
	@docker-compose -f docker-compose.dev-hot.yml down

docker-hot-logs: ## Show development services logs with hot reload
	@echo "$(BLUE)Showing development services logs with hot reload...$(NC)"
	@docker-compose -f docker-compose.dev-hot.yml logs -f 