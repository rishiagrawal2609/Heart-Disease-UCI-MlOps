#!/bin/bash
# End-to-end pipeline execution script

set -e  # Exit on error

echo "=========================================="
echo "Heart Disease Prediction - MLOps Pipeline"
echo "=========================================="

# Step 1: Download data
echo ""
echo "Step 1: Downloading dataset..."
python src/download_data.py

# Step 2: Train models
echo ""
echo "Step 2: Training models..."
python src/train_model.py

# Step 3: Run tests
echo ""
echo "Step 3: Running tests..."
pytest tests/ -v

# Step 4: Build Docker image
echo ""
echo "Step 4: Building Docker image..."
docker build -t heart-disease-api:latest -f docker/Dockerfile .

# Step 5: Test Docker container
echo ""
echo "Step 5: Testing Docker container..."
docker run -d -p 8000:8000 --name test-api heart-disease-api:latest
sleep 10

# Health check
if curl -f http://localhost:8000/health; then
    echo "✓ API is healthy"
else
    echo "✗ API health check failed"
    docker logs test-api
    docker stop test-api
    docker rm test-api
    exit 1
fi

# Test prediction
echo ""
echo "Testing prediction endpoint..."
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 63,
    "sex": 1,
    "cp": 3,
    "trestbps": 145,
    "chol": 233,
    "fbs": 1,
    "restecg": 0,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 2.3,
    "slope": 0,
    "ca": 0,
    "thal": 1
  }'

echo ""
echo "=========================================="
echo "Pipeline completed successfully!"
echo "=========================================="

# Cleanup
docker stop test-api
docker rm test-api

