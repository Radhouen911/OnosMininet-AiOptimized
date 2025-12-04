#!/bin/bash
# Setup script for ONOS + Mininet environment

echo "Building and starting containers..."
docker-compose up -d

echo "Waiting for ONOS to start (this may take 1-2 minutes)..."
sleep 60

echo "Checking ONOS status..."
curl -s http://localhost:8181/onos/v1/applications -u onos:rocks | grep -q "applications" && echo "✓ ONOS is running" || echo "✗ ONOS not ready yet"

echo ""
echo "Environment is ready!"
echo ""
echo "Access ONOS GUI: http://localhost:8181/onos/ui (onos/rocks)"
echo "Run Mininet: docker exec -it mininet bash"
echo ""
