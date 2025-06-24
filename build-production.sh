#!/bin/bash

# Production deployment script for DigitalOcean
echo "🚀 Building CECI-AI for production deployment..."

# Check if .env.prod.do exists
if [ ! -f .env.prod.do ]; then
    echo "❌ Error: .env.prod.do file not found!"
    echo "Using .env.prod instead..."
    cp .env.prod .env.prod.do
    echo "⚠️  Please update .env.prod.do with production values!"
fi

# Use production env file
cp .env.prod.do .env.prod

# Stop any running containers
echo "🛑 Stopping existing containers..."
docker compose down

# Build with production config
echo "🏗️  Building containers for production..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

echo "✅ Production build complete!"
echo ""
echo "📦 To deploy to DigitalOcean:"
echo "1. Commit and push to GitHub"
echo "2. On your DO server, pull the latest changes"
echo "3. Copy .env.prod.do to .env.prod"
echo "4. Run: docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
echo ""
echo "🔧 For local testing with production config:"
echo "docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
