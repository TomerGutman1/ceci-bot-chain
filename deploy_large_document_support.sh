#!/bin/bash
# Deploy Decision Guide Bot with large document support

echo "Deploying Decision Guide Bot with large document support..."
echo "=========================================================="

# Add and commit changes
echo -e "\n1. Committing changes..."
git add bot_chain/DECISION_GUIDE_BOT/main.py
git add tasks/large_document_support.md
git add test_large_document_analysis.py
git commit -m "feat: Add large document support to Decision Guide Bot

- Increased MAX_CHAR_LIMIT to 500K (~200 pages)
- Implemented intelligent document chunking (30K chars/chunk)
- Added chunk analysis with overlap for context preservation
- Built results aggregation across multiple chunks
- Added progress reporting in Hebrew
- Maintains consistency with caching and seed parameters

Now supports 72-page documents as requested by user"

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
echo ""
echo "The Decision Guide Bot now supports documents up to 500,000 characters (~200 pages)."
echo "Your 72-page documents will be automatically processed in chunks."
echo ""
echo "Monitor the service with:"
echo "ssh root@178.62.39.248 'docker logs -f ceci-w-bots-decision-guide-bot-1'"