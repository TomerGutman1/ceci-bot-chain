#!/bin/bash
# prepare-for-droplet.sh - הכנה לפריסה ב-DigitalOcean

echo "🚀 הכנת הפרויקט לפריסה ב-DigitalOcean Droplet"
echo "==============================================="

# פרטי השרת
DROPLET_IP="178.62.39.248"
REPO_URL="https://github.com/TomerGutman1/ceci-ai.git"
BRANCH="deploy_droplet"

echo "📋 פרטי פריסה:"
echo "  - Droplet IP: $DROPLET_IP"
echo "  - Repository: $REPO_URL"
echo "  - Branch: $BRANCH"
echo ""

# עדכון .gitignore
echo "📝 מעדכן .gitignore..."
cat > .gitignore << 'EOF'
# Environment files
.env
.env.*
!.env.example

# Node
node_modules/
dist/
build/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
bun.lockb

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Docker
*.log
docker-compose.override.yml

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Certificates
*.pem
*.key
*.crt
*.csr
/deploy/nginx/ssl/
/certbot/

# Data
*.xlsx
*.csv
decisions.json

# Backups
*.backup
*.bak
*_backup_*

# Test outputs
TESTS/debug/debug_results.md
TESTS/*.log
test_*.json
test_*.md
test_*.txt

# Redis data
dump.rdb

# Temporary files
ERROR
[frontend
.env.local.txt

# Deployment scripts (local only)
start-*.ps1
start-*.bat
setup-*.sh
deploy-edge-functions.sh
EOF

# יצירת סקריפט לשרת
echo "📝 יוצר סקריפט התקנה לשרת..."
cat > setup-on-droplet.sh << 'EOF'
#!/bin/bash
# setup-on-droplet.sh - הרצה על השרת

echo "🚀 מתקין CECI-AI על DigitalOcean Droplet"
echo "=========================================="

# בדיקת Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker לא מותקן. מתקין..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "⚠️  יש להתחבר מחדש כדי שההרשאות יכנסו לתוקף"
    echo "הרץ: exit ואז ssh שוב"
    exit 1
fi

# יצירת תיקיות נדרשות
echo "📁 יוצר תיקיות..."
mkdir -p certbot/conf
mkdir -p certbot/www

# בדיקת .env
if [ ! -f .env ]; then
    echo "❌ חסר קובץ .env"
    echo "צור אותו מ-.env.example והגדר:"
    echo "  - DOMAIN_NAME"
    echo "  - ADMIN_EMAIL"
    echo "  - OPENAI_API_KEY"
    echo "  - SUPABASE_URL"
    echo "  - SUPABASE_SERVICE_KEY"
    exit 1
fi

# טעינת משתנים
source .env

# בניית containers
echo "🏗️ בונה Docker images..."
docker compose build

# בדיקת תקינות
echo "✅ בודק תקינות הגדרות..."
docker compose config > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ בעיה בהגדרות Docker Compose"
    exit 1
fi

echo ""
echo "✅ המערכת מוכנה להתקנה!"
echo ""
echo "השלבים הבאים:"
echo "1. הגדר DNS להצביע ל-IP של השרת"
echo "2. הרץ: ./init-letsencrypt.sh"
echo "3. הרץ: docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
EOF

chmod +x setup-on-droplet.sh

# נקה קבצים מיותרים
echo "🧹 מנקה קבצים מיותרים..."
rm -f ERROR [frontend .env.local.txt
rm -f start-*.ps1 start-*.bat
rm -f test_*.json test_*.md test_*.txt
rm -f *.bak *.backup

# בדיקת שינויים
echo ""
echo "📊 סטטוס Git:"
git status --short

echo ""
echo "✅ הפרויקט מוכן להעלאה!"
echo ""
echo "📋 הוראות המשך:"
echo ""
echo "1️⃣ על המחשב המקומי:"
echo "   git add ."
echo "   git commit -m 'Prepare for DigitalOcean deployment'"
echo "   git checkout -b deploy_droplet"
echo "   git push origin deploy_droplet"
echo ""
echo "2️⃣ על השרת (DigitalOcean):"
echo "   ssh root@$DROPLET_IP"
echo "   git clone -b deploy_droplet $REPO_URL ceci-ai"
echo "   cd ceci-ai"
echo "   cp .env.example .env"
echo "   nano .env  # הגדר את המשתנים"
echo "   ./setup-on-droplet.sh"
echo "   ./init-letsencrypt.sh"
echo "   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
echo ""
echo "3️⃣ בדיקה:"
echo "   https://your-domain.com"
