// Debug server launcher - bypasses nodemon and concurrently
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('=== DEBUG SERVER LAUNCHER ===');
console.log(`Starting at: ${new Date().toISOString()}`);
console.log(`Current directory: ${process.cwd()}`);

// Create log directory
const logDir = path.join(__dirname, 'debug-logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir);
  console.log(`Created log directory: ${logDir}`);
}

// Create log file with timestamp
const logFile = path.join(logDir, `debug-${Date.now()}.log`);
const logStream = fs.createWriteStream(logFile, { flags: 'a' });

console.log(`Log file: ${logFile}`);

// Function to write to both console and file
function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}`;
  console.log(logMessage);
  logStream.write(logMessage + '\n');
}

// First, build the TypeScript
log('Building TypeScript...');
const buildProcess = spawn('npm', ['run', 'build'], { shell: true });

buildProcess.stdout.on('data', (data) => {
  log(`BUILD: ${data.toString().trim()}`);
});

buildProcess.stderr.on('data', (data) => {
  log(`BUILD ERROR: ${data.toString().trim()}`);
});

buildProcess.on('close', (code) => {
  if (code !== 0) {
    log(`Build failed with code ${code}`);
    process.exit(code);
  }
  
  log('Build completed successfully');
  log('Starting server...');
  
  // Start the server
  const serverProcess = spawn('node', ['dist/main.js'], {
    env: { ...process.env, DEBUG: 'true', FORCE_COLOR: '0' }
  });
  
  serverProcess.stdout.on('data', (data) => {
    const message = data.toString();
    log(`SERVER: ${message.trim()}`);
  });
  
  serverProcess.stderr.on('data', (data) => {
    const message = data.toString();
    log(`SERVER ERROR: ${message.trim()}`);
  });
  
  serverProcess.on('close', (code) => {
    log(`Server exited with code ${code}`);
    logStream.end();
  });
  
  // Handle Ctrl+C
  process.on('SIGINT', () => {
    log('Received SIGINT, shutting down...');
    serverProcess.kill();
    setTimeout(() => {
      process.exit(0);
    }, 1000);
  });
});
