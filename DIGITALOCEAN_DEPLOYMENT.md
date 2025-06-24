# 🚀 CECI-AI Deployment on DigitalOcean

## Server Details
- **IP**: 178.62.39.248
- **Repository**: https://github.com/TomerGutman1/ceci-ai.git
- **Branch**: deploy_droplet

## Pre-requisites
- Domain name pointing to 178.62.39.248
- OpenAI API Key
- Supabase project with loaded data

## Deployment Steps

### 1. Connect to Droplet
```bash
ssh root@178.62.39.248
```

### 2. Clone Repository
```bash
git clone -b deploy_droplet https://github.com/TomerGutman1/ceci-ai.git
cd ceci-ai
```

### 3. Configure Environment
```bash
cp .env.example .env
nano .env
```

Update these values:
- `DOMAIN_NAME`: Your domain (e.g., ceci-ai.com)
- `ADMIN_EMAIL`: Your email for SSL certificates
- `OPENAI_API_KEY`: Your OpenAI API key
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Your Supabase service key
- `VITE_SUPABASE_URL`: Same as SUPABASE_URL
- `VITE_SUPABASE_ANON_KEY`: Your Supabase anon key

### 4. Run Setup Script
```bash
chmod +x setup-on-droplet.sh
./setup-on-droplet.sh
```

### 5. Initialize SSL Certificate
```bash
chmod +x init-letsencrypt.sh
./init-letsencrypt.sh
```

### 6. Start Services
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 7. Verify Deployment
```bash
# Check services status
docker compose ps

# View logs
docker compose logs -f

# Test the application
curl https://your-domain.com
```

## Maintenance

### Update Application
```bash
git pull origin deploy_droplet
docker compose build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
```

### Backup Redis
```bash
docker compose exec redis redis-cli BGSAVE
```

### SSL Certificate Renewal
The certificate renews automatically via certbot container.

## Troubleshooting

### Port Issues
```bash
# Check if ports are open
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### DNS Issues
```bash
# Verify DNS
dig your-domain.com
nslookup your-domain.com
```

### Docker Issues
```bash
# Restart Docker
sudo systemctl restart docker

# Clean up
docker system prune -a
```

## Security Recommendations

1. **Change root password**
```bash
passwd
```

2. **Create non-root user**
```bash
adduser deploy
usermod -aG sudo,docker deploy
```

3. **Setup firewall**
```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

4. **Install fail2ban**
```bash
apt update && apt install fail2ban -y
```
