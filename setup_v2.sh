#!/bin/bash
# Setup script for RAG v2

echo "=========================================="
echo "Bhagavad Gita RAG v2 - Setup Script"
echo "=========================================="

# Check Python version
echo ""
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo ""
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
else
    echo ""
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p data/vector_store
mkdir -p logs
echo "✓ Directories created"

# Check if PDF exists
if [ -f "11-Bhagavad-gita_As_It_Is.pdf" ]; then
    echo ""
    echo "✓ Bhagavad Gita PDF found"
else
    echo ""
    echo "⚠️  WARNING: Bhagavad Gita PDF not found!"
    echo "   Please place '11-Bhagavad-gita_As_It_Is.pdf' in the project root"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Run: python test_rag.py (to test the system)"
echo "3. Run: python main_v2.py (to start the API server)"
echo ""
echo "Or use Docker:"
echo "  docker build -t gita-rag ."
echo "  docker run -p 8080:8080 -e OPENAI_API_KEY=your-key gita-rag"
echo ""
