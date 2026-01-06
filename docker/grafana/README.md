# Grafana Dashboard Setup

## Quick Start

1. **Start all services:**
   ```bash
   make docker-up
   ```

2. **Access Grafana:**
   - URL: http://localhost:3000
   - Username: `admin`
   - Password: `admin`

3. **View Dashboard:**
   - Go to **Dashboards** → **Browse**
   - Look for **"Heart Disease API Monitoring"**

## Troubleshooting

### Dashboard Not Appearing

1. **Check Grafana logs:**
   ```bash
   docker logs <grafana-container-id>
   ```

2. **Verify dashboard file exists:**
   ```bash
   docker exec <grafana-container-id> ls -la /etc/grafana/provisioning/dashboards/
   ```

3. **Restart Grafana:**
   ```bash
   make docker-down
   make docker-up
   ```

### Datasource Not Working

1. **Check Prometheus is running:**
   ```bash
   curl http://localhost:9090/api/v1/status/config
   ```

2. **Verify datasource in Grafana:**
   - Go to **Configuration** → **Data Sources**
   - Check that Prometheus datasource is configured
   - Click **Test** to verify connection

3. **Check network connectivity:**
   - In Grafana container, Prometheus should be reachable at `http://prometheus:9090`

### No Data in Dashboard

1. **Verify metrics are being exposed:**
   ```bash
   curl http://localhost:8000/metrics
   ```

2. **Check Prometheus is scraping:**
   - Go to http://localhost:9090/targets
   - Verify `heart-disease-api` target is **UP**

3. **Generate some traffic:**
   ```bash
   curl http://localhost:8000/health
   curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{...}'
   ```

4. **Query metrics in Prometheus:**
   - Go to http://localhost:9090
   - Try query: `up{job="heart-disease-api"}`
   - Try query: `http_requests_total`

### Manual Dashboard Import

If automatic provisioning doesn't work:

1. **Export dashboard JSON:**
   - The dashboard file is at: `docker/grafana/provisioning/dashboards/heart-disease-api.json`
   - Extract the `dashboard` object content

2. **Import in Grafana UI:**
   - Go to **Dashboards** → **Import**
   - Paste the dashboard JSON
   - Select Prometheus datasource
   - Click **Import**

## Dashboard Panels

The dashboard includes:

1. **API Health Status** - Shows if API is up (1) or down (0)
2. **HTTP Requests Rate** - Requests per second over time
3. **Total Predictions by Class** - Count of predictions by class (0 or 1)
4. **Prediction Duration** - 95th percentile prediction time

## Metrics Required

The dashboard queries these metrics:
- `up{job="heart-disease-api"}` - API availability
- `rate(http_requests_total{job="heart-disease-api"}[5m])` - Request rate
- `sum(predictions_total{job="heart-disease-api"}) by (prediction)` - Prediction counts
- `histogram_quantile(0.95, rate(prediction_duration_seconds_bucket{job="heart-disease-api"}[5m]))` - Duration

Make sure your API is exposing these metrics at `/metrics` endpoint.

