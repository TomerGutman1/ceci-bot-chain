# CECI-AI Deployment Guide

## 🚀 Quick Start

### Local Development
```bash
# 1. Clone the repository
git clone [your-repo-url]
cd ceci-ai-testing-main

# 2. Create .env.prod with your API keys
cp .env.example .env.prod
# Edit .env.prod with your actual keys

# 3. Run locally
chmod +x run-local.sh
./run-local.sh

# Access at http://localhost/
```

### Production Deployment (DigitalOcean)

#### On your local machine:
```bash
# 1. Prepare production build
chmod +x build-production.sh
./build-production.sh

# 2. Commit and push changes
git add .
git commit -m "Fix 404 issues and prepare for production"
git push origin main
```

#### On your DigitalOcean server:
```bash
# 1. Pull latest changes
cd /path/to/ceci-ai
git pull origin main

# 2. Copy production environment file
cp .env.prod.do .env.prod

# 3. Build and run with production config
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# 4. Check status
docker compose ps

# 5. View logs if needed
docker compose logs -f
```

## 🔧 Key Changes Made

1. **Fixed 404 on assets** - Added VITE_BASE_PATH support
2. **Updated vite.config.ts** - Dynamic base path
3. **Updated React Router** - Basename support
4. **Created production configs** - Separate configs for DO deployment
5. **Fixed API URLs** - Use relative paths instead of hardcoded localhost

## 📝 Environment Variables

### For Local Development (.env.prod)
- `VITE_API_URL=/api`
- `VITE_BASE_PATH=/`

### For DigitalOcean (.env.prod.do)
- `VITE_API_URL=/ceci-ai/api`
- `VITE_BASE_PATH=/ceci-ai/`
- `FRONTEND_URL=https://www.ceci.org.il`

## ⚠️ Important Notes

1. **SSL Certificates**: For production, set up Let's Encrypt:
   ```bash
   docker compose run --rm certbot certonly \
     --webroot --webroot-path=/var/www/certbot \
     -d your-domain.com
   ```

2. **OpenAI API Key**: Make sure your API key has sufficient credits

3. **Supabase**: Verify your Supabase project has enough API calls remaining

## 🐛 Troubleshooting

### Still getting 404 errors?
1. Clear browser cache
2. Check nginx logs: `docker compose logs nginx`
3. Verify build args: `docker inspect ceci-ai-testing-main-frontend-1 | grep VITE`

### Backend not responding?
1. Check health: `curl http://localhost/api/health`
2. View backend logs: `docker compose logs backend`
3. Verify Redis is running: `docker compose ps redis`

### Need help?
Check the full documentation in `FULL_PROJECT_SUMMARY.md`
