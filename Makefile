.PHONY: help install download-data eda train test lint format docker-build docker-run mlflow prometheus grafana docker-up docker-down clean pipeline pipeline-full jenkins jenkins-up jenkins-down jenkins-logs jenkins-password

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make download-data  - Download dataset"
	@echo "  make eda            - Run Exploratory Data Analysis"
	@echo "  make train          - Train models"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo "  make mlflow         - Start MLflow UI on port 10800"
	@echo "  make prometheus     - Start Prometheus on port 9090"
	@echo "  make grafana        - Start Grafana on port 3000"
	@echo "  make docker-up      - Start all services (API, Prometheus, Grafana, MLflow)"
	@echo "  make docker-down    - Stop all services"
	@echo "  make test-metrics   - Generate test traffic for Prometheus metrics"
	@echo "  make jenkins        - Start Jenkins server on port 8080"
	@echo "  make jenkins-up     - Start Jenkins server"
	@echo "  make jenkins-down   - Stop Jenkins server"
	@echo "  make jenkins-logs   - View Jenkins logs"
	@echo "  make jenkins-password - Get Jenkins initial admin password"
	@echo "  make jenkins-plugins - Check installed Jenkins plugins"
	@echo "  make pipeline       - Run complete end-to-end pipeline (data, EDA, train, test, docker)"
	@echo "  make pipeline-full  - Run full pipeline with code quality checks"
	@echo "  make clean          - Clean generated files"

install:
	pip install -r requirements.txt

download-data:
	python src/download_data.py

eda:
	python src/eda.py

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

mlflow:
	mlflow ui --port 10800 --backend-store-uri file://./mlruns

prometheus:
	cd docker && docker-compose up -d prometheus
	@echo "Prometheus started at http://localhost:9090"

grafana:
	cd docker && docker-compose up -d grafana
	@echo "Grafana started at http://localhost:3000 (admin/admin)"

docker-up:
	cd docker && docker-compose up -d
	@echo "All services started:"
	@echo "  - API: http://localhost:8000"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - Grafana: http://localhost:3000 (admin/admin)"
	@echo "  - MLflow: http://localhost:10800"

docker-down:
	cd docker && docker-compose down

jenkins:
	@echo "Starting Jenkins server..."
	cd docker && docker-compose -f docker-compose.jenkins.yml up -d
	@sleep 5
	@echo ""
	@echo "=========================================="
	@echo "Jenkins is starting..."
	@echo "=========================================="
	@echo "Access Jenkins at: http://localhost:8080"
	@echo ""
	@echo "To get the initial admin password, run:"
	@echo "  make jenkins-password"
	@echo ""
	@echo "Or manually:"
	@echo "  docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword"
	@echo ""
	@echo "Jenkins will be ready in about 1-2 minutes"

jenkins-up: jenkins

jenkins-down:
	@echo "Stopping Jenkins server..."
	cd docker && docker-compose -f docker-compose.jenkins.yml down
	@echo "Jenkins stopped"

jenkins-logs:
	@echo "Viewing Jenkins logs (Ctrl+C to exit)..."
	cd docker && docker-compose -f docker-compose.jenkins.yml logs -f jenkins

jenkins-password:
	@echo "Jenkins initial admin password:"
	@docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null || echo "Jenkins container not running. Start it with: make jenkins"

jenkins-plugins:
	@echo "Checking installed Jenkins plugins..."
	@docker exec jenkins ls /var/jenkins_home/plugins/ 2>/dev/null | wc -l | xargs echo "Total plugins installed:" || echo "Jenkins container not running"
	@echo ""
	@echo "To see all plugins, run:"
	@echo "  docker exec jenkins ls /var/jenkins_home/plugins/"

test-metrics:
	@echo "Generating traffic for Prometheus metrics..."
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		echo "Request $$i..."; \
		curl -s http://localhost:8000/health > /dev/null; \
		curl -s -X POST http://localhost:8000/predict \
		  -H "Content-Type: application/json" \
		  -d '{"age":63,"sex":1,"cp":3,"trestbps":145,"chol":233,"fbs":1,"restecg":0,"thalach":150,"exang":0,"oldpeak":2.3,"slope":0,"ca":0,"thal":1}' > /dev/null; \
		sleep 1; \
	done
	@echo ""
	@echo "✓ Generated 10 health checks and 10 predictions"
	@echo "Wait 15-30 seconds, then check Prometheus: http://localhost:9090"
	@echo ""
	@echo "Try these queries:"
	@echo "  - http_requests_total{job=\"heart-disease-api\"}"
	@echo "  - predictions_total{job=\"heart-disease-api\"}"
	@echo "  - rate(http_requests_total{job=\"heart-disease-api\"}[5m])"

pipeline:
	@echo "=========================================="
	@echo "Heart Disease Prediction - End-to-End Pipeline"
	@echo "=========================================="
	@echo ""
	@echo "Step 1/7: Downloading dataset..."
	@$(MAKE) download-data
	@echo ""
	@echo "Step 2/7: Running Exploratory Data Analysis..."
	@$(MAKE) eda || echo "Warning: EDA step failed, continuing..."
	@echo ""
	@echo "Step 3/7: Training models..."
	@$(MAKE) train
	@echo ""
	@echo "Step 4/7: Running tests..."
	@$(MAKE) test
	@echo ""
	@echo "Step 5/7: Building Docker image..."
	@$(MAKE) docker-build
	@echo ""
	@echo "Step 6/7: Testing Docker container..."
	@docker run -d -p 8000:8000 --name test-api heart-disease-api:latest || true
	@sleep 10
	@echo "Testing health endpoint..."
	@curl -f http://localhost:8000/health && echo "✓ API is healthy" || (echo "✗ API health check failed"; docker logs test-api; docker stop test-api 2>/dev/null || true; docker rm test-api 2>/dev/null || true; exit 1)
	@echo "Testing prediction endpoint..."
	@curl -X POST http://localhost:8000/predict \
	  -H "Content-Type: application/json" \
	  -d '{"age":63,"sex":1,"cp":3,"trestbps":145,"chol":233,"fbs":1,"restecg":0,"thalach":150,"exang":0,"oldpeak":2.3,"slope":0,"ca":0,"thal":1}' \
	  && echo "" && echo "✓ Prediction endpoint working"
	@docker stop test-api 2>/dev/null || true
	@docker rm test-api 2>/dev/null || true
	@echo ""
	@echo "Step 7/7: Starting all services..."
	@$(MAKE) docker-up
	@echo ""
	@echo "=========================================="
	@echo "✓ Pipeline completed successfully!"
	@echo "=========================================="
	@echo ""
	@echo "All services are now running:"
	@echo "  - API: http://localhost:8000"
	@echo "  - API Docs: http://localhost:8000/docs"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - Grafana: http://localhost:3000 (admin/admin)"
	@echo "  - MLflow: http://localhost:10800"
	@echo ""
	@echo "To stop services: make docker-down"

pipeline-full: format lint pipeline
	@echo ""
	@echo "=========================================="
	@echo "✓ Full pipeline with code quality checks completed!"
	@echo "=========================================="

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

