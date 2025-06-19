#!/bin/bash
echo "🔧 Starting Backend Service"
cd server
npm install
npm run build
npm start
