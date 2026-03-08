#!/bin/bash

echo "==================================="
echo "Movie Emotion Recommender - Setup"
echo "==================================="

# Create folder structure
echo "Creating folder structure..."

mkdir -p app/services
mkdir -p ml
mkdir -p recommender
mkdir -p quiz
mkdir -p data
mkdir -p models
mkdir -p static/css
mkdir -p static/js
mkdir -p templates

# Create __init__.py files for Python modules
touch app/__init__.py
touch app/services/__init__.py
touch ml/__init__.py
touch recommender/__init__.py
touch quiz/__init__.py

echo "✓ Folder structure created"

# Create Python virtual environment
echo "Creating Python virtual environment..."
python -m venv venv

echo "✓ Virtual environment created"

# Display activation instructions
echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo ""
echo "   Windows (PowerShell):   .\\venv\\Scripts\\Activate.ps1"
echo "   Windows (CMD):          .\\venv\\Scripts\\activate.bat"
echo "   Mac/Linux:              source venv/bin/activate"
echo ""
echo "2. Install dependencies:"
echo "   pip install -r requirements.txt"
echo ""
echo "3. Add your TMDB API key to .env (optional)"
echo ""
echo "4. Run the app:"
echo "   python run.py"
echo ""
echo "==================================="
