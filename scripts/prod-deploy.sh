#!/bin/bash

# IntelliDoc AI Production Deployment Script
# Deploys the application in production mode

set -e

echo "🚀 IntelliDoc AI - Production Deployment"
echo "========================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run ./scripts/setup.sh first."
    exit 1
fi

# Production environment check
echo "🔍 Production Environment Check"
echo "==============================="

# Check required environment variables
required_vars=("POSTGRES_PASSWORD" "SECRET_KEY" "MINIO_SECRET_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env || grep -q "^${var}=your_" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing or default values for required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "  • $var"
    done
    echo ""
    echo "Please update these variables in .env file with secure values."
    exit 1
fi

# Check SSL certificates (optional but recommended)
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    echo "⚠️  SSL certificates not found in nginx/ssl/"
    echo "   For production, it's recommended to use HTTPS."
    read -p "Continue without SSL? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please add SSL certificates to nginx/ssl/ directory:"
        echo "  • cert.pem - SSL certificate"
        echo "  • key.pem - Private key"
        exit 1
    fi
fi

# Check system resources
echo "📊 System Resource Check"
echo "======================="

# Check available memory
available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
if [ "$available_memory" -lt 8000 ]; then
    echo "⚠️  Warning: Available memory is ${available_memory}MB. Recommended for production: 16GB+"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check available disk space
available_space=$(df . | awk 'NR==2 {print $4}')
if [ "$available_space" -lt 52428800 ]; then  # 50GB in KB
    echo "⚠️  Warning: Available disk space is low. Recommended for production: 100GB+"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ System checks passed"

# Backup existing data (if any)
if docker volume ls | grep -q intellidoc; then
    echo "💾 Creating backup of existing data..."
    backup_dir="backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup database
    if docker-compose ps postgres | grep -q "Up"; then
        docker-compose exec -T postgres pg_dump -U intellidoc_user intellidoc_db > "$backup_dir/database.sql"
        echo "✅ Database backup created: $backup_dir/database.sql"
    fi
    
    # Backup uploaded files
    if [ -d "backend/storage" ]; then
        tar -czf "$backup_dir/storage.tar.gz" backend/storage/
        echo "✅ Storage backup created: $backup_dir/storage.tar.gz"
    fi
fi

# Stop development services if running
if docker-compose ps | grep -q "Up"; then
    echo "🛑 Stopping development services..."
    docker-compose down
fi

# Pull latest images
echo "🐳 Pulling production images..."
docker-compose -f docker-compose.prod.yml pull

# Build custom images
echo "🏗️  Building production images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Set production environment
export NODE_ENV=production
export ENVIRONMENT=production

# Start production services
echo "🚀 Starting production services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for production services..."

# Wait for PostgreSQL
echo "  📊 Waiting for PostgreSQL..."
timeout=60
while ! docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U intellidoc_user -d intellidoc_db > /dev/null 2>&1; do
    sleep 2
    timeout=$((timeout - 2))
    if [ $timeout -le 0 ]; then
        echo "❌ PostgreSQL failed to start"
        docker-compose -f docker-compose.prod.yml logs postgres
        exit 1
    fi
done
echo "  ✅ PostgreSQL is ready"

# Run database migrations
echo "  🗄️  Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

# Wait for other services
services=("redis" "elasticsearch" "minio" "backend" "frontend")
for service in "${services[@]}"; do
    echo "  ⏳ Waiting for $service..."
    timeout=120
    while ! docker-compose -f docker-compose.prod.yml ps $service | grep -q "Up"; do
        sleep 3
        timeout=$((timeout - 3))
        if [ $timeout -le 0 ]; then
            echo "❌ $service failed to start"
            docker-compose -f docker-compose.prod.yml logs $service
            exit 1
        fi
    done
    echo "  ✅ $service is ready"
done

# Health checks
echo "🔍 Running health checks..."

# API health check
timeout=60
while ! curl -f http://localhost:8000/health > /dev/null 2>&1; do
    sleep 3
    timeout=$((timeout - 3))
    if [ $timeout -le 0 ]; then
        echo "❌ Backend API health check failed"
        docker-compose -f docker-compose.prod.yml logs backend
        exit 1
    fi
done
echo "✅ Backend API health check passed"

# Frontend health check
timeout=60
while ! curl -f http://localhost:3000 > /dev/null 2>&1; do
    sleep 3
    timeout=$((timeout - 3))
    if [ $timeout -le 0 ]; then
        echo "❌ Frontend health check failed"
        docker-compose -f docker-compose.prod.yml logs frontend
        exit 1
    fi
done
echo "✅ Frontend health check passed"

# Show service status
echo ""
echo "📊 Production Service Status:"
echo "============================="
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🎉 Production deployment completed successfully!"
echo ""
echo "🌐 Production Access Points:"
echo "============================"
echo "• 🖥️  Application:     http://localhost:3000"
echo "• 🔧 API:             http://localhost:8000"
echo "• 📚 API Docs:        http://localhost:8000/docs"
echo "• 📊 Monitoring:      http://localhost:3001"
echo ""
echo "🔧 Production Management:"
echo "========================"
echo "• View logs:          docker-compose -f docker-compose.prod.yml logs -f [service]"
echo "• Stop all:           docker-compose -f docker-compose.prod.yml down"
echo "• Restart service:    docker-compose -f docker-compose.prod.yml restart [service]"
echo "• Scale workers:      docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=4"
echo ""
echo "📈 Monitoring:"
echo "============="
echo "• System metrics:     http://localhost:9090 (Prometheus)"
echo "• Application logs:   docker-compose -f docker-compose.prod.yml logs"
echo "• Health endpoint:    curl http://localhost:8000/health"
echo ""
echo "🔒 Security Recommendations:"
echo "============================"
echo "• Set up SSL/TLS certificates"
echo "• Configure firewall rules"
echo "• Enable log rotation"
echo "• Set up automated backups"
echo "• Monitor for security updates"
echo ""
echo "💾 Backup Location:"
if [ -n "$backup_dir" ]; then
    echo "• Previous data backup: $backup_dir/"
fi
echo "• Create regular backups with: ./scripts/backup.sh"

# Show resource usage
echo ""
echo "💾 Resource Usage:"
echo "=================="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
