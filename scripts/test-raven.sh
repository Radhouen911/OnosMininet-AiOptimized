#!/bin/bash
# Test script for RAVEN controller

echo "==================================="
echo "RAVEN Controller Test Script"
echo "==================================="
echo ""

# Check if containers are running
echo "1. Checking container status..."
docker-compose ps

echo ""
echo "2. Waiting for ONOS to be ready..."
sleep 5

# Check ONOS connectivity
echo ""
echo "3. Testing ONOS API..."
curl -s -u onos:rocks http://localhost:8181/onos/v1/applications | grep -q "applications" && echo "✓ ONOS API is responding" || echo "✗ ONOS API not ready"

echo ""
echo "4. Checking RAVEN controller logs..."
docker logs --tail 20 raven-controller

echo ""
echo "==================================="
echo "To run test topology:"
echo "  docker exec -it mininet bash"
echo "  service openvswitch-switch start"
echo "  python3 /topologies/raven_test_topology.py"
echo ""
echo "To monitor RAVEN:"
echo "  docker logs -f raven-controller"
echo ""
echo "To view ONOS GUI:"
echo "  http://localhost:8181/onos/ui (onos/rocks)"
echo "==================================="
