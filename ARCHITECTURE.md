# CECI-AI Architecture & Workflow Guide

## Project Structure Overview
```
ceci-ai/
├── server/                 # Backend Node.js/Express server
│   ├── src/
│   │   ├── main.ts        # Entry point
│   │   ├── api/           # GraphQL API
│   │   ├── controllers/   # REST controllers
│   │   ├── routes/        # Express routes
│   │   ├── services/      # Business logic
│   │   ├── dal/           # Data access layer
│   │   └── llms/          # LLM integration
│   └── package.json
├── sql-engine/            # Python SQL processing service
│   ├── src/
│   │   ├── index.ts       # FastAPI entry
│   │   ├── services/      # Core SQL logic
│   │   │   ├── nlToSql.ts # NL to SQL converter
│   │   │   ├── queryTemplates.ts # SQL templates
│   │   │   └── formatter.ts # Response formatter
│   │   └── utils/         # Utilities
│   └── package.json
├── src/                   # Frontend React/Vite
│   ├── App.tsx
│   ├── components/
│   ├── hooks/
│   └── services/
├── docker-compose.yml     # Development setup
├── docker-compose.prod.yml # Production setup
└── nginx.conf            # Reverse proxy config
```

## Runtime Flow

### 1. User Query Flow
```mermaid
graph TD
    A[User Input] --> B[Frontend React]
    B --> C[nginx:443]
    C --> D[Backend:8080]
    D --> E{Query Type?}
    E -->|SQL Query| F[sql-engine:8002]
    E -->|General Chat| G[LLM Service]
    F --> H[PostgreSQL:5432]
    G --> I[OpenAI API]
    F --> J[Redis Cache]
    J --> D
    H --> F
    I --> G
    F --> D
    G --> D
    D --> B
```

### 2. SQL Processing Pipeline
```typescript
// Path: sql-engine/src/services/nlToSql.ts
1. Natural Query → normalizeQuery()
   - Date normalization
   - Topic fuzzy matching
   - Query standardization

2. Template Matching → findMatchingTemplate()
   - Check 40+ predefined templates
   - Priority-based matching

3. GPT Fallback → convertWithGPT()
   - If no template matches
   - Confidence scoring

4. SQL Execution → PostgreSQL
   - Parameterized queries
   - Result formatting
```

## Key Code Paths & Interactions

### Backend Server
```typescript
// server/src/main.ts → Entry point
startServer() {
  // Initialize Express
  // Setup middleware
  // Mount routes
  // Start GraphQL
}

// server/src/routes/chat.routes.ts
POST /api/chat → chatController.processChat()
  → chatService.processMessage()
  → llmService.generateResponse()

// server/src/controllers/query.controller.ts
POST /api/query → queryController.processQuery()
  → Forwards to sql-engine:8002
```

### SQL Engine Service
```typescript
// sql-engine/src/index.ts
app.post('/api/process-query') → 
  → nlToSql.convertToSQL()
  → executor.executeQuery()
  → formatter.format()

// sql-engine/src/services/queryTemplates.ts
export const QUERY_TEMPLATES = {
  COUNT_BY_GOVERNMENT: {...},
  DECISIONS_BY_TOPIC: {...},
  // 40+ templates
}
```

### Frontend Flow
```typescript
// src/App.tsx
<ChatInterface /> → useChatStream()
  → fetch('/api/chat', {stream: true})
  → Server-Sent Events (SSE)
  → Display streaming response

// src/hooks/useChatStream.ts
const eventSource = new EventSource()
eventSource.onmessage = (event) => {
  // Update UI with chunks
}
```

## CI/CD Workflow

### GitHub Actions: `.github/workflows/deploy.yml`
```yaml
name: Deploy to DigitalOcean

on:
  push:
    branches: [deploy_droplet]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      1. Checkout code
      2. Setup Docker Buildx
      3. Login to Docker Hub
      4. Build and push images:
         - backend → tomergutman/ceci-backend:latest
         - sql-engine → tomergutman/ceci-sql-engine:latest
         - frontend → tomergutman/ceci-frontend:latest
      
      5. SSH to Droplet (178.62.39.248)
      6. Pull latest images
      7. Run docker compose up -d
      8. Health checks
```

### Deployment Flow
```bash
1. Developer: git push origin deploy_droplet
2. GitHub Actions: Triggered automatically
3. Build: Multi-stage Docker builds
4. Push: Images to Docker Hub
5. Deploy: SSH to droplet → docker-compose pull → restart
6. Verify: Health checks on all services
```

## Local Development Quick-Start

```bash
# 1. Clone and setup
git clone -b deploy_droplet git@github.com:TomerGutman1/ceci-ai.git
cd ceci-ai
cp .env.example .env

# 2. Configure environment
# Edit .env with:
OPENAI_API_KEY=sk-...
REDIS_URL=redis://redis:6379
DATABASE_URL=postgresql://user:pass@postgres:5432/decisions

# 3. Start all services
docker compose up -d

# 4. Verify services
docker compose ps
# Should see: nginx, frontend, backend, sql-engine, redis, postgres

# 5. Access application
open http://localhost:3000  # Frontend
curl http://localhost:8080/health  # Backend
curl http://localhost:8002/health  # SQL Engine

# 6. Watch logs
docker compose logs -f backend
docker compose logs -f sql-engine

# 7. Run tests
cd tests
chmod +x test_improvements_quick.sh
./test_improvements_quick.sh
```

## Critical File Paths

### Configuration
- `/docker-compose.yml` - Development orchestration
- `/docker-compose.prod.yml` - Production setup
- `/nginx.conf` - Reverse proxy & SSL
- `/.env.prod.do` - Production environment

### Backend Core
- `/server/src/main.ts` - Server entry
- `/server/src/services/chat.service.ts` - Chat logic
- `/server/src/llms/configs.ts` - LLM configuration
- `/server/src/dal/decisions.dal.ts` - Database queries

### SQL Engine Core
- `/sql-engine/src/services/nlToSql.ts` - NL→SQL conversion
- `/sql-engine/src/services/queryTemplates.ts` - SQL templates
- `/sql-engine/src/utils/fuzzyMatcher.ts` - Topic matching
- `/sql-engine/src/utils/dateNormalizer.ts` - Date parsing

### Frontend Core
- `/src/App.tsx` - Main React component
- `/src/components/ChatInterface.tsx` - Chat UI
- `/src/hooks/useChatStream.ts` - SSE handling
- `/src/services/api.ts` - API client

### Testing
- `/tests/test_improvements_quick.sh` - Quick test suite
- `/tests/test_comprehensive.sh` - Full test suite
- `/tests/debug/*` - Debug utilities

## Service Communication

```yaml
Internal Network: ceci-network
├── nginx:80/443 → Public interface
├── frontend:3000 → React dev server
├── backend:8080 → Express API
├── sql-engine:8002 → FastAPI SQL service
├── redis:6379 → Cache & session store
└── postgres:5432 → Database

Inter-service calls:
- Frontend → nginx → backend (REST/GraphQL)
- Backend → sql-engine (HTTP POST)
- Backend → redis (Cache)
- sql-engine → postgres (SQL)
- Backend → OpenAI API (External)
```

## Environment Variables Flow

```bash
# Development (.env)
OPENAI_API_KEY → backend → LLM service
DATABASE_URL → sql-engine → PostgreSQL
REDIS_URL → backend → Cache service

# Production (.env.prod.do)
DOMAIN=ceci-ai.ceci.org.il → nginx → SSL
NODE_ENV=production → All services
```

## Build & Deploy Commands

```bash
# Local development
docker compose up -d --build

# Production build
docker compose -f docker-compose.prod.yml build

# Deploy to production
ssh root@178.62.39.248
cd /root/ceci-ai
git pull origin deploy_droplet
docker compose -f docker-compose.prod.yml up -d --build

# Rollback
docker compose down
git checkout <previous-commit>
docker compose up -d --build
```
