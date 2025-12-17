#!/bin/bash

echo "🔄 Restarting Provider Validation System..."

# Kill any existing Flask processes on port 5000
echo "Stopping existing server..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || true

# Wait a moment
sleep 1

# Activate virtual environment and start server
echo "Starting server..."
cd "$(dirname "$0")"
source venv/bin/activate
python3 app.py
