# 📚 Production Deployment Guide for CECI-AI

## 🎯 Overview
This guide provides step-by-step instructions for making changes and deploying updates to the production server at https://ceci-ai.ceci.org.il

## 🌿 Git Branch Structure
- **Main branch**: `main` (for PRs and stable releases)
- **Production branch**: `production-deploy` (currently active on server)
- **Development**: Create feature branches from `main`

## 🔧 Development Workflow

### 1. Making Changes Locally

```bash
# Always work on the production-deploy branch for immediate fixes
git checkout production-deploy
git pull origin production-deploy

# Make your changes
# Edit files as needed

# Test locally with Docker
docker compose up -d
docker compose logs -f [service-name]
```

### 2. Committing and Pushing Changes

```bash
# Stage your changes
git add [files]

# Commit with descriptive message
git commit -m "type: Brief description

- Detailed change 1
- Detailed change 2"

# Push to GitHub
git push origin production-deploy
```

### 3. Deploying to Production Server

#### Quick Deploy (for code changes only):
```bash
# Connect to server and update
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && git pull origin production-deploy"

# Rebuild and restart specific service
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod build [service-name] && ./run-compose.sh up -d [service-name]"
```

#### Full Deploy (with all services):
```bash
ssh root@178.62.39.248
cd /root/CECI-W-BOTS
git pull origin production-deploy
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

## 📦 Service Names Reference

| Service | Container Name | Port | Description |
|---------|---------------|------|-------------|
| backend | backend | 5173 | Node.js API server |
| frontend | frontend | 80 | React application |
| unified-intent-bot | unified-intent-bot | 8011 | Intent detection (GPT-4o) |
| sql-gen-bot | sql-gen-bot | 8012 | SQL query generation |
| context-router-bot | context-router-bot | 8013 | Context management |
| evaluator-bot | evaluator-bot | 8014 | Decision analysis |
| clarify-bot | clarify-bot | 8015 | Clarification requests |
| ranker-bot | ranker-bot | 8016 | Result ranking (disabled) |
| llm-formatter-bot | llm-formatter-bot | 8017 | Response formatting (GPT-4o-mini) |
| decision-guide-bot | decision-guide-bot | 8018 | Document analysis |
| postgres | postgres | 5432 | PostgreSQL database |
| redis | redis | 6379 | Redis cache |
| nginx | nginx | 80/443 | Reverse proxy |

## 🛠️ Common Operations

### View Logs
```bash
# All services
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && ./run-compose.sh logs -f"

# Specific service
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && ./run-compose.sh logs -f [service-name]"

# Last 100 lines
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && ./run-compose.sh logs --tail=100 [service-name]"
```

### Check Service Status
```bash
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && ./run-compose.sh ps"
```

### Restart Services
```bash
# Single service
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && ./run-compose.sh restart [service-name]"

# All services
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && ./run-compose.sh restart"
```

### Emergency Rollback
```bash
ssh root@178.62.39.248
cd /root/CECI-W-BOTS
git log --oneline -10  # Find the commit to rollback to
git checkout [commit-hash]
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

## 🔍 Debugging Production Issues

### 1. Check Logs for Errors
```bash
# Search for errors across all services
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && ./run-compose.sh logs --tail=500 | grep -i error"

# Check specific bot logs
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && ./run-compose.sh logs [bot-name] --tail=50"
```

### 2. Test Endpoints
```bash
# Health check
curl https://ceci-ai.ceci.org.il/health

# API health
curl https://ceci-ai.ceci.org.il/api/health

# Test chat endpoint
curl -X POST https://ceci-ai.ceci.org.il/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "sessionId": "test-123"}'
```

### 3. Database Access
```bash
# Connect to PostgreSQL (if local DB is used)
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && docker compose exec postgres psql -U postgres ceci_ai"

# Note: Production uses Supabase, so most data operations go through the API
```

## ⚠️ Important Notes

1. **Environment Variables**: Production env vars are in `.env.prod` on the server
2. **SSL Certificates**: Auto-renewed by certbot, certificates in `/root/CECI-W-BOTS/certbot/`
3. **Backups**: Database backups run daily at 3 AM to `/root/backups/`
4. **Monitoring**: Check disk space with `df -h` and Docker usage with `docker system df`

## 🚨 Critical Rules

1. **NEVER** commit `.env` files or API keys to Git
2. **ALWAYS** test changes locally before deploying
3. **MONITOR** logs after deployment for at least 5 minutes
4. **BACKUP** before major changes
5. **USE** the `run-compose.sh` wrapper for docker commands (it loads env vars)

## 📝 Update Checklist

- [ ] Test changes locally
- [ ] Commit with clear message
- [ ] Push to `production-deploy` branch
- [ ] Pull changes on server
- [ ] Rebuild affected services
- [ ] Restart services
- [ ] Check logs for errors
- [ ] Test functionality on production
- [ ] Update documentation if needed

## 🔑 Server Access

- **Server IP**: 178.62.39.248
- **SSH**: `ssh root@178.62.39.248`
- **Domain**: https://ceci-ai.ceci.org.il
- **Email**: project@ceci.org.il
- **GitHub**: https://github.com/TomerGutman1/ceci-bot-chain

## 📊 Cost Monitoring

Monitor OpenAI API usage to stay within budget:
```bash
# Check recent token usage in logs
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && ./run-compose.sh logs --tail=1000 | grep -i 'token usage'"
```

---

Last updated: 13 July 2025