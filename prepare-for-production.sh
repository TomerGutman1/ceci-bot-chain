#!/bin/bash
# prepare-for-production.sh

echo "🚀 הכנת הפרויקט ל-Production"
echo "=============================="

# בדיקת קבצי .env
echo "✅ בודק קבצי סביבה..."
if [ ! -f .env ]; then
    echo "❌ חסר קובץ .env"
    echo "💡 העתק מ-.env.example והגדר את המשתנים"
    exit 1
fi

# בדיקת משתנים קריטיים
source .env
required_vars=(
    "OPENAI_API_KEY"
    "SUPABASE_URL"
    "SUPABASE_SERVICE_KEY"
    "DOMAIN_NAME"
    "ADMIN_EMAIL"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ משתנה חסר: $var"
        exit 1
    fi
done

echo "✅ כל המשתנים הקריטיים קיימים"

# ניקוי קבצים מיותרים
echo "🧹 מנקה קבצים מיותרים..."
find . -name "*.log" -delete
find . -name "*.bak" -delete
find . -name "*_backup_*" -delete
rm -f dump.rdb
rm -rf TESTS/debug/debug_results.md

# בדיקת Docker
echo "🐳 בודק Docker..."
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose לא מותקן"
    exit 1
fi

# בניית images
echo "🏗️ בונה Docker images..."
docker compose build

# בדיקת תקינות
echo "✅ בודק תקינות..."
docker compose config

echo ""
echo "✅ הפרויקט מוכן להעלאה!"
echo ""
echo "השלבים הבאים:"
echo "1. git add ."
echo "2. git commit -m 'Initial production-ready version'"
echo "3. git push origin main"
echo "4. בשרת: git clone ..."
echo "5. בשרת: ./init-letsencrypt.sh"
echo "6. בשרת: docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
