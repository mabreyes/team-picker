# Team Picker Development Makefile
.PHONY: help install install-dev setup-pre-commit test test-only test-watch test-coverage test-clean lint format check clean run

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
	@echo ""
	@echo "Testing Commands:"
	@echo "  test             Run all tests with coverage"
	@echo "  test-only        Run tests without coverage"
	@echo "  test-watch       Run tests in watch mode"
	@echo "  test-coverage    Run tests and generate coverage reports"
	@echo "  test-clean       Clean test artifacts and cache"
	@echo ""
	@echo "Quality Commands:"
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

# Testing commands
test: test-coverage
	@echo "All tests completed with coverage!"

test-only:
	@echo "Running tests without coverage..."
	pytest tests/ -v

test-watch:
	@echo "Running tests in watch mode (press Ctrl+C to stop)..."
	pytest-watch tests/ -- -v

test-coverage:
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml --cov-fail-under=95
	@echo "Coverage reports generated:"
	@echo "  - HTML: htmlcov/index.html"
	@echo "  - XML: coverage.xml"
	@echo "  - Terminal: displayed above"

test-clean:
	@echo "Cleaning test artifacts..."
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -f .coverage
	rm -f coverage.xml
	rm -rf .tox/
	rm -rf .nox/
	find tests/ -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find tests/ -type f -name "*.pyc" -delete
	@echo "Test artifacts cleaned!"

# Quality commands
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
clean: test-clean
	@echo "Cleaning up generated files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache/
	rm -rf dist/
	rm -rf build/
	rm -f bandit-report.json
	rm -f safety-report.json
	rm -rf output/
	rm -rf uploads/
	rm -f debug_flask.py
	rm -f temp_*
	rm -f *_backup.*
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
