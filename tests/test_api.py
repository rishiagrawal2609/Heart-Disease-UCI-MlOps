"""
Unit tests for API endpoints
"""

import os
import sys

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Create a simple mock model before importing api
mock_model = LogisticRegression(max_iter=1000, random_state=42)
mock_model.fit(np.random.randn(10, 13), np.random.randint(0, 2, 10))

# Import and mock the model
from src import api as api_module

api_module.model = mock_model
api_module.preprocessor = None

from src.api import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_health_endpoint():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_loaded" in data


def test_predict_endpoint():
    """Test predict endpoint"""
    input_data = {
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
        "thal": 1,
    }

    response = client.post("/predict", json=input_data)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "probability" in data
    assert "confidence" in data
    assert "timestamp" in data
    assert data["prediction"] in [0, 1]
    assert 0 <= data["probability"] <= 1


def test_predict_endpoint_invalid_input():
    """Test predict endpoint with invalid input"""
    invalid_data = {
        "age": -1,  # Invalid age
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
        "thal": 1,
    }

    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422  # Validation error


def test_metrics_endpoint():
    """Test metrics endpoint returns Prometheus-formatted metrics"""
    response = client.get("/metrics")
    assert response.status_code == 200
    # Metrics endpoint returns Prometheus text format, not JSON
    content_type = response.headers.get("content-type", "")
    assert content_type.startswith("text/plain")
    assert "version=0.0.4" in content_type or "charset=utf-8" in content_type
    text = response.text
    # Check for Prometheus metric format
    assert "# HELP" in text or "# TYPE" in text or "http_requests_total" in text
