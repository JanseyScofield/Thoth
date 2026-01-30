#!/bin/bash

# Installation script for Thoth API
# Run: bash setup.sh

set -e  # Stop script on error

echo "🚀 Setting up Thoth API environment..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Installing..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Installing..."
    sudo apt install -y python3-pip
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install poppler (required for pdf2image)
if ! command -v pdftoppm &> /dev/null; then
    echo "📄 Installing poppler-utils (required for PDF processing)..."
    sudo apt install -y poppler-utils
fi

# Update pip
echo "⬆️  Updating pip..."
pip install --upgrade pip

# Install dependencies in the correct order
echo "📥 Installing Python dependencies..."

echo "   → Installing PaddleOCR and main dependencies..."
pip install "paddlepaddle>=2.6.0" "paddleocr==2.7.3" layoutparser shapely

echo "   → Removing opencv-python and installing compatible opencv-python-headless..."
pip uninstall opencv-python opencv-python-headless -y 2>/dev/null || true
pip install opencv-python-headless==4.8.1.78

echo "   → Installing compatible numpy..."
pip install "numpy<2.0.0" --force-reinstall

echo "   → Installing FastAPI and server..."
pip install fastapi uvicorn[standard]

echo "   → Installing PDF processor..."
pip install pdf2image

echo ""
echo "✅ Installation completed!"
echo ""
echo "To run the application:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "  3. Access: http://localhost:8000/docs"
echo ""
