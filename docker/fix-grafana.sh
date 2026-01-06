#!/bin/bash
# Script to fix Grafana datasource provisioning issue

echo "Fixing Grafana datasource provisioning issue..."

# Stop services
echo "Stopping services..."
cd "$(dirname "$0")"
docker-compose down

# Remove Grafana volume to clear corrupted state
echo "Removing Grafana volume..."
docker volume rm docker_grafana_data 2>/dev/null || true
docker volume rm assignment-1_grafana_data 2>/dev/null || true

# Remove any existing Grafana containers
echo "Removing Grafana containers..."
docker rm -f $(docker ps -aq -f "name=grafana") 2>/dev/null || true

# Start services
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check Grafana logs
echo ""
echo "Checking Grafana status..."
docker-compose logs grafana | tail -20

echo ""
echo "Grafana should now be running at http://localhost:3000"
echo "Login: admin/admin"

