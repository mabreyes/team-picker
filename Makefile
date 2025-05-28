# Team Picker Development Makefile
.PHONY: help install install-dev setup-pre-commit test lint format check clean run

# Default target
help:
	@echo "Team Picker Development Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  setup-pre-commit Install and setup pre-commit hooks"
	@echo ""
	@echo "Development Commands:"
	@echo "  run              Start the Flask development server"
	@echo "  test             Run all tests"
	@echo "  lint             Run all linting checks"
	@echo "  format           Format all code"
	@echo "  check            Run all quality checks (lint + test)"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  clean            Clean up generated files"
	@echo "  update-deps      Update all dependencies"
	@echo ""

# Installation commands
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	@echo "Development dependencies installed!"

setup-pre-commit: install-dev
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "Pre-commit hooks installed!"
	@echo "Run 'make check' to verify everything is working"

# Development commands
run:
	python app.py

test:
	@echo "Running tests..."
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

lint:
	@echo "Running linting checks..."
	@echo "1. Checking Python code with flake8..."
	flake8 .
	@echo "2. Checking Python imports with isort..."
	isort --check-only --diff .
	@echo "3. Checking Python formatting with black..."
	black --check --diff .
	@echo "4. Running security checks with bandit..."
	bandit -r . -f json -o bandit-report.json || true
	@echo "5. Running type checks with mypy..."
	mypy . || true
	@echo "6. Checking JavaScript/CSS with prettier..."
	npx prettier --check "static/**/*.{js,css}" "templates/**/*.html" || true

format:
	@echo "Formatting code..."
	@echo "1. Formatting Python code with black..."
	black .
	@echo "2. Sorting Python imports with isort..."
	isort .
	@echo "3. Formatting JavaScript/CSS with prettier..."
	npx prettier --write "static/**/*.{js,css}" "templates/**/*.html" || true

check: lint test
	@echo "All quality checks completed!"

# Maintenance commands
clean:
	@echo "Cleaning up generated files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -f bandit-report.json
	rm -rf output/
	rm -rf uploads/
	@echo "Cleanup completed!"

update-deps:
	@echo "Updating dependencies..."
	pip install --upgrade pip
	pip install --upgrade -e ".[dev]"
	pre-commit autoupdate
	@echo "Dependencies updated!"

# Pre-commit commands
pre-commit-run:
	pre-commit run --all-files

pre-commit-update:
	pre-commit autoupdate

# Docker commands (if needed in the future)
docker-build:
	docker build -t team-picker .

docker-run:
	docker run -p 8000:8000 team-picker

# Git helpers
git-setup:
	git config --local core.autocrlf false
	git config --local core.eol lf
	@echo "Git configuration updated for consistent line endings"
