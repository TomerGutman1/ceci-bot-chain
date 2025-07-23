#!/bin/bash
# Deploy Decision Guide Bot improvements

echo "Deploying Decision Guide Bot improvements..."
echo "==========================================="

# Add and commit changes
echo -e "\n1. Committing changes..."
git add bot_chain/DECISION_GUIDE_BOT/main.py
git add tasks/decision_guide_improvements.md
git add test_decision_guide_improvements.py
git commit -m "fix: Decision Guide Bot consistency issues for large documents

- Added document size limits (50K warning, 100K max)
- Set temperature=0 and seed=42 for consistent results
- Implemented analysis result caching (1 hour expiry)
- Enhanced logging with document hash tracking

Resolves inconsistent scoring for 72-page documents"

# Push to production branch
echo -e "\n2. Pushing to production-deploy branch..."
git push origin production-deploy

# Deploy to server
echo -e "\n3. Deploying to production server..."
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && \
  git pull && \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod build decision-guide-bot && \
  ./run-compose.sh up -d decision-guide-bot"

echo -e "\n✅ Deployment complete!"
echo "Monitor logs with: ssh root@178.62.39.248 'docker logs -f ceci-w-bots-decision-guide-bot-1'"