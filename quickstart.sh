#!/bin/bash

echo "=========================================="
echo "Provider Validation System - Quick Start"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "⚠️  WARNING: Please add your OpenAI API key to .env file"
    echo "   (Optional for demo - system will work with simulated data)"
fi

echo ""

# Generate data
if [ ! -f "data/providers.json" ]; then
    echo "🔄 Generating synthetic provider data..."
    python3 generate_data.py
    echo "✅ Data generated"
else
    echo "✅ Provider data already exists"
fi

echo ""

# Generate diagrams
echo "📊 Generating architecture diagrams..."
python3 create_diagrams.py
echo "✅ Diagrams created in docs/ folder"

echo ""

# Run validation demo
echo "🚀 Running validation demo..."
python3 orchestrator.py

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the web dashboard:"
echo "  python3 app.py"
echo ""
echo "Then open your browser to:"
echo "  http://localhost:5000"
echo ""
echo "=========================================="
