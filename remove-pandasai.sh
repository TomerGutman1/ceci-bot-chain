#!/bin/bash

# Script to remove PandasAI from the project
# This will clean up all PandasAI related files and dependencies

echo "=================================================="
echo "🧹 Removing PandasAI from CECI-AI Project"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to confirm action
confirm() {
    read -p "$1 (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Aborted.${NC}"
        exit 1
    fi
}

echo -e "${YELLOW}This script will:${NC}"
echo "1. Stop and remove PandasAI container"
echo "2. Remove PandasAI service from docker-compose.yml"
echo "3. Delete all PandasAI Python files"
echo "4. Remove PandasAI service references from backend code"
echo "5. Clean up unused dependencies"
echo ""

confirm "Do you want to proceed?"

# Step 1: Stop PandasAI container
echo -e "\n${YELLOW}Step 1: Stopping PandasAI container...${NC}"
docker compose stop pandasai
docker compose rm -f pandasai
echo -e "${GREEN}✓ PandasAI container stopped and removed${NC}"

# Step 2: List files to be removed
echo -e "\n${YELLOW}Step 2: Files that will be removed:${NC}"
echo "- server/src/services/python/ (entire directory)"
echo "- server/src/services/pandasAIService.ts"
echo "- PandasAI configuration in docker-compose.yml"
echo ""

confirm "Continue with file removal?"

# Step 3: Remove Python files
echo -e "\n${YELLOW}Step 3: Removing PandasAI Python files...${NC}"
if [ -d "server/src/services/python" ]; then
    rm -rf server/src/services/python
    echo -e "${GREEN}✓ Removed server/src/services/python/${NC}"
else
    echo -e "${YELLOW}Directory server/src/services/python not found${NC}"
fi

# Step 4: Remove TypeScript service file
echo -e "\n${YELLOW}Step 4: Removing PandasAI TypeScript service...${NC}"
if [ -f "server/src/services/pandasAIService.ts" ]; then
    rm -f server/src/services/pandasAIService.ts
    echo -e "${GREEN}✓ Removed server/src/services/pandasAIService.ts${NC}"
else
    echo -e "${YELLOW}File server/src/services/pandasAIService.ts not found${NC}"
fi

# Step 5: Create updated docker-compose.yml without PandasAI
echo -e "\n${YELLOW}Step 5: Creating updated docker-compose.yml...${NC}"
cat > docker-compose-no-pandas.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - ceci-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  sql-engine:
    build:
      context: ./sql-engine
      dockerfile: Dockerfile
    restart: unless-stopped
    ports:
      - "8002:8002"
    env_file:
      - .env.prod
    networks:
      - ceci-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  backend:
    build:
      context: ./server
      dockerfile: Dockerfile
    restart: unless-stopped
    env_file:
      - .env.prod
    environment:
      - REDIS_URL=redis://redis:6379
      - SQL_ENGINE_URL=http://sql-engine:8002
      - SQL_ENGINE_ENABLED=true
      - SQL_ENGINE_PERCENTAGE=100
    depends_on:
      - redis
      - sql-engine
    networks:
      - ceci-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5173/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    env_file:
      - .env.prod
    depends_on:
      - backend
    networks:
      - ceci-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    build:
      context: ./deploy/nginx
      dockerfile: Dockerfile
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deploy/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
    depends_on:
      - frontend
      - backend
    networks:
      - ceci-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  certbot:
    image: certbot/certbot:latest
    restart: unless-stopped
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
    networks:
      - ceci-network

volumes:
  redis-data:

networks:
  ceci-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
EOF

echo -e "${GREEN}✓ Created docker-compose-no-pandas.yml${NC}"

# Step 6: Show what needs to be updated in backend code
echo -e "\n${YELLOW}Step 6: Backend code updates needed:${NC}"
echo "The following files reference PandasAI and need to be updated:"
grep -r "pandasai\|PandasAI" server/src --exclude-dir=python 2>/dev/null | grep -v ".git" || echo "No references found"

echo -e "\n${YELLOW}Step 7: Next steps:${NC}"
echo "1. Review docker-compose-no-pandas.yml"
echo "2. Update backend code to remove PandasAI references"
echo "3. Replace docker-compose.yml with docker-compose-no-pandas.yml"
echo "4. Rebuild and restart services"

echo -e "\n${GREEN}✓ PandasAI removal script completed!${NC}"
echo -e "${YELLOW}Note: Backend code still needs manual updates${NC}"
