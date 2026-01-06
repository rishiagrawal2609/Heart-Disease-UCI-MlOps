# How Prometheus Metrics Export Works

## Overview

Prometheus uses a **pull-based** model where Prometheus server scrapes metrics from your application. The `prometheus-client` library exposes metrics in Prometheus format at an HTTP endpoint.

## Architecture Flow

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   FastAPI   │         │  Prometheus  │         │   Grafana   │
│   Service   │◄────────│   Server     │────────►│  Dashboard  │
│  (Port 8000)│  Scrape │  (Port 9090) │  Query  │  (Port 3000)│
└─────────────┘         └──────────────┘         └─────────────┘
      │
      │ Exposes /metrics endpoint
      │ (Prometheus format)
      ▼
┌─────────────────────────────────────┐
│  prometheus-client library           │
│  - Counters                          │
│  - Histograms                        │
│  - Gauges                            │
└─────────────────────────────────────┘
```

## Step-by-Step Process

### 1. **Define Metrics in Your Application**

In `src/api.py`, metrics are defined using `prometheus-client`:

```python
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.openmetrics.exposition import REGISTRY

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']  # Labels for grouping
)

PREDICTION_COUNT = Counter(
    'predictions_total',
    'Total predictions made',
    ['prediction']
)

PREDICTION_DURATION = Histogram(
    'prediction_duration_seconds',
    'Time spent processing predictions',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)
```

### 2. **Record Metrics During Application Execution**

Metrics are incremented/observed as events happen:

```python
# In the /predict endpoint
PREDICTION_DURATION.observe(duration)  # Record time taken
PREDICTION_COUNT.labels(prediction=str(prediction)).inc()  # Increment counter
REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='200').inc()
```

### 3. **Expose Metrics Endpoint**

The `/metrics` endpoint generates Prometheus-formatted output:

```python
@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint"""
    REQUEST_COUNT.labels(method='GET', endpoint='/metrics', status='200').inc()
    return Response(
        content=generate_latest(REGISTRY),  # Generate Prometheus format
        media_type=CONTENT_TYPE_LATEST      # text/plain; version=0.0.4
    )
```

### 4. **Prometheus Scrapes the Endpoint**

Prometheus server (configured in `docker/prometheus.yml`) periodically scrapes:

```yaml
scrape_configs:
  - job_name: 'heart-disease-api'
    static_configs:
      - targets: ['api:8000']  # Your API service
    metrics_path: '/metrics'   # The endpoint to scrape
    scrape_interval: 15s        # How often to scrape
```

**What happens:**
1. Every 15 seconds, Prometheus makes an HTTP GET request to `http://api:8000/metrics`
2. Your API responds with metrics in Prometheus format
3. Prometheus stores the metrics in its time-series database

### 5. **Metrics Format**

The `/metrics` endpoint returns text in Prometheus format:

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/",method="GET",status="200"} 5.0
http_requests_total{endpoint="/predict",method="POST",status="200"} 12.0
http_requests_total{endpoint="/predict",method="POST",status="500"} 1.0

# HELP predictions_total Total predictions made
# TYPE predictions_total counter
predictions_total{prediction="0"} 8.0
predictions_total{prediction="1"} 5.0

# HELP prediction_duration_seconds Time spent processing predictions
# TYPE prediction_duration_seconds histogram
prediction_duration_seconds_bucket{le="0.001"} 0.0
prediction_duration_seconds_bucket{le="0.005"} 2.0
prediction_duration_seconds_bucket{le="0.01"} 8.0
prediction_duration_seconds_bucket{le="0.025"} 12.0
prediction_duration_seconds_bucket{le="0.05"} 13.0
prediction_duration_seconds_bucket{le="+Inf"} 13.0
prediction_duration_seconds_sum 0.234
prediction_duration_seconds_count 13.0
```

## Testing the Export

### 1. **Start the Services**

```bash
make docker-up
```

### 2. **Check Metrics Endpoint Directly**

```bash
curl http://localhost:8000/metrics
```

You should see Prometheus-formatted metrics.

### 3. **Verify Prometheus is Scraping**

1. Open Prometheus UI: http://localhost:9090
2. Go to **Status → Targets**
3. Check that `heart-disease-api` target is **UP**
4. If DOWN, check:
   - API is running: `curl http://localhost:8000/health`
   - Network connectivity between containers
   - Prometheus config is correct

### 4. **Query Metrics in Prometheus**

In Prometheus UI (http://localhost:9090), try these queries:

```promql
# Total HTTP requests
http_requests_total

# Requests per second
rate(http_requests_total[5m])

# Total predictions
predictions_total

# Prediction rate
rate(predictions_total[5m])

# 95th percentile prediction duration
histogram_quantile(0.95, prediction_duration_seconds)

# Average prediction duration
rate(prediction_duration_seconds_sum[5m]) / rate(prediction_duration_seconds_count[5m])
```

### 5. **Generate Some Traffic**

To see metrics change:

```bash
# Make some predictions
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

# Check health endpoint
curl http://localhost:8000/health

# Check metrics
curl http://localhost:8000/metrics | grep predictions_total
```

## Key Concepts

### Pull Model vs Push Model

- **Pull Model (Prometheus)**: Prometheus actively scrapes metrics from your app
  - Pros: Simple, no need for service discovery, centralized
  - Cons: App must be reachable, requires HTTP endpoint

- **Push Model (StatsD)**: Application pushes metrics to a collector
  - Pros: Works behind firewalls, can batch metrics
  - Cons: More complex, requires push gateway

### Metric Types

1. **Counter**: Monotonically increasing value (e.g., total requests)
   ```python
   REQUEST_COUNT.inc()  # Increment by 1
   REQUEST_COUNT.inc(5)  # Increment by 5
   ```

2. **Histogram**: Distribution of values (e.g., request duration)
   ```python
   PREDICTION_DURATION.observe(0.023)  # Record a value
   ```

3. **Gauge**: Value that can go up or down (e.g., current memory usage)
   ```python
   MEMORY_USAGE.set(512)  # Set absolute value
   MEMORY_USAGE.inc()     # Increase
   MEMORY_USAGE.dec()     # Decrease
   ```

### Labels

Labels allow you to group and filter metrics:

```python
REQUEST_COUNT.labels(method='GET', endpoint='/health', status='200').inc()
REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='200').inc()
```

This creates separate time series for each combination of labels, allowing queries like:
- `http_requests_total{method="POST"}` - All POST requests
- `http_requests_total{endpoint="/predict"}` - All prediction requests
- `http_requests_total{status="500"}` - All error requests

## Troubleshooting

### Metrics Not Appearing

1. **Check API is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check metrics endpoint:**
   ```bash
   curl http://localhost:8000/metrics
   ```

3. **Check Prometheus targets:**
   - Go to http://localhost:9090/targets
   - Verify `heart-disease-api` is UP

4. **Check Prometheus logs:**
   ```bash
   docker logs <prometheus-container-id>
   ```

5. **Verify network connectivity:**
   - In Docker Compose, services can reach each other by service name
   - `api:8000` should be reachable from Prometheus container

### Metrics Format Issues

If Prometheus can't parse metrics:
- Check `/metrics` endpoint returns `text/plain` content type
- Verify metrics follow Prometheus naming conventions (snake_case)
- Ensure metric names don't start with numbers

## Summary

1. **Application** defines metrics using `prometheus-client`
2. **Application** records metrics as events occur
3. **Application** exposes `/metrics` endpoint in Prometheus format
4. **Prometheus** scrapes `/metrics` every 15 seconds (configurable)
5. **Prometheus** stores metrics in time-series database
6. **Grafana** queries Prometheus to visualize metrics

The export happens automatically - you just need to:
- Define metrics
- Record metrics in your code
- Expose `/metrics` endpoint
- Configure Prometheus to scrape it

