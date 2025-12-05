#!/bin/bash
# Check system status

echo "🔍 Checking LeetCode Study Plan System Status..."
echo ""

# Check Docker
echo "1. Docker Status:"
if docker info > /dev/null 2>&1; then
    echo "   ✅ Docker is running"
else
    echo "   ❌ Docker is not running"
    exit 1
fi

# Check containers
echo ""
echo "2. Container Status:"
docker-compose ps

# Check port
echo ""
echo "3. Port Status:"
CONFIGURED_PORT=$(grep -oE '"[0-9]+:5000"' docker-compose.yml | grep -oE '[0-9]+' | head -1)
if [ -z "$CONFIGURED_PORT" ]; then
    CONFIGURED_PORT=5001
fi

if lsof -i :$CONFIGURED_PORT > /dev/null 2>&1; then
    echo "   ✅ Port $CONFIGURED_PORT is in use"
    echo "   Process: $(lsof -i :$CONFIGURED_PORT | tail -1 | awk '{print $1}')"
else
    echo "   ❌ Port $CONFIGURED_PORT is not in use"
fi

# Test connection
echo ""
echo "4. Testing Connection:"
if curl -s -o /dev/null -w "   HTTP Status: %{http_code}\n" http://localhost:$CONFIGURED_PORT/; then
    echo "   ✅ Application is responding"
else
    echo "   ❌ Application is not responding"
fi

# Show access URL
echo ""
echo "5. Access Information:"
echo "   📱 URL: http://localhost:$CONFIGURED_PORT"
echo "   📱 Alternative: http://127.0.0.1:$CONFIGURED_PORT"
echo ""

# Show recent logs
echo "6. Recent Logs (last 10 lines):"
docker-compose logs --tail=10 2>/dev/null || echo "   No logs available"

echo ""
echo "💡 If you can't access the site:"
echo "   1. Make sure you're using the correct port: $CONFIGURED_PORT"
echo "   2. Try: http://127.0.0.1:$CONFIGURED_PORT"
echo "   3. Clear browser cache and try again"
echo "   4. Check if firewall is blocking the connection"
echo "   5. View full logs: docker-compose logs -f"

