# Deployment Guide

This guide provides detailed instructions for deploying the Heart Disease Prediction API.

## Table of Contents

1. [Local Deployment](#local-deployment)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Monitoring Setup](#monitoring-setup)

## Local Deployment

### Prerequisites
- Python 3.9+
- Virtual environment

### Steps

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download and prepare data**
   ```bash
   python src/download_data.py
   ```

3. **Train models**
   ```bash
   python src/train_model.py
   ```

4. **Start API server**
   ```bash
   python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
   ```

5. **Verify deployment**
   ```bash
   curl http://localhost:8000/health
   ```

## Docker Deployment

### Build Image

```bash
docker build -t heart-disease-api:latest -f docker/Dockerfile .
```

### Run Container

```bash
docker run -p 8000:8000 heart-disease-api:latest
```

### Using Docker Compose

The docker-compose setup includes the API, Prometheus, and Grafana:

```bash
cd docker
docker-compose up -d
```

Services:
- API: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (Minikube, GKE, EKS, AKS, or Docker Desktop)
- kubectl configured
- Helm 3.x (optional, for Helm deployment)

### Using kubectl

1. **Apply deployment**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   ```

2. **Check status**
   ```bash
   kubectl get pods
   kubectl get services
   kubectl get ingress
   ```

3. **Get service URL**
   ```bash
   # For LoadBalancer
   kubectl get service heart-disease-api-service
   
   # For Ingress
   kubectl get ingress heart-disease-api-ingress
   ```

4. **Port forward (for testing)**
   ```bash
   kubectl port-forward service/heart-disease-api-service 8000:80
   ```

### Using Helm

1. **Install chart**
   ```bash
   helm install heart-disease-api k8s/helm/
   ```

2. **Upgrade deployment**
   ```bash
   helm upgrade heart-disease-api k8s/helm/
   ```

3. **Uninstall**
   ```bash
   helm uninstall heart-disease-api
   ```

### Minikube Setup

1. **Start Minikube**
   ```bash
   minikube start
   ```

2. **Enable ingress**
   ```bash
   minikube addons enable ingress
   ```

3. **Deploy application**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   ```

4. **Get service URL**
   ```bash
   minikube service heart-disease-api-service
   ```

### Docker Desktop Kubernetes

1. **Enable Kubernetes** in Docker Desktop settings

2. **Deploy application**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   ```

3. **Access service**
   ```bash
   kubectl port-forward service/heart-disease-api-service 8000:80
   ```

## Monitoring Setup

### Prometheus

Prometheus is configured to scrape metrics from the API:

1. **Access Prometheus UI**
   - Local: http://localhost:9090
   - Kubernetes: Port-forward the Prometheus service

2. **Query metrics**
   - Example: `up{job="heart-disease-api"}`

### Grafana

1. **Access Grafana**
   - URL: http://localhost:3000
   - Default credentials: admin/admin

2. **Configure datasource**
   - Prometheus is pre-configured in docker-compose setup

3. **Create dashboards**
   - Import pre-built dashboards or create custom ones

### API Metrics

The API exposes metrics at `/metrics` endpoint:

```bash
curl http://localhost:8000/metrics
```

## Troubleshooting

### Container Issues

1. **Check logs**
   ```bash
   docker logs <container-id>
   ```

2. **Verify model files**
   ```bash
   docker exec <container-id> ls -la mlruns/
   docker exec <container-id> ls -la artifacts/
   ```

### Kubernetes Issues

1. **Check pod status**
   ```bash
   kubectl describe pod <pod-name>
   ```

2. **View logs**
   ```bash
   kubectl logs <pod-name>
   ```

3. **Check events**
   ```bash
   kubectl get events --sort-by='.lastTimestamp'
   ```

### Model Loading Issues

1. **Verify model path**
   - Check `MODEL_PATH` environment variable
   - Ensure model artifacts are in container/image

2. **Check preprocessor**
   - Verify `PREPROCESSOR_PATH` is correct
   - Ensure preprocessor.pkl exists

## Production Considerations

1. **Resource Limits**
   - Adjust CPU/memory limits in deployment.yaml
   - Monitor resource usage

2. **Scaling**
   - Use HorizontalPodAutoscaler for auto-scaling
   - Configure based on metrics

3. **Security**
   - Use secrets for sensitive data
   - Enable TLS/HTTPS
   - Implement authentication

4. **High Availability**
   - Deploy multiple replicas
   - Use load balancer
   - Configure health checks

5. **Monitoring**
   - Set up alerting rules
   - Monitor API latency
   - Track prediction accuracy

## Screenshots

After deployment, capture screenshots of:
- Kubernetes dashboard showing running pods
- Service endpoints
- Ingress configuration
- Prometheus metrics
- Grafana dashboards
- API health checks
- Sample predictions

Store screenshots in the `screenshots/` directory.

