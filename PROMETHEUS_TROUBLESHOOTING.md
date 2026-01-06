# Prometheus Troubleshooting Guide

## Quick Check: Is Prometheus Scraping?

1. **Check Targets Status:**
   - Go to: http://localhost:9090/targets
   - Look for `heart-disease-api` target
   - Status should be **UP** (green)

2. **Check if API is exposing metrics:**
   ```bash
   curl http://localhost:8000/metrics
   ```
   You should see Prometheus-formatted metrics.

## Why You Might Not See Data

### 1. No Traffic Generated Yet

Prometheus only shows metrics that have been recorded. If you haven't made any API requests, custom metrics won't exist yet.

**Solution:** Generate some traffic:

```bash
# Make some API calls
curl http://localhost:8000/health
curl http://localhost:8000/
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

Wait 15-30 seconds, then check Prometheus again.

### 2. Using Wrong Queries

**Basic Queries to Try:**

1. **Check if API is up:**
   ```
   up{job="heart-disease-api"}
   ```
   Should return `1` if API is running.

2. **Check HTTP requests:**
   ```
   http_requests_total
   ```
   Or with labels:
   ```
   http_requests_total{job="heart-disease-api"}
   ```

3. **Check predictions:**
   ```
   predictions_total
   ```

4. **Request rate:**
   ```
   rate(http_requests_total{job="heart-disease-api"}[5m])
   ```

5. **Prediction rate:**
   ```
   rate(predictions_total{job="heart-disease-api"}[5m])
   ```

### 3. Time Range Issue

Make sure you're looking at the right time range:
- In Prometheus UI, check the time range selector (top right)
- Try: "Last 1 hour" or "Last 5 minutes"
- If you just started services, use "Last 5 minutes"

### 4. Metrics Not Being Exposed

Check what metrics are actually available:

```bash
# List all metrics
curl http://localhost:8000/metrics | grep "^[^#]" | grep -v "^$" | cut -d' ' -f1 | sort -u
```

You should see:
- `http_requests_total`
- `predictions_total`
- `prediction_duration_seconds_*`

## Step-by-Step: View Data in Prometheus

1. **Open Prometheus UI:**
   ```
   http://localhost:9090
   ```

2. **Check Targets:**
   - Click **Status** → **Targets**
   - Verify `heart-disease-api` is **UP**

3. **Generate Traffic:**
   ```bash
   # Run this script to generate traffic
   for i in {1..10}; do
     curl http://localhost:8000/health
     curl -X POST http://localhost:8000/predict \
       -H "Content-Type: application/json" \
       -d '{"age":63,"sex":1,"cp":3,"trestbps":145,"chol":233,"fbs":1,"restecg":0,"thalach":150,"exang":0,"oldpeak":2.3,"slope":0,"ca":0,"thal":1}'
     sleep 2
   done
   ```

4. **Query Metrics:**
   - Go to **Graph** tab
   - Enter query: `http_requests_total{job="heart-disease-api"}`
   - Click **Execute**
   - You should see data points

5. **View as Graph:**
   - Click **Graph** tab
   - Enter query: `rate(http_requests_total{job="heart-disease-api"}[5m])`
   - Click **Execute**
   - You should see a graph

## Common Queries

### Basic Metrics
```promql
# API availability
up{job="heart-disease-api"}

# Total HTTP requests
http_requests_total{job="heart-disease-api"}

# Requests by endpoint
http_requests_total{job="heart-disease-api", endpoint="/predict"}

# Requests by status
http_requests_total{job="heart-disease-api", status="200"}
```

### Rate Metrics
```promql
# Request rate (requests per second)
rate(http_requests_total{job="heart-disease-api"}[5m])

# Prediction rate
rate(predictions_total{job="heart-disease-api"}[5m])
```

### Duration Metrics
```promql
# Average prediction duration
rate(prediction_duration_seconds_sum{job="heart-disease-api"}[5m]) / 
rate(prediction_duration_seconds_count{job="heart-disease-api"}[5m])

# 95th percentile duration
histogram_quantile(0.95, 
  rate(prediction_duration_seconds_bucket{job="heart-disease-api"}[5m])
)
```

### Aggregations
```promql
# Total requests across all endpoints
sum(http_requests_total{job="heart-disease-api"})

# Requests per endpoint
sum by (endpoint) (http_requests_total{job="heart-disease-api"})

# Predictions by class
sum by (prediction) (predictions_total{job="heart-disease-api"})
```

## Still Not Working?

1. **Check Prometheus logs:**
   ```bash
   docker logs $(docker ps -q -f "name=prometheus")
   ```

2. **Check API logs:**
   ```bash
   docker logs $(docker ps -q -f "name=api")
   ```

3. **Verify network connectivity:**
   ```bash
   # From Prometheus container
   docker exec $(docker ps -q -f "name=prometheus") wget -O- http://api:8000/metrics
   ```

4. **Restart services:**
   ```bash
   make docker-down
   make docker-up
   ```

5. **Check Prometheus config:**
   ```bash
   docker exec $(docker ps -q -f "name=prometheus") cat /etc/prometheus/prometheus.yml
   ```

## Quick Test Script

Save this as `test_metrics.sh`:

```bash
#!/bin/bash
echo "Generating traffic for Prometheus metrics..."

# Generate 20 requests
for i in {1..20}; do
  echo "Request $i..."
  curl -s http://localhost:8000/health > /dev/null
  curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"age":63,"sex":1,"cp":3,"trestbps":145,"chol":233,"fbs":1,"restecg":0,"thalach":150,"exang":0,"oldpeak":2.3,"slope":0,"ca":0,"thal":1}' > /dev/null
  sleep 1
done

echo "Done! Wait 15-30 seconds, then check Prometheus:"
echo "  http://localhost:9090"
echo ""
echo "Try these queries:"
echo "  - http_requests_total{job=\"heart-disease-api\"}"
echo "  - predictions_total{job=\"heart-disease-api\"}"
echo "  - rate(http_requests_total{job=\"heart-disease-api\"}[5m])"
```

Run it:
```bash
chmod +x test_metrics.sh
./test_metrics.sh
```

