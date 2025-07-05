#!/bin/bash
# Rebuild all bot chain services after code changes

echo "🔄 Rebuilding Bot Chain Services..."

# Stop existing containers
echo "⏹️  Stopping existing containers..."
docker-compose stop intent-bot rewrite-bot sql-gen-bot context-router-bot evaluator-bot clarify-bot ranker-bot formatter-bot backend

# Rebuild services
echo "🏗️  Building services..."
docker-compose build --no-cache intent-bot rewrite-bot sql-gen-bot context-router-bot evaluator-bot clarify-bot ranker-bot formatter-bot backend

# Start services
echo "▶️  Starting services..."
docker-compose up -d intent-bot rewrite-bot sql-gen-bot context-router-bot evaluator-bot clarify-bot ranker-bot formatter-bot backend

# Wait for services to be ready
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
echo "🔍 Checking service health..."
docker-compose ps | grep -E "(intent-bot|rewrite-bot|sql-gen-bot|context-router-bot|evaluator-bot|clarify-bot|ranker-bot|formatter-bot|backend)"

echo "✅ Bot Chain rebuild complete!"
