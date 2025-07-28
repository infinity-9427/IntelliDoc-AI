#!/bin/bash

# IntelliDoc AI - Complete Setup Script
# Initializes the entire system for production-ready deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
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

echo "🚀 IntelliDoc AI - Complete System Setup"
echo "========================================"

# Check prerequisites
print_status "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose (both old and new syntax)
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Determine which docker compose command to use
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

print_status "Using Docker Compose command: $DOCKER_COMPOSE"

# Check system requirements
print_status "Checking system requirements..."

# Check available memory
available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
if [ "$available_memory" -lt 6000 ]; then
    print_warning "Available memory is ${available_memory}MB. Recommended: 8GB+"
    if [ "$1" != "--force" ]; then
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Check available disk space (need at least 10GB for complete system)
available_space=$(df . | awk 'NR==2 {print $4}')
if [ "$available_space" -lt 10485760 ]; then  # 10GB in KB
    print_warning "Available disk space is low. Need at least 10GB for models and data."
    if [ "$1" != "--force" ]; then
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

print_success "Prerequisites check passed"

# Function to cleanup existing containers
cleanup_existing() {
    print_status "Cleaning up existing containers..."
    
    $DOCKER_COMPOSE down --volumes --remove-orphans 2>/dev/null || true
    
    # Clean up any orphaned containers
    docker container prune -f >/dev/null 2>&1 || true
    docker volume prune -f >/dev/null 2>&1 || true
    
    print_success "Cleanup completed"
}

# Create environment file if it doesn't exist
setup_environment() {
    if [ ! -f .env ]; then
        print_status "Creating environment file..."
        
        # Check if .env.example exists
        if [ ! -f .env.example ]; then
            print_status "Creating default .env file..."
            cat > .env << EOF
# Database Configuration
POSTGRES_DB=intellidoc_ai
POSTGRES_USER=intellidoc_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# MinIO Configuration
MINIO_ROOT_USER=intellidoc
MINIO_ROOT_PASSWORD=$(openssl rand -base64 32)
MINIO_ENDPOINT=http://minio:9000
MINIO_BUCKET_NAME=intellidoc-storage

# Application Configuration
SECRET_KEY=$(openssl rand -base64 32)
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Ollama Configuration
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Elasticsearch Configuration
ELASTICSEARCH_HOST=http://elasticsearch:9200

# Monitoring Configuration
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 32)

# Celery Configuration
USE_CELERY=true
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
EOF
        else
            cp .env.example .env
            
            # Generate secure secrets
            print_status "Generating secure secrets..."
            
            # Generate secure passwords
            POSTGRES_PASSWORD=$(openssl rand -base64 32)
            MINIO_SECRET_KEY=$(openssl rand -base64 32)
            SECRET_KEY=$(openssl rand -base64 32)
            GRAFANA_SECRET_KEY=$(openssl rand -base64 32)
            
            # Update .env file
            sed -i "s/your_secure_postgres_password_here/$POSTGRES_PASSWORD/" .env
            sed -i "s/your_secure_minio_password_here/$MINIO_SECRET_KEY/" .env
            sed -i "s/your_very_secure_secret_key_here_32_chars_minimum/$SECRET_KEY/" .env
            sed -i "s/your_grafana_secret_key_here/$GRAFANA_SECRET_KEY/" .env
        fi
        
        print_success "Environment file created with secure secrets"
    else
        print_success "Environment file already exists"
    fi
}

# Create storage directories
setup_storage() {
    print_status "Creating storage directories..."
    mkdir -p backend/storage/{uploads,processed,temp,models,vectors}
    mkdir -p ml-models/{classification,entity-extraction,embeddings,language-detection}

    # Set permissions
    chmod 755 backend/storage/
    chmod 755 backend/storage/*
    chmod +x ml-models/download-models.sh 2>/dev/null || true
    chmod +x scripts/*.sh 2>/dev/null || true

    print_success "Storage directories created"
}

# Function to build and start services
build_and_start() {
    print_status "Building and starting IntelliDoc AI services..."
    
    # Build all services
    print_status "Building Docker images... (this may take several minutes)"
    $DOCKER_COMPOSE build --no-cache
    
    # Start infrastructure services first
    print_status "Starting infrastructure services..."
    $DOCKER_COMPOSE up -d postgres redis elasticsearch minio
    
    # Wait for infrastructure to be ready
    print_status "Waiting for infrastructure services to be ready..."
    sleep 15
    
    # Start Ollama (which will download models automatically)
    print_status "Starting Ollama service and downloading AI models..."
    print_warning "First-time model download may take 10-15 minutes"
    $DOCKER_COMPOSE up -d ollama
    
    # Start application services
    print_status "Starting application services..."
    $DOCKER_COMPOSE up -d backend celery-worker celery-beat frontend
    
    # Start monitoring services
    print_status "Starting monitoring services..."
    $DOCKER_COMPOSE up -d prometheus grafana 2>/dev/null || print_warning "Monitoring services not available"
    
    print_success "All services started successfully!"
}

# Function to wait for Ollama models
wait_for_ollama() {
    print_status "Waiting for Ollama models to download..."
    timeout=900  # 15 minutes
    elapsed=0
    
    while [ $elapsed -lt $timeout ]; do
        if $DOCKER_COMPOSE exec -T ollama ollama list 2>/dev/null | grep -q "llama3.2:3b" && 
           $DOCKER_COMPOSE exec -T ollama ollama list 2>/dev/null | grep -q "nomic-embed-text"; then
            print_success "Ollama models downloaded successfully!"
            return 0
        fi
        
        if [ $((elapsed % 30)) -eq 0 ]; then
            print_status "Still downloading models... (${elapsed}s elapsed)"
        fi
        
        sleep 5
        elapsed=$((elapsed + 5))
    done
    
    print_warning "Model download timeout, but system will continue working in basic mode"
    return 1
}

# Function to verify services
verify_services() {
    print_status "Verifying service health..."
    
    # Wait a moment for services to stabilize
    sleep 10
    
    # Check service health
    services=("postgres" "redis" "elasticsearch" "minio" "ollama" "backend" "frontend")
    all_healthy=true
    
    for service in "${services[@]}"; do
        if $DOCKER_COMPOSE ps "$service" 2>/dev/null | grep -q "running\|healthy"; then
            print_success "$service is running"
        else
            print_warning "$service may need more time to start"
            all_healthy=false
        fi
    done
    
    if $all_healthy; then
        print_success "All core services are healthy!"
    else
        print_warning "Some services may need more time to start. Check with: $DOCKER_COMPOSE ps"
    fi
}

# Function to show access information
show_access_info() {
    echo ""
    echo "🎉 IntelliDoc AI Setup Complete!"
    echo "======================================"
    echo ""
    echo "📊 Service Access URLs:"
    echo "  • Frontend (Main App):    http://localhost:3000"
    echo "  • Backend API:           http://localhost:8000"
    echo "  • API Documentation:     http://localhost:8000/docs"
    echo "  • Grafana Monitoring:    http://localhost:3001"
    echo "  • MinIO Storage:         http://localhost:9001"
    echo ""
    echo "🔧 Useful Commands:"
    echo "  • View logs:             $DOCKER_COMPOSE logs -f"
    echo "  • Stop all services:     $DOCKER_COMPOSE down"
    echo "  • Restart services:      $DOCKER_COMPOSE restart"
    echo "  • View service status:   $DOCKER_COMPOSE ps"
    echo ""
    echo "� Check .env file for default credentials"
    echo ""
    print_success "System is ready for intelligent document processing!"
}

# Handle script interruption
trap 'print_error "Setup interrupted!"; exit 1' INT TERM

# Main execution
main() {
    case "${1:-}" in
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --force          Skip interactive prompts"
            echo "  --skip-models    Skip Ollama model download verification"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "This script will:"
            echo "  1. Check system requirements"
            echo "  2. Setup environment configuration"
            echo "  3. Create necessary directories"
            echo "  4. Build and start all Docker services"
            echo "  5. Download AI models automatically"
            echo "  6. Verify system health"
            exit 0
            ;;
    esac
    
    cleanup_existing
    setup_environment
    setup_storage
    build_and_start
    
    if [ "$1" != "--skip-models" ]; then
        wait_for_ollama
    fi
    
    verify_services
    show_access_info
}

# Run main function
main "$@"
