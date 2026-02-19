#!/bin/bash

# 🐼 Chinese Learning Web App - One-step Setup & Run
# Usage: bash setup.sh

set -e

echo "🐼 Chinese Learning Web App"
echo "=================================="

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    echo "   Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-venv python3-pip"
    echo "   macOS: brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ Found $PYTHON_VERSION"

# Check python3-venv is available
if ! python3 -m venv --help &> /dev/null 2>&1; then
    echo "❌ python3-venv is not installed."
    echo "   Run: sudo apt install python3-venv"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo "📚 Installing dependencies (this may take a few minutes on first run)..."
pip install -r requirements.txt -q

# Create required directories
mkdir -p uploads saved_vocab

echo ""
echo "🎉 Setup complete!"
echo "=================================="
echo ""
echo "🚀 Starting the app..."
echo "   Open your browser at: http://localhost:8080"
echo "   Press Ctrl+C to stop the server"
echo ""

# Start the app
python3 app.py
