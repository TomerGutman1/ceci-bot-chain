#!/bin/bash

# CECI-AI System Check Script

echo "🔍 CECI-AI System Check"
echo "======================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check Node.js
echo -e "\n${BLUE}Checking Node.js...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "✅ Node.js installed: ${GREEN}$NODE_VERSION${NC}"
else
    echo -e "❌ Node.js: ${RED}Not installed${NC}"
    echo "Install with: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs"
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "✅ npm installed: ${GREEN}$NPM_VERSION${NC}"
else
    echo -e "❌ npm: ${RED}Not installed${NC}"
fi

# Check Python
echo -e "\n${BLUE}Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "✅ Python installed: ${GREEN}$PYTHON_VERSION${NC}"
else
    echo -e "❌ Python: ${RED}Not installed${NC}"
    echo "Install with: sudo apt-get install python3 python3-pip python3-venv"
fi

# Check pip
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    echo -e "✅ pip installed: ${GREEN}$PIP_VERSION${NC}"
else
    echo -e "❌ pip: ${RED}Not installed${NC}"
fi

# Check PostgreSQL dev files
echo -e "\n${BLUE}Checking PostgreSQL dev files...${NC}"
if dpkg -l | grep -q libpq-dev; then
    echo -e "✅ libpq-dev: ${GREEN}Installed${NC}"
else
    echo -e "❌ libpq-dev: ${RED}Not installed${NC}"
    echo "Install with: sudo apt-get install libpq-dev"
fi

# Check ports
echo -e "\n${BLUE}Checking ports...${NC}"
for port in 8001 5173 8080; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "⚠️  Port $port: ${YELLOW}Already in use${NC}"
    else
        echo -e "✅ Port $port: ${GREEN}Available${NC}"
    fi
done

# Check environment files
echo -e "\n${BLUE}Checking environment files...${NC}"
if [ -f "server/.env" ]; then
    echo -e "✅ Backend .env: ${GREEN}Found${NC}"
    
    # Check for API key
    if grep -q "OPENAI_API_KEY=sk-" server/.env; then
        echo -e "✅ OpenAI API Key: ${GREEN}Configured${NC}"
    else
        echo -e "⚠️  OpenAI API Key: ${YELLOW}Not configured or invalid${NC}"
    fi
else
    echo -e "❌ Backend .env: ${RED}Not found${NC}"
fi

if [ -f "server/src/services/python/.env" ]; then
    echo -e "✅ PandasAI .env: ${GREEN}Found${NC}"
else
    echo -e "❌ PandasAI .env: ${RED}Not found${NC}"
fi

# Check Python virtual environment
echo -e "\n${BLUE}Checking Python environment...${NC}"
if [ -d "server/src/services/python/venv" ]; then
    echo -e "✅ Python venv: ${GREEN}Created${NC}"
else
    echo -e "❌ Python venv: ${RED}Not created${NC}"
    echo "Run: ./setup-pandasai-ubuntu.sh"
fi

# Check tmux (optional but recommended)
echo -e "\n${BLUE}Checking optional tools...${NC}"
if command -v tmux &> /dev/null; then
    TMUX_VERSION=$(tmux -V)
    echo -e "✅ tmux: ${GREEN}$TMUX_VERSION${NC}"
else
    echo -e "⚠️  tmux: ${YELLOW}Not installed (optional)${NC}"
    echo "Install with: sudo apt-get install tmux"
fi

# Summary
echo -e "\n${BLUE}Summary:${NC}"
echo "========="

READY=true

# Check critical components
if ! command -v node &> /dev/null || ! command -v python3 &> /dev/null; then
    READY=false
fi

if [ "$READY" = true ]; then
    echo -e "${GREEN}✅ System is ready to run CECI-AI${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Make sure all scripts are executable:"
    echo "   chmod +x *.sh"
    echo "2. Set up PandasAI (if not done):"
    echo "   ./setup-pandasai-ubuntu.sh"
    echo "3. Configure your API keys in .env files"
    echo "4. Start all services:"
    echo "   ./start-all-services.sh"
else
    echo -e "${RED}❌ System is not ready${NC}"
    echo "Please install missing components first."
fi
