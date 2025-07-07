#!/bin/bash
# Setup production aliases for easier Docker Compose usage

echo "Setting up production Docker Compose aliases..."

# Create wrapper script
cat > /usr/local/bin/dc << 'EOF'
#!/bin/bash
# Docker compose wrapper for production
cd /opt/ceci-bot-chain
docker compose --env-file .env.prod "$@"
EOF

chmod +x /usr/local/bin/dc

# Add aliases to root's bashrc
cat >> /root/.bashrc << 'EOF'

# CECI Production Docker aliases
alias dc='docker compose --env-file .env.prod'
alias dcup='docker compose --env-file .env.prod up -d'
alias dcdown='docker compose --env-file .env.prod down'
alias dclogs='docker compose --env-file .env.prod logs -f'
alias dcps='docker compose --env-file .env.prod ps'
alias dcbuild='docker compose --env-file .env.prod build'
alias dcrestart='docker compose --env-file .env.prod restart'

# Quick shortcuts
alias backend-logs='docker compose --env-file .env.prod logs -f backend'
alias backend-restart='docker compose --env-file .env.prod restart backend'
alias eval-restart='docker compose --env-file .env.prod restart evaluator-bot'
EOF

echo "✅ Aliases installed!"
echo ""
echo "Available commands:"
echo "  dc [command]       - Run any docker compose command with .env.prod"
echo "  dcup              - Start all services"
echo "  dcdown            - Stop all services"
echo "  dclogs            - Follow all logs"
echo "  dcps              - Show service status"
echo "  dcbuild           - Build all services"
echo "  dcrestart         - Restart all services"
echo "  backend-logs      - Follow backend logs"
echo "  backend-restart   - Restart backend"
echo "  eval-restart      - Restart evaluator bot"
echo ""
echo "Run 'source ~/.bashrc' to activate aliases in current session"