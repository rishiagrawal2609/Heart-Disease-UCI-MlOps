.PHONY: help install download-data train test lint format docker-build docker-run clean

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make download-data  - Download dataset"
	@echo "  make train          - Train models"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo "  make clean          - Clean generated files"

install:
	pip install -r requirements.txt

download-data:
	python src/download_data.py

train:
	python src/train_model.py

test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	black src/ tests/
	isort src/ tests/

docker-build:
	docker build -t heart-disease-api:latest -f docker/Dockerfile .

docker-run:
	docker run -p 8000:8000 heart-disease-api:latest

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

