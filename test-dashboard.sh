#!/bin/bash

# Test Script for Macro Filter View Dashboard
# Runs the dashboard components in standalone test mode

set -e

echo "🧪 MACRO FILTER VIEW - TEST RUNNER"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: package.json not found. Please run from project root.${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Checking project setup...${NC}"

# Check Node.js version
if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js: $NODE_VERSION${NC}"
else
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    npm install
fi

echo -e "${BLUE}🔧 Setting up test environment...${NC}"

# Create test index.html if it doesn't exist in the right place
if [ ! -f "index.html" ]; then
    echo -e "${YELLOW}📄 Creating test index.html...${NC}"
    cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧪 Macro Filter View Test</title>
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/macro_filter_view/test/main.tsx"></script>
</body>
</html>
EOF
fi

# Update vite.config if needed to include our test paths
if [ ! -f "vite.config.ts" ]; then
    echo -e "${YELLOW}⚙️ Creating Vite config...${NC}"
    cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    open: true,
    host: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
EOF
fi

echo -e "${BLUE}🚀 Starting test server...${NC}"

# Check if port 3000 is available
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️ Port 3000 is in use. Trying port 3001...${NC}"
    PORT=3001
else
    PORT=3000
fi

echo -e "${GREEN}🌐 Test dashboard will be available at:${NC}"
echo -e "${BLUE}   Local:   http://localhost:$PORT${NC}"
echo -e "${BLUE}   Network: http://$(hostname -I | awk '{print $1}'):$PORT${NC}"
echo ""
echo -e "${YELLOW}📊 Available test sections:${NC}"
echo "   • סקירה כללית (Overview)"
echo "   • מיטוב נתונים (Data Optimizer)"
echo "   • השוואת ממשלות (Government Comparison)"
echo "   • התראות חכמות (Smart Alerts)"
echo "   • שיתוף דוחות (Report Sharing)"
echo "   • סביבת עבודה (Personal Workspace)"
echo ""
echo -e "${GREEN}🔧 Development features enabled:${NC}"
echo "   • Hot reload"
echo "   • TypeScript checking"
echo "   • Hebrew RTL support"
echo "   • Mock data simulation"
echo "   • Performance monitoring"
echo ""
echo -e "${BLUE}📝 Press Ctrl+C to stop the server${NC}"
echo ""

# Start the development server
npm run dev -- --port $PORT