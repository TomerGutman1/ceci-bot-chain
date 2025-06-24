#!/bin/bash

# Local development script
echo "🚀 Starting CECI-AI in local development mode..."

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    echo "❌ Error: .env.prod file not found!"
    echo "Please create .env.prod file with your API keys"
    exit 1
fi

# Stop any running containers
echo "🛑 Stopping existing containers..."
docker compose down

# Build and start
echo "🏗️  Building containers..."
docker compose build

echo "🚀 Starting services..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check health
echo "🔍 Checking service health..."
docker compose ps

echo "✅ Local development environment is ready!"
echo "📍 Frontend: http://localhost/"
echo "📍 Backend API: http://localhost/api"
echo "📍 View logs: docker compose logs -f"
