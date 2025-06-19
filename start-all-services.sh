#!/bin/bash

# CECI-AI Complete System Startup Script

echo "🚀 Starting CECI-AI Complete System"
echo "==================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    
    # Kill all child processes
    pkill -P $$
    
    # Kill specific services by port
    lsof -ti:8001 | xargs kill -9 2>/dev/null
    lsof -ti:5173 | xargs kill -9 2>/dev/null
    lsof -ti:8080 | xargs kill -9 2>/dev/null
    
    echo -e "${GREEN}All services stopped.${NC}"
    exit
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Check if tmux is installed
if command -v tmux &> /dev/null; then
    echo -e "${BLUE}Using tmux for better process management${NC}"
    USE_TMUX=true
else
    echo -e "${YELLOW}tmux not found. Install it for better experience:${NC}"
    echo "sudo apt-get install tmux"
    USE_TMUX=false
fi

if [ "$USE_TMUX" = true ]; then
    # Kill existing session if exists
    tmux kill-session -t ceci-ai 2>/dev/null
    
    # Create new tmux session
    tmux new-session -d -s ceci-ai
    
    # Window 1: PandasAI
    tmux rename-window -t ceci-ai:0 'PandasAI'
    tmux send-keys -t ceci-ai:0 "./start-pandasai.sh" C-m
    
    # Window 2: Backend
    tmux new-window -t ceci-ai:1 -n 'Backend'
    tmux send-keys -t ceci-ai:1 "./start-backend.sh" C-m
    
    # Window 3: Frontend
    tmux new-window -t ceci-ai:2 -n 'Frontend'
    tmux send-keys -t ceci-ai:2 "./start-frontend.sh" C-m
    
    # Wait for services to start
    echo "Waiting for services to start..."
    sleep 10
    
    # Check services
    echo -e "\n${GREEN}Checking services...${NC}"
    
    # Check PandasAI
    if curl -s http://localhost:8001 > /dev/null; then
        echo -e "✅ PandasAI Service: ${GREEN}Running${NC}"
    else
        echo -e "❌ PandasAI Service: ${RED}Not running${NC}"
    fi
    
    # Check Backend
    if curl -s http://localhost:5173/health > /dev/null; then
        echo -e "✅ Backend Service: ${GREEN}Running${NC}"
    else
        echo -e "❌ Backend Service: ${RED}Not running${NC}"
    fi
    
    # Check Frontend (might take longer to start)
    if curl -s http://localhost:8080 > /dev/null; then
        echo -e "✅ Frontend Service: ${GREEN}Running${NC}"
    else
        echo -e "⏳ Frontend Service: ${YELLOW}Starting...${NC}"
    fi
    
    echo -e "\n${GREEN}✅ All services started!${NC}"
    echo "========================"
    echo ""
    echo -e "📊 PandasAI API: ${BLUE}http://localhost:8001${NC}"
    echo -e "🔧 Backend API: ${BLUE}http://localhost:5173${NC}"
    echo -e "🌐 Frontend: ${BLUE}http://localhost:8080${NC}"
    echo ""
    echo -e "${YELLOW}To view logs:${NC}"
    echo "tmux attach -t ceci-ai"
    echo ""
    echo -e "${YELLOW}To stop all services:${NC}"
    echo "Press Ctrl+C or run: tmux kill-session -t ceci-ai"
    echo ""
    
    # Keep script running
    while true; do
        sleep 1
    done
    
else
    # Fallback: Run without tmux
    echo -e "${YELLOW}Running without tmux (less optimal)${NC}"
    
    # Start PandasAI in background
    echo -e "\n${YELLOW}Starting PandasAI Service...${NC}"
    ./start-pandasai.sh &
    PANDAS_PID=$!
    
    # Wait for PandasAI to start
    sleep 5
    
    # Start Backend in background
    echo -e "\n${YELLOW}Starting Backend Service...${NC}"
    ./start-backend.sh &
    BACKEND_PID=$!
    
    # Wait for Backend to start
    sleep 5
    
    # Start Frontend in background
    echo -e "\n${YELLOW}Starting Frontend Service...${NC}"
    ./start-frontend.sh &
    FRONTEND_PID=$!
    
    # Wait a bit
    sleep 5
    
    echo -e "\n${GREEN}✅ All services started!${NC}"
    echo "========================"
    echo ""
    echo -e "📊 PandasAI API: ${BLUE}http://localhost:8001${NC}"
    echo -e "🔧 Backend API: ${BLUE}http://localhost:5173${NC}"
    echo -e "🌐 Frontend: ${BLUE}http://localhost:8080${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    
    # Wait for all background processes
    wait
fi
