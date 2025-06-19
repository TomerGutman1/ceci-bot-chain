#!/bin/bash

# CECI-AI PandasAI Setup Script for Ubuntu

echo "🚀 Setting up CECI-AI with PandasAI integration on Ubuntu"
echo "========================================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: Not in CECI-AI root directory${NC}"
    exit 1
fi

# Step 1: Install system dependencies
echo -e "\n${YELLOW}Step 1: Installing system dependencies${NC}"
echo "======================================="

# Update package list
sudo apt-get update

# Install Python and pip if not installed
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3..."
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Install PostgreSQL development files (needed for psycopg2)
echo "Installing PostgreSQL development files..."
sudo apt-get install -y libpq-dev

# Install other dependencies
sudo apt-get install -y build-essential

# Step 2: Set up Python virtual environment
echo -e "\n${YELLOW}Step 2: Setting up Python environment${NC}"
echo "======================================"

cd server/src/services/python

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements_pandasai.txt

# Deactivate for now
deactivate

cd ../../../../

# Step 3: Create systemd service for PandasAI (optional)
echo -e "\n${YELLOW}Step 3: Creating systemd service (optional)${NC}"
echo "==========================================="

# Create service file
sudo tee /etc/systemd/system/pandasai.service > /dev/null << EOF
[Unit]
Description=CECI-AI PandasAI Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)/server/src/services/python
Environment="PATH=$(pwd)/server/src/services/python/venv/bin"
ExecStart=$(pwd)/server/src/services/python/venv/bin/python pandasai_service.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo "===================================="
echo ""
echo "To run PandasAI service:"
echo -e "${YELLOW}./start-pandasai.sh${NC}"
echo ""
echo "Or to enable as a system service:"
echo -e "${YELLOW}sudo systemctl enable pandasai.service${NC}"
echo -e "${YELLOW}sudo systemctl start pandasai.service${NC}"
