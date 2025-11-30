# Heart Disease Prediction - MLOps Assignment

End-to-end machine learning solution for predicting heart disease risk using modern MLOps practices.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Architecture](#architecture)
- [Components](#components)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [CI/CD Pipeline](#cicd-pipeline)

## 🎯 Overview

This project implements a complete MLOps pipeline for heart disease prediction, including:

- **Data Acquisition & EDA**: Automated data download and comprehensive exploratory analysis
- **Model Development**: Logistic Regression and Random Forest classifiers with cross-validation
- **Experiment Tracking**: MLflow integration for tracking experiments, metrics, and artifacts
- **Model Packaging**: Reproducible model and preprocessing pipeline
- **CI/CD Pipeline**: GitHub Actions workflow with linting, testing, and training
- **Containerization**: Docker container for model serving
- **Production Deployment**: Kubernetes manifests and Helm charts
- **Monitoring**: Prometheus and Grafana integration

## 📁 Project Structure

```
assignment-1/
├── src/                    # Source code
│   ├── download_data.py    # Data acquisition script
│   ├── data_preprocessing.py  # Preprocessing pipeline
│   ├── train_model.py      # Model training with MLflow
│   └── api.py              # FastAPI service
├── tests/                  # Unit tests
│   ├── test_data_preprocessing.py
│   ├── test_model.py
│   └── test_api.py
├── notebooks/              # Jupyter notebooks
│   └── 01_eda.ipynb        # Exploratory Data Analysis
├── docker/                 # Docker configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── prometheus.yml
├── k8s/                    # Kubernetes manifests
│   ├── deployment.yaml
│   └── helm/               # Helm charts
├── .github/workflows/      # CI/CD pipelines
│   └── ci_cd.yml
├── data/                   # Dataset storage
├── artifacts/              # Model artifacts
├── mlruns/                 # MLflow runs
├── screenshots/            # Documentation screenshots
└── requirements.txt        # Python dependencies
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (for containerization)
- Kubernetes cluster (for production deployment)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd assignment-1
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download dataset**
   ```bash
   python src/download_data.py
   ```

5. **Run EDA notebook** (optional)
   ```bash
   jupyter notebook notebooks/01_eda.ipynb
   ```

6. **Train models**
   ```bash
   python src/train_model.py
   ```

## 💻 Usage

### Local Development

1. **Start the API locally**
   ```bash
   python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
   ```

2. **Test the API**
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Make prediction
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
   ```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html
```

### Docker Deployment

1. **Build Docker image**
   ```bash
   docker build -t heart-disease-api:latest -f docker/Dockerfile .
   ```

2. **Run container**
   ```bash
   docker run -p 8000:8000 heart-disease-api:latest
   ```

3. **Using Docker Compose** (includes Prometheus and Grafana)
   ```bash
   cd docker
   docker-compose up -d
   ```

### Kubernetes Deployment

1. **Using kubectl**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   ```

2. **Using Helm**
   ```bash
   helm install heart-disease-api k8s/helm/
   ```

3. **Check deployment**
   ```bash
   kubectl get pods
   kubectl get services
   kubectl get ingress
   ```

## 🏗️ Architecture

```
┌─────────────────┐
│   Data Source   │
│   (UCI Repo)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Download  │
│   & Cleaning    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│   EDA & Feature │─────▶│   MLflow     │
│   Engineering   │      │  Tracking    │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│  Model Training │
│  (LR & RF)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  Model Package  │─────▶│   Docker     │
│  (MLflow)       │      │  Container   │
└────────┬────────┘      └──────┬───────┘
         │                      │
         ▼                      ▼
┌─────────────────┐      ┌──────────────┐
│  FastAPI Service│      │ Kubernetes   │
│  (/predict)     │      │  Deployment  │
└────────┬────────┘      └──────┬───────┘
         │                      │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────┐
         │  Prometheus +    │
         │  Grafana         │
         │  (Monitoring)    │
         └──────────────────┘
```

## 🔧 Components

### 1. Data Acquisition
- Automated download from UCI ML Repository
- Data cleaning and preprocessing
- Target variable binarization

### 2. Exploratory Data Analysis
- Class distribution analysis
- Feature histograms and distributions
- Correlation heatmaps
- Box plots by target variable

### 3. Model Development
- **Logistic Regression**: Baseline model with L2 regularization
- **Random Forest**: Ensemble model with hyperparameter tuning
- Cross-validation with stratified k-fold
- Metrics: Accuracy, Precision, Recall, ROC-AUC

### 4. Experiment Tracking
- MLflow integration
- Parameter logging
- Metric tracking
- Artifact storage (models, plots, preprocessors)

### 5. API Service
- FastAPI framework
- `/predict` endpoint with JSON input/output
- Input validation with Pydantic
- Health check endpoints
- Request logging

### 6. CI/CD Pipeline
- **Linting**: flake8, black, isort
- **Testing**: pytest with coverage
- **Training**: Automated model training
- **Docker Build**: Container image creation and testing

### 7. Monitoring
- Prometheus metrics endpoint
- Grafana dashboards
- API request logging
- Health check monitoring

## 📊 Model Performance

Models are evaluated using:
- **Accuracy**: Overall correctness
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **ROC-AUC**: Area under the ROC curve

Results are tracked in MLflow and can be viewed using:
```bash
mlflow ui
```

## 🔍 Monitoring

### Prometheus
- Scrapes metrics from API endpoint
- Accessible at `http://localhost:9090`

### Grafana
- Pre-configured dashboards
- Accessible at `http://localhost:3000`
- Default credentials: admin/admin

## 🧪 CI/CD Pipeline

The GitHub Actions workflow includes:

1. **Lint Job**: Code quality checks
2. **Test Job**: Unit tests with coverage
3. **Train Job**: Model training and artifact upload
4. **Build Job**: Docker image build and test

Workflow triggers on:
- Push to `main` or `develop` branches
- Pull requests to `main` branch

## 📝 API Documentation

Once the API is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints

- `GET /`: Root endpoint
- `GET /health`: Health check
- `POST /predict`: Make predictions
- `GET /metrics`: Prometheus metrics

### Example Request

```json
{
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
}
```

### Example Response

```json
{
  "prediction": 1,
  "probability": 0.85,
  "confidence": "High",
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🐛 Troubleshooting

### Model not loading
- Ensure `mlruns/` directory contains trained models
- Check `MODEL_PATH` environment variable
- Verify preprocessor is saved in `artifacts/`

### Docker build fails
- Ensure all dependencies are in `requirements.txt`
- Check that model artifacts are copied to container
- Verify Dockerfile paths are correct

### Kubernetes deployment issues
- Check pod logs: `kubectl logs <pod-name>`
- Verify service endpoints: `kubectl get endpoints`
- Check ingress configuration

## 📄 License

This project is part of an academic assignment.

## 👥 Authors

MLOps Assignment - S1-25_AIMLCZG523

## 🔗 Links

- [UCI Heart Disease Dataset](https://archive.ics.uci.edu/ml/datasets/heart+disease)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

