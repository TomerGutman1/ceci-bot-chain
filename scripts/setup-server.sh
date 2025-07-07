#!/bin/bash

# CECI Bot Chain Server Setup Script
# This script sets up a fresh Ubuntu server for running CECI Bot Chain
# Usage: ./scripts/setup-server.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_DIR="/opt/ceci-bot-chain"
GITHUB_REPO="https://github.com/TomerGutman1/ceci-bot-chain.git"
DOMAIN="ceci-ai.ceci.org.il"
EMAIL="admin@ceci.org.il"

# Functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        print_error "This script must be run as root"
        exit 1
    fi
}

# Update system
update_system() {
    print_info "Updating system packages..."
    apt-get update
    apt-get upgrade -y
    apt-get install -y \
        curl \
        wget \
        git \
        vim \
        htop \
        ufw \
        fail2ban \
        nginx \
        certbot \
        python3-certbot-nginx \
        net-tools \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    
    print_success "System updated"
}

# Install Docker
install_docker() {
    print_info "Installing Docker..."
    
    # Check if Docker is already installed
    if command -v docker &> /dev/null; then
        print_warning "Docker is already installed"
        return
    fi
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Install Docker Compose plugin
    apt-get install -y docker-compose-plugin
    
    # Enable Docker service
    systemctl enable docker
    systemctl start docker
    
    print_success "Docker installed"
}

# Setup firewall
setup_firewall() {
    print_info "Configuring firewall..."
    
    # Allow SSH
    ufw allow 22/tcp comment 'SSH'
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    
    # Allow Docker Swarm (if needed)
    # ufw allow 2377/tcp comment 'Docker Swarm'
    # ufw allow 7946/tcp comment 'Docker Swarm'
    # ufw allow 7946/udp comment 'Docker Swarm'
    # ufw allow 4789/udp comment 'Docker Swarm'
    
    # Enable firewall
    ufw --force enable
    
    print_success "Firewall configured"
}

# Setup fail2ban
setup_fail2ban() {
    print_info "Configuring fail2ban..."
    
    # Create jail.local
    cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
filter = nginx-badbots
logpath = /var/log/nginx/access.log
maxretry = 2

[nginx-noproxy]
enabled = true
port = http,https
filter = nginx-noproxy
logpath = /var/log/nginx/access.log
maxretry = 2
EOF
    
    # Restart fail2ban
    systemctl restart fail2ban
    systemctl enable fail2ban
    
    print_success "fail2ban configured"
}

# Create project directory
setup_project_directory() {
    print_info "Setting up project directory..."
    
    # Create directory
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    # Clone repository
    if [ ! -d ".git" ]; then
        git clone "$GITHUB_REPO" .
    else
        git pull origin main
    fi
    
    # Create necessary directories
    mkdir -p certbot/conf certbot/www
    mkdir -p postgres_data redis_data
    
    # Set permissions
    chown -R root:root "$PROJECT_DIR"
    chmod -R 755 "$PROJECT_DIR"
    
    print_success "Project directory setup complete"
}

# Setup environment file
setup_environment() {
    print_info "Setting up environment file..."
    
    if [ -f ".env.prod" ]; then
        print_warning ".env.prod already exists, skipping..."
        return
    fi
    
    # Create .env.prod template
    cat > .env.prod << 'EOF'
# Production Environment Variables

# Frontend Environment Variables
VITE_SUPABASE_URL=https://hthrsrekzyobmlvtquub.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
VITE_API_URL=/api
VITE_BASE_PATH=/

# Backend Environment Variables
NODE_ENV=production
PORT=5173

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Supabase Backend Configuration
SUPABASE_URL=https://hthrsrekzyobmlvtquub.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_key_here

# CORS Configuration
FRONTEND_URL=https://ceci-ai.ceci.org.il

# Redis
REDIS_URL=redis://redis:6379

# Bot Chain Configuration
BOT_CHAIN_ENABLED=true
SKIP_RANKER=true
SKIP_EVALUATOR=true

# SQL Engine Configuration
USE_SUPABASE_RPC=false

# Postgres
POSTGRES_PASSWORD=your_secure_postgres_password_here
POSTGRES_PASSWORD_PROD=your_secure_postgres_password_here

# Logging
LOG_LEVEL=INFO

# Domain
DOMAIN_NAME=ceci-ai.ceci.org.il
EOF
    
    chmod 600 .env.prod
    
    print_warning "Please edit .env.prod and add your API keys and passwords"
    print_info "Use: vim $PROJECT_DIR/.env.prod"
}

# Setup SSL certificate
setup_ssl() {
    print_info "Setting up SSL certificate..."
    
    # Check if certificate already exists
    if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        print_warning "SSL certificate already exists for $DOMAIN"
        return
    fi
    
    # Stop nginx if running
    systemctl stop nginx || true
    
    # Get certificate
    certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        --domains "$DOMAIN,www.$DOMAIN" \
        --redirect \
        --expand
    
    # Copy certificates to project directory
    cp -r /etc/letsencrypt "$PROJECT_DIR/certbot/conf/"
    
    print_success "SSL certificate obtained"
}

# Setup Docker logging
setup_docker_logging() {
    print_info "Configuring Docker logging..."
    
    # Create Docker daemon configuration
    cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3",
    "labels": "service",
    "env": "NODE_ENV,LOG_LEVEL"
  },
  "metrics-addr": "127.0.0.1:9323",
  "experimental": true
}
EOF
    
    # Restart Docker
    systemctl restart docker
    
    print_success "Docker logging configured"
}

# Setup system monitoring
setup_monitoring() {
    print_info "Setting up system monitoring..."
    
    # Install monitoring tools
    apt-get install -y \
        prometheus-node-exporter \
        sysstat \
        iotop \
        ncdu
    
    # Create monitoring script
    cat > /usr/local/bin/ceci-monitor << 'EOF'
#!/bin/bash
# CECI monitoring script

echo "=== CECI Bot Chain Status ==="
echo ""
echo "Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "System Resources:"
free -h
echo ""
df -h | grep -E '^/dev/'
echo ""
echo "Docker Stats:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
EOF
    
    chmod +x /usr/local/bin/ceci-monitor
    
    print_success "Monitoring tools installed"
}

# Setup cron jobs
setup_cron() {
    print_info "Setting up cron jobs..."
    
    # Add cron jobs
    cat > /etc/cron.d/ceci-bot-chain << EOF
# CECI Bot Chain Cron Jobs

# Docker cleanup - daily at 3 AM
0 3 * * * root docker system prune -af --filter "until=24h" >> /var/log/docker-cleanup.log 2>&1

# Backup database - daily at 2 AM
0 2 * * * root docker exec ceci-bot-chain-postgres-1 pg_dump -U postgres ceci_bot_chain | gzip > /backup/postgres/ceci_bot_chain_\$(date +\%Y\%m\%d).sql.gz

# SSL renewal check - twice daily
0 2,14 * * * root certbot renew --post-hook "docker restart ceci-bot-chain-nginx-1" >> /var/log/certbot-renewal.log 2>&1

# Health check - every 5 minutes
*/5 * * * * root curl -f http://localhost/health || docker restart ceci-bot-chain-nginx-1
EOF
    
    # Create backup directory
    mkdir -p /backup/postgres
    
    print_success "Cron jobs configured"
}

# Create helpful aliases
setup_aliases() {
    print_info "Setting up helpful aliases..."
    
    cat >> /root/.bashrc << 'EOF'

# CECI Bot Chain aliases
alias ceci-cd='cd /opt/ceci-bot-chain'
alias ceci-logs='docker compose logs -f'
alias ceci-ps='docker compose ps'
alias ceci-restart='docker compose restart'
alias ceci-deploy='cd /opt/ceci-bot-chain && ./scripts/deploy.sh'
alias ceci-test='cd /opt/ceci-bot-chain && ./scripts/smoke-test.sh --production'
alias ceci-monitor='/usr/local/bin/ceci-monitor'
EOF
    
    print_success "Aliases configured"
}

# Main setup function
main() {
    print_info "CECI Bot Chain Server Setup"
    print_info "==========================="
    
    # Check root
    check_root
    
    # Run setup steps
    update_system
    install_docker
    setup_firewall
    setup_fail2ban
    setup_project_directory
    setup_environment
    setup_docker_logging
    setup_monitoring
    setup_cron
    setup_aliases
    
    # Try to setup SSL (may fail if domain not pointed yet)
    setup_ssl || print_warning "SSL setup failed - run later when domain is pointed to this server"
    
    print_success "Server setup complete!"
    print_info ""
    print_info "Next steps:"
    print_info "1. Edit environment file: vim $PROJECT_DIR/.env.prod"
    print_info "2. Point domain to this server: $DOMAIN -> $(curl -s ifconfig.me)"
    print_info "3. Run SSL setup if needed: certbot certonly --nginx -d $DOMAIN -d www.$DOMAIN"
    print_info "4. Deploy application: cd $PROJECT_DIR && ./scripts/deploy.sh"
    print_info "5. Run smoke tests: ./scripts/smoke-test.sh --production"
    print_info ""
    print_info "Useful commands:"
    print_info "- ceci-monitor     : Check system status"
    print_info "- ceci-logs       : View container logs"
    print_info "- ceci-deploy     : Deploy application"
    print_info "- ceci-test       : Run smoke tests"
}

# Run main function
main