#!/bin/bash

echo "Cleaning PandasAI cache..."

# Remove cache directory
rm -rf cache/

# Remove any __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove any .pyc files
find . -name "*.pyc" -delete

echo "Cache cleaned successfully!"
echo "Now restart the PandasAI service and run the tests again."
