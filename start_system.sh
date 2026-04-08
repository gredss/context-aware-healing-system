#!/bin/bash

# Context-Aware Healing System - Complete System Startup Script
# This script starts both the healer agent and the web dashboard

echo "🚀 Starting Context-Aware Healing System..."
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your IBM Watsonx credentials:"
    echo "   - WATSONX_API_KEY"
    echo "   - WATSONX_PROJECT_ID"
    echo ""
    echo "Get your API key from: https://cloud.ibm.com/iam/apikeys"
    echo ""
    read -p "Press Enter after updating .env file to continue..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🎯 Starting Web Dashboard and Healer Agent..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Dashboard will be available at: http://localhost:8000"
echo "🤖 Healer Agent will run in the background"
echo ""
echo "Press Ctrl+C to stop the system"
echo ""

# Start the FastAPI application (which includes the agent)
python -m uvicorn ui.app:app --host 0.0.0.0 --port 8000 --reload

# Made with Bob
