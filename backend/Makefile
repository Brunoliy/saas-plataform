# Variables
PYTHON_VERSION := 3.11
VENV_NAME := saas-platform-venv
POETRY_ENV := $(shell poetry env info --path 2>/dev/null || echo "")

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: help create-venv create-venv-mac create-venv-aws clean-venv install-deps dev test test-coverage test-file ruff ruff-check ruff-fix migrate migrate-up migrate-down shell lint type-check format check-all

help: ## Show this help message
	@echo "$(BLUE)SaaS Platform Backend - Available Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

create-venv: ## Create virtual environment (detects OS)
	@echo "$(BLUE)Detecting OS and creating virtual environment...$(NC)"
	@if [ "$(OS)" = "Windows_NT" ]; then \
		$(MAKE) create-venv-windows; \
	elif [ "$$(uname)" = "Darwin" ]; then \
		$(MAKE) create-venv-mac; \
	else \
		$(MAKE) create-venv-aws; \
	fi

create-venv-mac: ## Create virtual environment for macOS
	@echo "$(BLUE)Setting up environment for macOS...$(NC)"
	@echo "$(YELLOW)Installing Python $(PYTHON_VERSION) with pyenv...$(NC)"
	@if ! command -v pyenv &> /dev/null; then \
		echo "$(RED)pyenv not found. Installing with Homebrew...$(NC)"; \
		brew install pyenv; \
	fi
	@pyenv install $(PYTHON_VERSION) -s
	@echo "$(YELLOW)Setting global Python version...$(NC)"
	@pyenv global $(PYTHON_VERSION)
	@echo "$(YELLOW)Removing existing virtual environment if exists...$(NC)"
	@rm -rf $(VENV_NAME)
	@echo "$(YELLOW)Creating virtual environment...$(NC)"
	@python$(PYTHON_VERSION) -m venv $(VENV_NAME)
	@echo "$(YELLOW)Setting pyenv local...$(NC)"
	@pyenv local $(PYTHON_VERSION)
	@echo "$(YELLOW)Activating virtual environment...$(NC)"
	@source $(VENV_NAME)/bin/activate && \
	echo "$(YELLOW)Upgrading pip...$(NC)" && \
	pip install --upgrade pip && \
	echo "$(YELLOW)Installing Poetry...$(NC)" && \
	pip install poetry && \
	echo "$(YELLOW)Configuring Poetry to use virtual environment...$(NC)" && \
	poetry config virtualenvs.create false && \
	poetry config virtualenvs.in-project true && \
	echo "$(YELLOW)Installing dependencies...$(NC)" && \
	poetry install --sync --no-root
	@echo "$(GREEN)Virtual environment created successfully!$(NC)"
	@echo "$(BLUE)To activate: source $(VENV_NAME)/bin/activate$(NC)"

create-venv-aws: ## Create virtual environment for AWS/Linux
	@echo "$(BLUE)Setting up environment for AWS/Linux...$(NC)"
	@echo "$(YELLOW)Installing Python $(PYTHON_VERSION) with pyenv...$(NC)"
	@if ! command -v pyenv &> /dev/null; then \
		echo "$(RED)pyenv not found. Installing...$(NC)"; \
		curl https://pyenv.run | bash; \
		echo 'export PYENV_ROOT="$$HOME/.pyenv"' >> ~/.bashrc; \
		echo 'command -v pyenv >/dev/null || export PATH="$$PYENV_ROOT/bin:$$PATH"' >> ~/.bashrc; \
		echo 'eval "$$(pyenv init -)"' >> ~/.bashrc; \
		source ~/.bashrc; \
	fi
	@pyenv install $(PYTHON_VERSION) -s
	@echo "$(YELLOW)Setting global Python version...$(NC)"
	@pyenv global $(PYTHON_VERSION)
	@echo "$(YELLOW)Removing existing virtual environment if exists...$(NC)"
	@rm -rf $(VENV_NAME)
	@echo "$(YELLOW)Creating virtual environment...$(NC)"
	@python$(PYTHON_VERSION) -m venv $(VENV_NAME)
	@echo "$(YELLOW)Setting pyenv local...$(NC)"
	@pyenv local $(PYTHON_VERSION)
	@echo "$(YELLOW)Activating virtual environment...$(NC)"
	@source $(VENV_NAME)/bin/activate && \
	echo "$(YELLOW)Upgrading pip...$(NC)" && \
	pip install --upgrade pip && \
	echo "$(YELLOW)Installing Poetry...$(NC)" && \
	pip install poetry && \
	echo "$(YELLOW)Configuring Poetry to use virtual environment...$(NC)" && \
	poetry config virtualenvs.create false && \
	poetry config virtualenvs.in-project true && \
	echo "$(YELLOW)Installing dependencies...$(NC)" && \
	poetry install --sync --no-root
	@echo "$(GREEN)Virtual environment created successfully!$(NC)"
	@echo "$(BLUE)To activate: source $(VENV_NAME)/bin/activate$(NC)"

create-venv-wsl: ## Create virtual environment for WSL/Ubuntu
	@echo "$(BLUE)Setting up environment for WSL/Ubuntu...$(NC)"
	@echo "$(YELLOW)Installing Python $(PYTHON_VERSION) with pyenv...$(NC)"
	@if ! command -v pyenv &> /dev/null; then \
		echo "$(RED)pyenv not found. Installing...$(NC)"; \
		curl https://pyenv.run | bash; \
		echo 'export PYENV_ROOT="$$HOME/.pyenv"' >> ~/.bashrc; \
		echo 'command -v pyenv >/dev/null || export PATH="$$PYENV_ROOT/bin:$$PATH"' >> ~/.bashrc; \
		echo 'eval "$$(pyenv init -)"' >> ~/.bashrc; \
		source ~/.bashrc; \
	fi
	@pyenv install $(PYTHON_VERSION) -s
	@echo "$(YELLOW)Setting global Python version...$(NC)"
	@pyenv global $(PYTHON_VERSION)
	@echo "$(YELLOW)Removing existing virtual environment if exists...$(NC)"
	@rm -rf $(VENV_NAME)
	@echo "$(YELLOW)Creating virtual environment...$(NC)"
	@python$(PYTHON_VERSION) -m venv $(VENV_NAME)
	@echo "$(YELLOW)Setting pyenv local...$(NC)"
	@pyenv local $(PYTHON_VERSION)
	@echo "$(YELLOW)Activating virtual environment...$(NC)"
	@source $(VENV_NAME)/bin/activate && \
	echo "$(YELLOW)Upgrading pip...$(NC)" && \
	pip install --upgrade pip && \
	echo "$(YELLOW)Installing Poetry...$(NC)" && \
	pip install poetry && \
	echo "$(YELLOW)Configuring Poetry to use virtual environment...$(NC)" && \
	poetry config virtualenvs.create false && \
	poetry config virtualenvs.in-project true && \
	echo "$(YELLOW)Installing dependencies...$(NC)" && \
	poetry install --sync --no-root
	@echo "$(GREEN)Virtual environment created successfully!$(NC)"
	@echo "$(BLUE)To activate: source $(VENV_NAME)/bin/activate$(NC)"

create-venv-windows: ## Create virtual environment for Windows
	@echo "$(BLUE)Setting up environment for Windows...$(NC)"
	@echo "$(YELLOW)Installing Python $(PYTHON_VERSION) with pyenv-win...$(NC)"
	@if ! command -v pyenv &> /dev/null; then \
		echo "$(RED)pyenv-win not found. Please install it manually or use chocolatey: choco install pyenv-win$(NC)"; \
		exit 1; \
	fi
	@pyenv install $(PYTHON_VERSION) -s
	@echo "$(YELLOW)Setting global Python version...$(NC)"
	@pyenv global $(PYTHON_VERSION)
	@echo "$(YELLOW)Removing existing virtual environment if exists...$(NC)"
	@if exist $(VENV_NAME) rmdir /s /q $(VENV_NAME)
	@echo "$(YELLOW)Creating virtual environment...$(NC)"
	@python -m venv $(VENV_NAME)
	@echo "$(YELLOW)Setting pyenv local...$(NC)"
	@pyenv local $(PYTHON_VERSION)
	@echo "$(YELLOW)Activating virtual environment...$(NC)"
	@$(VENV_NAME)\Scripts\activate && \
	echo "$(YELLOW)Upgrading pip...$(NC)" && \
	python -m pip install --upgrade pip && \
	echo "$(YELLOW)Installing Poetry...$(NC)" && \
	pip install poetry && \
	echo "$(YELLOW)Configuring Poetry to use virtual environment...$(NC)" && \
	poetry config virtualenvs.create false && \
	poetry config virtualenvs.in-project true && \
	echo "$(YELLOW)Installing dependencies...$(NC)" && \
	poetry install --sync --no-root
	@echo "$(GREEN)Virtual environment created successfully!$(NC)"
	@echo "$(BLUE)To activate: $(VENV_NAME)\Scripts\activate$(NC)"

clean-venv: ## Remove virtual environment
	@echo "$(YELLOW)Removing virtual environment...$(NC)"
	@rm -rf $(VENV_NAME)
	@rm -rf .venv
	@echo "$(GREEN)Virtual environment removed!$(NC)"

install-deps: ## Install dependencies with Poetry
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	@poetry install --sync --no-root
	@echo "$(GREEN)Dependencies installed!$(NC)"

dev: ## Start development server
	@echo "$(BLUE)Starting development server...$(NC)"
	@poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	@poetry run pytest

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@poetry run pytest --cov=app --cov-report=html --cov-report=term-missing

test-file: ## Run specific test file (usage: make test-file FILE=test_users.py)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Please specify FILE parameter: make test-file FILE=test_users.py$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Running test file: $(FILE)$(NC)"
	@poetry run pytest tests/$(FILE)

ruff: ## Run ruff check and format
	@echo "$(BLUE)Running ruff check and format...$(NC)"
	@poetry run ruff check .
	@poetry run ruff format .

ruff-check: ## Run ruff check only
	@echo "$(BLUE)Running ruff check...$(NC)"
	@poetry run ruff check .

ruff-fix: ## Run ruff fix only
	@echo "$(BLUE)Running ruff fix...$(NC)"
	@poetry run ruff check --fix .

lint: ## Run all linting tools
	@echo "$(BLUE)Running linting tools...$(NC)"
	@poetry run ruff check .
	@poetry run black --check .
	@poetry run mypy app/

type-check: ## Run type checking
	@echo "$(BLUE)Running type checking...$(NC)"
	@poetry run mypy app/

format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	@poetry run black .
	@poetry run ruff format .

check-all: ## Run all checks (lint, type-check, tests)
	@echo "$(BLUE)Running all checks...$(NC)"
	@$(MAKE) lint
	@$(MAKE) type-check
	@$(MAKE) test

migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	@poetry run alembic upgrade head

migrate-up: ## Upgrade to latest migration
	@echo "$(BLUE)Upgrading to latest migration...$(NC)"
	@poetry run alembic upgrade head

migrate-down: ## Downgrade one migration
	@echo "$(BLUE)Downgrading one migration...$(NC)"
	@poetry run alembic downgrade -1

migrate-revision: ## Create new migration (usage: make migrate-revision MESSAGE="add users table")
	@if [ -z "$(MESSAGE)" ]; then \
		echo "$(RED)Please specify MESSAGE parameter: make migrate-revision MESSAGE=\"add users table\"$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Creating new migration: $(MESSAGE)$(NC)"
	@poetry run alembic revision --autogenerate -m "$(MESSAGE)"

shell: ## Open Python shell
	@echo "$(BLUE)Opening Python shell...$(NC)"
	@poetry run python

logs: ## Show application logs
	@echo "$(BLUE)Showing application logs...$(NC)"
	@tail -f logs/app.log

clean: ## Clean all generated files
	@echo "$(YELLOW)Cleaning generated files...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name "htmlcov" -exec rm -rf {} +
	@find . -type f -name ".coverage" -delete
	@echo "$(GREEN)Clean completed!$(NC)"

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	@docker build -t saas-platform-backend .

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	@docker run -p 8000:8000 saas-platform-backend

docker-compose-up: ## Start all services with Docker Compose
	@echo "$(BLUE)Starting all services...$(NC)"
	@docker-compose up -d

docker-compose-down: ## Stop all services
	@echo "$(BLUE)Stopping all services...$(NC)"
	@docker-compose down

docker-compose-logs: ## Show Docker Compose logs
	@echo "$(BLUE)Showing Docker Compose logs...$(NC)"
	@docker-compose logs -f 