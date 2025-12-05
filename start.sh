#!/bin/bash
# Startup script

# Check if running with sudo (not recommended)
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Warning: Running with sudo is not recommended"
    echo "   This can cause Docker credential issues."
    echo "   Please run without sudo: ./start.sh"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🚀 Starting LeetCode Study Plan System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running, please start Docker first"
    exit 1
fi

# Check if port 5000 is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if the configured port is in use
CONFIGURED_PORT=$(grep -oP '"\K[0-9]+(?=:5000)' docker-compose.yml | head -1)
if [ -z "$CONFIGURED_PORT" ]; then
    CONFIGURED_PORT=5001
fi

if check_port $CONFIGURED_PORT; then
    echo "⚠️  Port $CONFIGURED_PORT is already in use"
    echo "   Finding an available port..."
    
    # Find an available port
    PORT_FOUND=false
    for p in 5001 5002 5003 5004 5005 5006 5007 5008 5009 5010; do
        if ! check_port $p; then
            NEW_PORT=$p
            PORT_FOUND=true
            echo "✅ Using port $NEW_PORT instead"
            # Update docker-compose.yml
            sed -i.bak "s/\"$CONFIGURED_PORT:5000\"/\"$NEW_PORT:5000\"/" docker-compose.yml
            CONFIGURED_PORT=$NEW_PORT
            break
        fi
    done
    
    if [ "$PORT_FOUND" = false ]; then
        echo "❌ Could not find an available port (tried 5001-5010)"
        echo "   Please free up a port or modify docker-compose.yml manually"
        exit 1
    fi
fi

# Stop and remove existing containers
echo "🛑 Stopping existing containers (if any)..."
docker-compose down 2>/dev/null || true

# Clean up any orphaned containers
echo "🧹 Cleaning up..."
docker-compose rm -f 2>/dev/null || true

# Restore docker-compose.yml if it was modified
if [ -f docker-compose.yml.bak ]; then
    mv docker-compose.yml.bak docker-compose.yml
fi

# Test Docker Hub connectivity by trying to pull the base image
echo "📡 Checking Docker Hub connectivity..."
if docker pull python:3.11-slim > /dev/null 2>&1; then
    echo "✅ Docker Hub connection OK"
else
    echo "⚠️  Warning: Cannot pull from Docker Hub"
    echo "   This might be a network or credentials issue."
    echo "   Trying to continue with cached images..."
fi

# Build and start containers
echo "🔨 Building and starting containers..."
if docker-compose up -d --build; then
    echo ""
    echo "✅ System started successfully!"
    echo "📱 Access at: http://localhost:$CONFIGURED_PORT"
    echo ""
    echo "Useful commands:"
    echo "  View logs:    docker-compose logs -f"
    echo "  Stop service: ./stop.sh or docker-compose down"
    echo "  Restart:      docker-compose restart"
else
    echo ""
    echo "❌ Failed to start the system"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Make sure Docker Desktop is running"
    echo "  2. ⚠️  IMPORTANT: Don't use sudo! Run: ./start.sh (not sudo ./start.sh)"
    echo "  3. Check if port is still in use: lsof -i :$CONFIGURED_PORT"
    echo "  4. Run locally instead: ./run-local.sh"
    echo ""
    exit 1
fi
