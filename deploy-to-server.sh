#!/bin/bash
set -e

echo "🚀 Starting deployment to production server..."

# Server details
SERVER_IP="178.62.39.248"
DOMAIN="ceci-ai.ceci.org.il"
EMAIL="your-email@example.com"  # UPDATE THIS

echo "📋 Prerequisites:"
echo "1. Update EMAIL variable in this script"
echo "2. Ensure domain $DOMAIN points to $SERVER_IP"
echo "3. Have SSH access to root@$SERVER_IP"
echo ""
read -p "Have you completed all prerequisites? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please complete prerequisites first."
    exit 1
fi

cat << 'EOF' > server-deploy.sh
#!/bin/bash
set -e

DOMAIN="ceci-ai.ceci.org.il"
EMAIL="$1"

echo "🧹 Cleaning up server..."
# Stop all containers
docker compose down 2>/dev/null || true

# Remove unused Docker resources
echo "Removing unused Docker resources..."
docker system prune -a --volumes -f

# Remove old project files
echo "Removing old project files..."
rm -rf /root/ceci-ai-backend /root/CECI-W-BOTS

# Check disk space
echo "Current disk usage:"
df -h

echo "📥 Cloning repository..."
cd /root
git clone https://github.com/TomerGutman1/ceci-bot-chain.git CECI-W-BOTS
cd CECI-W-BOTS
git checkout production-deploy

echo "🔧 Setting up environment..."
# Copy and configure production environment
cp .env.example .env.prod

# Create required directories
mkdir -p certbot/conf certbot/www

echo "📝 Please edit /root/CECI-W-BOTS/.env.prod with production values"
echo "Required variables:"
echo "- OPENAI_API_KEY"
echo "- SUPABASE_URL"
echo "- SUPABASE_SERVICE_KEY"
echo "- POSTGRES_PASSWORD_PROD"
echo ""
read -p "Press enter when .env.prod is configured..."

# Load environment variables
set -a
source .env.prod
set +a

echo "🌐 Creating production network..."
docker network create ceci-ai-prod-network 2>/dev/null || true

echo "🏗️ Starting initial services for SSL setup..."
# Start nginx and certbot first for SSL certificate
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx certbot

echo "⏳ Waiting for nginx to start..."
sleep 10

echo "🔐 Requesting SSL certificate..."
docker compose exec certbot certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email $EMAIL \
  --agree-tos \
  --no-eff-email \
  --force-renewal \
  -d $DOMAIN

echo "🚀 Deploying full application..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "✅ Checking service status..."
docker compose ps

echo "📊 Setting up monitoring..."
# Setup log rotation
cat > /etc/logrotate.d/docker-containers << 'LOGROTATE'
/var/lib/docker/containers/*/*.log {
  rotate 7
  daily
  compress
  size=10M
  missingok
  delaycompress
}
LOGROTATE

# Setup backup cron
mkdir -p /root/backups
(crontab -l 2>/dev/null; echo "0 3 * * * docker exec ceci-w-bots-postgres-1 pg_dump -U postgres ceci_ai | gzip > /root/backups/ceci_ai_\$(date +\%Y\%m\%d).sql.gz") | crontab -

echo "🎉 Deployment complete!"
echo "Visit https://$DOMAIN to verify the deployment"
echo ""
echo "📋 Post-deployment checklist:"
echo "- [ ] Verify HTTPS is working"
echo "- [ ] Test chat functionality"
echo "- [ ] Test decision guide feature"
echo "- [ ] Check all bot services are running"
echo "- [ ] Monitor logs: docker compose logs -f"
EOF

echo "📤 Copying deployment script to server..."
scp server-deploy.sh root@$SERVER_IP:/root/

echo "🔗 Connecting to server..."
echo "Run the following commands on the server:"
echo "1. chmod +x /root/server-deploy.sh"
echo "2. /root/server-deploy.sh $EMAIL"
echo ""
echo "Connecting to server now..."
ssh root@$SERVER_IP