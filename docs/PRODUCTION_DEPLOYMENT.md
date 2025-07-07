# CECI Bot Chain Production Deployment Guide

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Initial Deployment](#initial-deployment)
4. [SSL Certificate Setup](#ssl-certificate-setup)
5. [Deployment Workflow](#deployment-workflow)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Procedures](#rollback-procedures)
9. [Security Checklist](#security-checklist)

## 🔧 Prerequisites

### Local Requirements
- Git configured with repository access
- SSH key for server access
- Docker and Docker Compose installed locally (for testing)

### Server Requirements
- Ubuntu 20.04 LTS or newer
- Minimum 4GB RAM, 2 CPU cores
- 50GB SSD storage
- Root access
- Domain pointed to server IP

### Repository Information
- **GitHub Repository**: https://github.com/TomerGutman1/ceci-bot-chain.git
- **Production Server**: 178.62.39.248
- **Production Domain**: https://ceci-ai.ceci.org.il

## 🖥️ Server Setup

### 1. Initial Server Configuration

SSH into your server and run the automated setup script:

```bash
# SSH to server
ssh root@178.62.39.248

# Download and run setup script
wget https://raw.githubusercontent.com/TomerGutman1/ceci-bot-chain/main/scripts/setup-server.sh
chmod +x setup-server.sh
./setup-server.sh
```

This script will:
- Update system packages
- Install Docker and Docker Compose
- Configure firewall (UFW)
- Setup fail2ban for security
- Create project directory structure
- Install monitoring tools
- Configure helpful aliases

### 2. Manual Configuration

After the automated setup, configure the environment:

```bash
cd /opt/ceci-bot-chain
vim .env.prod
```

**Required changes in .env.prod:**
- `OPENAI_API_KEY`: Your production OpenAI API key
- `POSTGRES_PASSWORD`: Strong database password
- `POSTGRES_PASSWORD_PROD`: Same as above
- Verify Supabase credentials are correct

### 3. SSH Key Configuration

Add your deployment SSH key:

```bash
# On your local machine
ssh-copy-id -i ~/.ssh/id_rsa root@178.62.39.248

# Or manually on the server
mkdir -p ~/.ssh
echo "your-public-key-here" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

## 🚀 Initial Deployment

### 1. Clone Repository

```bash
cd /opt/ceci-bot-chain
git clone https://github.com/TomerGutman1/ceci-bot-chain.git .
```

### 2. Setup SSL Certificate

Before deploying, obtain SSL certificate:

```bash
# Ensure domain is pointed to server
certbot certonly --standalone \
  --non-interactive \
  --agree-tos \
  --email admin@ceci.org.il \
  --domains ceci-ai.ceci.org.il,www.ceci-ai.ceci.org.il

# Copy certificates to project
cp -r /etc/letsencrypt /opt/ceci-bot-chain/certbot/conf/
```

### 3. Deploy Application

```bash
cd /opt/ceci-bot-chain
./scripts/deploy.sh
```

### 4. Verify Deployment

```bash
# Check container status
docker compose ps

# Run smoke tests
./scripts/smoke-test.sh --production

# Monitor logs
docker compose logs -f
```

## 🔒 SSL Certificate Setup

### Cloudflare Configuration

1. Log into Cloudflare dashboard
2. Navigate to your domain
3. SSL/TLS → Overview → Set to "Full (strict)"
4. SSL/TLS → Edge Certificates → Always Use HTTPS: ON
5. SSL/TLS → Edge Certificates → Minimum TLS Version: 1.2

### Let's Encrypt Renewal

SSL certificates auto-renew via cron job. To manually renew:

```bash
certbot renew --dry-run  # Test renewal
certbot renew            # Actual renewal
docker restart ceci-bot-chain-nginx-1  # Reload nginx
```

## 📦 Deployment Workflow

### GitHub Actions (Automated)

Deployments trigger automatically on push to main branch:

```yaml
# .github/workflows/deploy.yml handles:
- Code checkout
- SSH connection
- Docker image building
- Container orchestration
- Health checks
- Rollback on failure
```

### Manual Deployment

```bash
# SSH to server
ssh root@178.62.39.248

# Navigate to project
cd /opt/ceci-bot-chain

# Pull latest changes
git pull origin main

# Deploy
./scripts/deploy.sh

# Or deploy without rebuild
./scripts/deploy.sh --no-build
```

### Deployment Options

```bash
# Standard deployment (rebuild all)
./scripts/deploy.sh

# Skip Docker build (use existing images)
./scripts/deploy.sh --no-build

# Rollback to previous version
./scripts/deploy.sh --rollback
```

## 📊 Monitoring & Maintenance

### Health Monitoring

```bash
# Quick status check
ceci-monitor

# Container logs
ceci-logs

# Specific service logs
docker compose logs -f backend
docker compose logs -f rewrite-bot

# System resources
htop
docker stats
```

### Automated Monitoring

The system includes:
- Health checks every 5 minutes
- Automatic container restart on failure
- Daily Docker cleanup (3 AM)
- Daily database backups (2 AM)
- SSL renewal checks (2 AM, 2 PM)

### Log Locations

```
/var/log/nginx/access.log     # Nginx access logs
/var/log/nginx/error.log      # Nginx error logs
/var/log/docker-cleanup.log   # Docker cleanup logs
/var/log/certbot-renewal.log  # SSL renewal logs
/var/log/ceci-deployment.log  # Deployment history
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker compose logs [service-name]

# Check resource usage
df -h
free -m

# Restart specific service
docker compose restart [service-name]
```

#### 2. SSL Certificate Issues
```bash
# Check certificate status
certbot certificates

# Force renewal
certbot renew --force-renewal

# Check nginx config
docker exec ceci-bot-chain-nginx-1 nginx -t
```

#### 3. Database Connection Issues
```bash
# Check postgres
docker exec ceci-bot-chain-postgres-1 pg_isready

# Check migrations
docker exec ceci-bot-chain-postgres-1 psql -U postgres -d ceci_bot_chain -c "\dt"
```

#### 4. Bot Chain Timeout
```bash
# Check individual bot health
curl http://localhost:8010/health  # Rewrite bot
curl http://localhost:8011/health  # Intent bot
# ... etc

# Increase timeout in .env.prod
BOT_CHAIN_TIMEOUT=180000  # 3 minutes
```

### Debug Commands

```bash
# Full system check
docker compose ps
docker compose logs --tail=50
df -h
free -m
systemctl status docker

# Network debugging
docker network ls
docker network inspect ceci-ai-prod-network

# Clean up resources
docker system prune -af
docker volume prune -f
```

## ⏪ Rollback Procedures

### Quick Rollback

```bash
# Automated rollback
./scripts/deploy.sh --rollback
```

### Manual Rollback

```bash
# Stop current deployment
docker compose down

# Restore previous images
docker tag ceci-bot-chain-backend:rollback ceci-bot-chain-backend:latest
docker tag ceci-bot-chain-frontend:rollback ceci-bot-chain-frontend:latest
# ... repeat for all services

# Start with restored images
docker compose up -d
```

### Database Rollback

```bash
# Restore from backup
gunzip < /backup/postgres/ceci_bot_chain_20240107.sql.gz | \
  docker exec -i ceci-bot-chain-postgres-1 psql -U postgres -d ceci_bot_chain
```

## 🔐 Security Checklist

### Pre-Deployment
- [ ] Update .env.prod with secure passwords
- [ ] Remove default API keys
- [ ] Configure firewall rules
- [ ] Setup fail2ban
- [ ] Enable SSH key-only authentication
- [ ] Disable root password login

### Post-Deployment
- [ ] Verify SSL certificate active
- [ ] Check security headers (https://securityheaders.com)
- [ ] Verify no development ports exposed
- [ ] Check file permissions (especially .env.prod)
- [ ] Review nginx access logs for suspicious activity
- [ ] Ensure backups are working

### Ongoing Security
- [ ] Regular system updates
- [ ] Monitor fail2ban logs
- [ ] Review Docker images for vulnerabilities
- [ ] Rotate API keys periodically
- [ ] Audit user access

## 📞 Support

### Logs to Collect for Support

When reporting issues, provide:
1. Output of `ceci-monitor`
2. Recent deployment logs: `tail -100 /var/log/ceci-deployment.log`
3. Container logs: `docker compose logs --tail=100`
4. System info: `uname -a && docker --version && docker compose version`

### Emergency Contacts

- **System Admin**: root@178.62.39.248
- **Repository**: https://github.com/TomerGutman1/ceci-bot-chain
- **Domain Issues**: Cloudflare dashboard

## 🔄 Regular Maintenance

### Weekly
- Review container logs for errors
- Check disk usage
- Verify backup integrity

### Monthly
- Update system packages: `apt update && apt upgrade`
- Review and rotate logs
- Check SSL certificate expiry
- Review resource usage trends

### Quarterly
- Update Docker images
- Review security patches
- Audit user access
- Performance optimization review

---

## Quick Reference Card

```bash
# SSH to server
ssh root@178.62.39.248

# Common aliases
ceci-cd         # Go to project directory
ceci-monitor    # Check system status
ceci-logs       # View all logs
ceci-deploy     # Deploy latest version
ceci-test       # Run smoke tests

# Emergency commands
docker compose down              # Stop all services
docker compose up -d            # Start all services
./scripts/deploy.sh --rollback  # Rollback deployment
```

---

Last updated: January 2025