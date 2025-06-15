.PHONY: help test test-unit test-integration test-e2e test-all test-cov lint format security clean install

help: ## Mostrar ayuda
	@echo "Comandos disponibles:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Instalar dependencias
	pip install -r requirements.txt
	pip install pytest-cov pytest-asyncio bandit safety black isort flake8 mypy

test-unit: ## Ejecutar tests unitarios
	pytest tests/unit/ -v

test-integration: ## Ejecutar tests de integración
	pytest tests/integration/ -v -m integration

test-e2e: ## Ejecutar tests end-to-end
	pytest tests/e2e/ -v -m e2e

test: ## Ejecutar todos los tests
	pytest tests/ -v

test-cov: ## Ejecutar tests con cobertura
	pytest --cov=app --cov-report=term-missing --cov-report=html

test-all: test-unit test-integration test-e2e ## Ejecutar todos los tipos de tests

lint: ## Verificar calidad del código
	black --check app/ tests/
	isort --check-only app/ tests/
	flake8 app/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	mypy app/ --ignore-missing-imports

format: ## Formatear código
	black app/ tests/
	isort app/ tests/

security: ## Análisis de seguridad
	bandit -r app/ -f json -o bandit-report.json
	safety check

clean: ## Limpiar archivos temporales
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf bandit-report.json
	rm -rf safety-report.json
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

dev-setup: ## Configurar entorno de desarrollo
	python -m venv .venv
	source .venv/bin/activate && pip install -r requirements.txt
	source .venv/bin/activate && pip install pytest-cov pytest-asyncio bandit safety black isort flake8 mypy

run: ## Ejecutar la aplicación
	uvicorn app.main:app --reload

docker-test: ## Ejecutar tests en Docker
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

ci: lint security test-cov ## Pipeline completo de CI