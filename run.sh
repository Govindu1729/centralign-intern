#!/bin/bash
# run.sh - Quick start for Invoice Processor

echo "🚀 Starting Invoice Processor..."

# Check if virtualenv exists
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies if needed
pip install -q -r requirements.txt 2>/dev/null

# Start server in background
echo "🔌 Starting Flask Portal (http://localhost:5000)..."
python app.py &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Run agent
echo "🤖 Running Agent..."
python agent.py

# Cleanup
echo "🛑 Stopping server..."
kill $SERVER_PID
