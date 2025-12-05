#!/bin/bash
# Run locally without Docker

echo "🚀 Starting LeetCode Study Plan System (Local Mode)..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create data directory
mkdir -p data

# Start the application
echo ""
echo "✅ Starting application..."
echo "📱 Access at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python app.py

