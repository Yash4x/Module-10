.PHONY: help install test test-unit test-integration coverage run docker-up docker-down clean lint format

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install dependencies
	pip install -r requirements.txt

test:  ## Run all tests
	TESTING=1 pytest tests/ -v

test-unit:  ## Run unit tests only
	TESTING=1 pytest tests/test_unit.py -v

test-integration:  ## Run integration tests only
	TESTING=1 pytest tests/test_integration.py -v

coverage:  ## Run tests with coverage report
	TESTING=1 pytest --cov=src --cov-report=html --cov-report=term-missing

run:  ## Run the application locally
	uvicorn src.main:app --reload

docker-up:  ## Start Docker containers
	docker-compose up --build

docker-down:  ## Stop Docker containers
	docker-compose down -v

clean:  ## Clean up temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f test.db

lint:  ## Run code quality checks
	pylint src/ --errors-only
	black --check src/ tests/
	isort --check-only src/ tests/

format:  ## Format code
	black src/ tests/
	isort src/ tests/
