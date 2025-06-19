#!/bin/bash
echo "🚀 Starting PandasAI Service"
cd server/src/services/python

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements_pandasai.txt

echo "Starting PandasAI on http://localhost:8001"
python pandasai_service.py
