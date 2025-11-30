#!/bin/bash
# Setup script for the project

set -e

echo "Setting up Heart Disease Prediction MLOps Project..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p data artifacts mlruns screenshots logs

# Download dataset
echo "Downloading dataset..."
python src/download_data.py

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run EDA notebook: jupyter notebook notebooks/01_eda.ipynb"
echo "3. Train models: python src/train_model.py"
echo "4. Run tests: pytest tests/ -v"
echo "5. Start API: python -m uvicorn src.api:app --host 0.0.0.0 --port 8000"

