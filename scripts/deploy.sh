#!/bin/bash

# CECI Bot Chain Production Deployment Script
# Usage: ./scripts/deploy.sh [--no-build] [--rollback]

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_PROJECT_NAME="ceci-bot-chain"
DOCKER_COMPOSE_CMD="docker compose"
PROD_COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"
BACKUP_TAG="rollback"
DEPLOYMENT_LOG="/var/log/ceci-deployment.log"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$DEPLOYMENT_LOG"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running or not installed"
        exit 1
    fi
}

# Function to check required files
check_required_files() {
    local required_files=(
        "docker-compose.yml"
        "docker-compose.prod.yml"
        ".env.prod"
        "deploy/nginx/nginx.prod.conf"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file missing: $file"
            exit 1
        fi
    done
}

# Function to backup current images
backup_images() {
    print_info "Backing up current images..."
    
    local services=(
        "frontend"
        "backend"
        "rewrite-bot"
        "intent-bot"
        "sql-gen-bot"
        "context-router-bot"
        "evaluator-bot"
        "clarify-bot"
        "ranker-bot"
        "formatter-bot"
    )
    
    for service in "${services[@]}"; do
        local image="${COMPOSE_PROJECT_NAME}-${service}"
        if docker image inspect "$image:latest" >/dev/null 2>&1; then
            docker tag "$image:latest" "$image:$BACKUP_TAG" || true
        fi
    done
    
    print_success "Images backed up with tag: $BACKUP_TAG"
}

# Function to rollback to previous version
rollback() {
    print_warning "Starting rollback..."
    log "Rollback initiated"
    
    local services=(
        "frontend"
        "backend"
        "rewrite-bot"
        "intent-bot"
        "sql-gen-bot"
        "context-router-bot"
        "evaluator-bot"
        "clarify-bot"
        "ranker-bot"
        "formatter-bot"
    )
    
    # Stop current containers
    $DOCKER_COMPOSE_CMD $PROD_COMPOSE_FILES down
    
    # Restore backup images
    for service in "${services[@]}"; do
        local image="${COMPOSE_PROJECT_NAME}-${service}"
        if docker image inspect "$image:$BACKUP_TAG" >/dev/null 2>&1; then
            docker tag "$image:$BACKUP_TAG" "$image:latest"
            print_info "Restored $service from backup"
        fi
    done
    
    # Start with restored images
    $DOCKER_COMPOSE_CMD $PROD_COMPOSE_FILES up -d
    
    print_success "Rollback completed"
    log "Rollback completed successfully"
}

# Function to run health checks
run_health_checks() {
    print_info "Running health checks..."
    
    local services=(
        "backend:5173/api/health"
        "rewrite-bot:8010/health"
        "intent-bot:8011/health"
        "sql-gen-bot:8012/health"
        "context-router-bot:8013/health"
        "evaluator-bot:8014/health"
        "clarify-bot:8015/health"
        "ranker-bot:8016/health"
        "formatter-bot:8017/health"
    )
    
    local all_healthy=true
    
    # Wait for services to be ready
    sleep 10
    
    for service_endpoint in "${services[@]}"; do
        local service="${service_endpoint%%:*}"
        local endpoint="${service_endpoint#*:}"
        
        # Get container name
        local container=$(docker ps --format "table {{.Names}}" | grep -E "${service}" | head -1)
        
        if [ -z "$container" ]; then
            print_error "$service container not found"
            all_healthy=false
            continue
        fi
        
        # Check health endpoint
        if docker exec "$container" curl -f -s "http://localhost:${endpoint}" >/dev/null 2>&1; then
            print_success "$service is healthy"
        else
            print_error "$service health check failed"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = false ]; then
        print_error "Some services failed health checks"
        return 1
    fi
    
    print_success "All services are healthy"
    return 0
}

# Function to update database
update_database() {
    print_info "Checking database migrations..."
    
    # Run any pending migrations
    if [ -f "bot_chain/schemas/migrations" ]; then
        docker exec ceci-bot-chain-postgres-1 psql -U postgres -d ceci_bot_chain -f /migrations/*.sql
    fi
    
    print_success "Database is up to date"
}

# Main deployment function
deploy() {
    local build_flag="$1"
    
    log "Deployment started"
    
    # Pull latest code
    print_info "Pulling latest code from repository..."
    git pull origin main
    
    # Load production environment
    export $(grep -v '^#' .env.prod | xargs)
    
    # Backup current images
    backup_images
    
    if [ "$build_flag" != "--no-build" ]; then
        # Build new images
        print_info "Building Docker images..."
        $DOCKER_COMPOSE_CMD $PROD_COMPOSE_FILES build --parallel
    else
        print_info "Skipping build (--no-build flag)"
    fi
    
    # Stop old containers
    print_info "Stopping current containers..."
    $DOCKER_COMPOSE_CMD $PROD_COMPOSE_FILES down
    
    # Start new containers
    print_info "Starting new containers..."
    $DOCKER_COMPOSE_CMD $PROD_COMPOSE_FILES up -d
    
    # Update database if needed
    update_database
    
    # Run health checks
    if run_health_checks; then
        print_success "Deployment completed successfully!"
        log "Deployment completed successfully"
        
        # Clean up old images
        print_info "Cleaning up old images..."
        docker image prune -f
    else
        print_error "Deployment failed health checks"
        log "Deployment failed - health checks failed"
        
        # Ask for rollback
        read -p "Do you want to rollback? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rollback
        fi
        exit 1
    fi
}

# Main script
main() {
    print_info "CECI Bot Chain Production Deployment"
    print_info "====================================="
    
    # Check prerequisites
    check_docker
    check_required_files
    
    # Parse arguments
    case "${1:-deploy}" in
        --rollback)
            rollback
            ;;
        --no-build|deploy)
            deploy "${1:-deploy}"
            ;;
        --help)
            echo "Usage: $0 [--no-build] [--rollback]"
            echo "  --no-build   Deploy without rebuilding images"
            echo "  --rollback   Rollback to previous version"
            echo "  --help       Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
    
    # Show final status
    print_info "Container status:"
    $DOCKER_COMPOSE_CMD $PROD_COMPOSE_FILES ps
    
    print_info "Deployment log: $DEPLOYMENT_LOG"
}

# Run main function
main "$@"