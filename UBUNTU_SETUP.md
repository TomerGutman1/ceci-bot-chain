# CECI-AI Ubuntu Installation Guide

## Prerequisites

Make sure you have Ubuntu 20.04 or later.

## Quick Start

1. **Clone/Copy the project to your Ubuntu machine**

2. **Make scripts executable:**
   ```bash
   chmod +x *.sh
   # or run:
   ./make-executable.sh
   ```

3. **Check system requirements:**
   ```bash
   ./check-system.sh
   ```

4. **Install system dependencies (if needed):**
   ```bash
   # Node.js
   curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
   sudo apt-get install -y nodejs

   # Python and dependencies
   sudo apt-get update
   sudo apt-get install -y python3 python3-pip python3-venv libpq-dev build-essential

   # Optional: tmux for better process management
   sudo apt-get install -y tmux
   ```

5. **Set up PandasAI:**
   ```bash
   ./setup-pandasai-ubuntu.sh
   ```

6. **Configure API Keys:**
   
   Edit the .env files:
   ```bash
   # Backend .env
   nano server/.env
   # Add your OpenAI API key

   # PandasAI .env (if different)
   nano server/src/services/python/.env
   ```

7. **Start all services:**
   ```bash
   ./start-all-services.sh
   ```

## Running Services Individually

If you prefer to run services in separate terminals:

**Terminal 1 - PandasAI Service:**
```bash
./start-pandasai.sh
```

**Terminal 2 - Backend:**
```bash
./start-backend.sh
```

**Terminal 3 - Frontend:**
```bash
./start-frontend.sh
```

## Service URLs

- 📊 **PandasAI API**: http://localhost:8001
- 🔧 **Backend API**: http://localhost:5173
- 🌐 **Frontend**: http://localhost:8080

## Using tmux (Recommended)

If you have tmux installed, the `start-all-services.sh` script will automatically create a tmux session with three windows:

- Window 0: PandasAI
- Window 1: Backend
- Window 2: Frontend

To attach to the session:
```bash
tmux attach -t ceci-ai
```

To navigate between windows:
- `Ctrl+B` then `0/1/2` - Switch to window
- `Ctrl+B` then `D` - Detach from session

To stop all services:
```bash
tmux kill-session -t ceci-ai
```

## Troubleshooting

1. **Port already in use:**
   ```bash
   # Find process using port
   sudo lsof -i :PORT_NUMBER
   
   # Kill process
   sudo kill -9 PID
   ```

2. **Python dependencies fail to install:**
   ```bash
   # Make sure you have all system dependencies
   sudo apt-get install -y python3-dev libpq-dev build-essential
   ```

3. **Permission denied errors:**
   ```bash
   # Make sure scripts are executable
   chmod +x *.sh
   ```

4. **Check logs:**
   - PandasAI logs: Check terminal output
   - Backend logs: `server/logs/`
   - Frontend logs: Browser console

## Running as System Services (Optional)

To run services as systemd services:

1. **PandasAI Service:**
   ```bash
   sudo systemctl enable pandasai.service
   sudo systemctl start pandasai.service
   sudo systemctl status pandasai.service
   ```

2. **Create similar services for backend and frontend if needed**

## Environment Variables

Make sure these are set in your .env files:

**server/.env:**
```
NODE_ENV=development
PORT=5173
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_key
FRONTEND_URL=http://localhost:8080
PANDASAI_SERVICE_URL=http://localhost:8001
```

**server/src/services/python/.env:**
```
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_key
```
