# 🚀 CECI-AI - מערכת חיפוש החלטות ממשלה חכמה

<div align="center">
  <img src="docs/logo.png" alt="CECI-AI Logo" width="200"/>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)](https://nodejs.org)
  [![Docker](https://img.shields.io/badge/docker-%3E%3D20.10-blue)](https://www.docker.com/)
</div>

## 📖 תיאור

CECI-AI היא מערכת חכמה לחיפוש וניתוח החלטות ממשלת ישראל באמצעות בינה מלאכותית. המערכת מאפשרת שאילתות בשפה טבעית בעברית ומחזירה תוצאות מדויקות ורלוונטיות.

### ✨ תכונות עיקריות

- 🔍 **חיפוש חכם** - שאילתות בשפה טבעית בעברית
- 🤖 **AI מתקדם** - שימוש ב-GPT לניתוח שאילתות
- 📊 **24,716 החלטות** - מסד נתונים מקיף
- 🚀 **ביצועים מעולים** - SQL Engine מהיר ומדויק
- 🔒 **אבטחה** - HTTPS, rate limiting, security headers
- 📱 **ממשק מודרני** - React + TypeScript

## 🛠️ טכנולוגיות

- **Frontend**: React, TypeScript, Vite, TailwindCSS
- **Backend**: Node.js, Express, TypeScript
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenAI GPT-3.5, SQL Query Engine
- **Infrastructure**: Docker, Nginx, Redis
- **Security**: Let's Encrypt SSL, Rate Limiting

## 📋 דרישות מערכת

- Docker >= 20.10
- Docker Compose >= 2.0
- Domain name (for HTTPS)
- OpenAI API Key
- Supabase account

## 🚀 התקנה מהירה

### 1. Clone the repository
```bash
git clone https://github.com/your-username/ceci-ai.git
cd ceci-ai
```

### 2. הגדרת Environment Variables
```bash
cp .env.example .env
# ערוך את .env עם הפרטים שלך
```

### 3. הרצה לוקלית (HTTP)
```bash
docker compose up -d
```

### 4. הרצה ב-Production (HTTPS)
```bash
# הגדר DOMAIN_NAME ו-ADMIN_EMAIL ב-.env
./init-letsencrypt.sh
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📚 מדריך שימוש

### דוגמאות לשאילתות

- "כמה החלטות קיבלה ממשלה 37?"
- "הבא לי החלטות בנושא חינוך משנת 2023"
- "מה עשה נתניהו בנושא ביטחון?"
- "החלטה 660 של ממשלה 35"

### API Endpoints

```bash
POST /api/chat
Content-Type: application/json
{
  "message": "השאילתה שלך",
  "sessionId": "optional-session-id"
}
```

## 🔧 פיתוח

### הרצת סביבת פיתוח
```bash
# Frontend
cd src && npm install && npm run dev

# Backend
cd server && npm install && npm run dev

# SQL Engine
cd sql-engine && npm install && npm run dev
```

### הרצת בדיקות
```bash
cd TESTS
./test-sql-engine.sh
```

## 📊 ארכיטקטורה

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Nginx     │────▶│   Backend    │────▶│ SQL Engine  │
│  (Reverse   │◀────│  (Node.js)   │◀────│ (Node.js)   │
│   Proxy)    │     │              │     │             │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │                     │
       ▼                    ▼                     ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Frontend   │     │    Redis     │     │  Supabase   │
│   (React)   │     │   (Cache)    │     │    (DB)     │
└─────────────┘     └──────────────┘     └─────────────┘
```

## 🔒 אבטחה

- HTTPS עם Let's Encrypt
- Security headers (CSP, HSTS, etc.)
- Rate limiting
- Input validation
- SQL injection protection

## 📝 רישיון

MIT License - ראה קובץ [LICENSE](LICENSE)

## 🤝 תרומה

אנו מזמינים תרומות! אנא קרא את [CONTRIBUTING.md](CONTRIBUTING.md)

## 📞 יצירת קשר

- Email: your-email@example.com
- Issues: [GitHub Issues](https://github.com/your-username/ceci-ai/issues)

## 🙏 תודות

- צוות Anthropic על Claude
- OpenAI על GPT-3.5
- Supabase על הפלטפורמה המעולה

---

<div align="center">
  נבנה עם ❤️ על ידי צוות CECI-AI
</div>
