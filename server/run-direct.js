// Direct Node.js runner with enhanced logging
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

console.log('=== CECI-AI Direct Runner ===');
console.log(`Starting at: ${new Date().toISOString()}`);

// Setup logging
const logsDir = path.join(__dirname, 'logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir);
}

const logFile = path.join(logsDir, `direct-${Date.now()}.log`);
const logStream = fs.createWriteStream(logFile);

function log(message) {
  const timestamp = new Date().toISOString();
  const logLine = `[${timestamp}] ${message}`;
  console.log(logLine);
  logStream.write(logLine + '\n');
}

// Check if dist exists
if (!fs.existsSync(path.join(__dirname, 'dist', 'main.js'))) {
  log('ERROR: dist/main.js not found! Run npm run build first.');
  process.exit(1);
}

// Set environment variables
process.env.NODE_ENV = 'development';
process.env.DEBUG = 'true';
process.env.FORCE_COLOR = '0';

log('Starting server directly...');
log(`Working directory: ${__dirname}`);
log(`Node version: ${process.version}`);

// Start the main.js file directly
try {
  // Load and run main.js in the same process
  require('./dist/main.js');
  
  log('Server loaded successfully');
  
  // Keep the process alive
  process.stdin.resume();
  
  // Handle shutdown
  process.on('SIGINT', () => {
    log('Received SIGINT, shutting down...');
    logStream.end();
    process.exit(0);
  });
  
} catch (error) {
  log(`ERROR: Failed to start server: ${error.message}`);
  console.error(error);
  process.exit(1);
}
