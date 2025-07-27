#!/bin/bash

# IntelliDoc AI Development Start Script
# Starts the development environment with all services

set -e

echo "🚀 Starting IntelliDoc AI Development Environment"
echo "================================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run ./scripts/setup.sh first."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create network if it doesn't exist
echo "🌐 Setting up Docker network..."
docker network create intellidoc-network 2>/dev/null || true

# Start services
echo "🐳 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."

# Wait for PostgreSQL
echo "  📊 Waiting for PostgreSQL..."
timeout=60
while ! docker-compose exec -T postgres pg_isready -U intellidoc_user -d intellidoc_db > /dev/null 2>&1; do
    sleep 2
    timeout=$((timeout - 2))
    if [ $timeout -le 0 ]; then
        echo "❌ PostgreSQL failed to start within 60 seconds"
        docker-compose logs postgres
        exit 1
    fi
done
echo "  ✅ PostgreSQL is ready"

# Wait for Redis
echo "  🔴 Waiting for Redis..."
timeout=30
while ! docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    sleep 2
    timeout=$((timeout - 2))
    if [ $timeout -le 0 ]; then
        echo "❌ Redis failed to start within 30 seconds"
        docker-compose logs redis
        exit 1
    fi
done
echo "  ✅ Redis is ready"

# Wait for Elasticsearch
echo "  🔍 Waiting for Elasticsearch..."
timeout=90
while ! curl -f http://localhost:9200/_cluster/health > /dev/null 2>&1; do
    sleep 3
    timeout=$((timeout - 3))
    if [ $timeout -le 0 ]; then
        echo "❌ Elasticsearch failed to start within 90 seconds"
        docker-compose logs elasticsearch
        exit 1
    fi
done
echo "  ✅ Elasticsearch is ready"

# Wait for MinIO
echo "  🗄️  Waiting for MinIO..."
timeout=30
while ! curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1; do
    sleep 2
    timeout=$((timeout - 2))
    if [ $timeout -le 0 ]; then
        echo "❌ MinIO failed to start within 30 seconds"
        docker-compose logs minio
        exit 1
    fi
done
echo "  ✅ MinIO is ready"

# Wait for Backend API
echo "  ⚙️  Waiting for Backend API..."
timeout=120
while ! curl -f http://localhost:8000/health > /dev/null 2>&1; do
    sleep 3
    timeout=$((timeout - 3))
    if [ $timeout -le 0 ]; then
        echo "❌ Backend API failed to start within 120 seconds"
        echo "📋 Backend logs:"
        docker-compose logs backend
        exit 1
    fi
done
echo "  ✅ Backend API is ready"

# Wait for Frontend
echo "  🌐 Waiting for Frontend..."
timeout=60
while ! curl -f http://localhost:3000 > /dev/null 2>&1; do
    sleep 3
    timeout=$((timeout - 3))
    if [ $timeout -le 0 ]; then
        echo "❌ Frontend failed to start within 60 seconds"
        docker-compose logs frontend
        exit 1
    fi
done
echo "  ✅ Frontend is ready"

# Show service status
echo ""
echo "📊 Service Status:"
echo "=================="
docker-compose ps

echo ""
echo "🎉 All services are running!"
echo ""
echo "🌐 Access Points:"
echo "================"
echo "• 🖥️  Frontend:        http://localhost:3000"
echo "• 🔧 Backend API:     http://localhost:8000"
echo "• 📚 API Docs:        http://localhost:8000/docs"
echo "• 📊 Grafana:         http://localhost:3001 (admin/admin)"
echo "• 🔍 Elasticsearch:   http://localhost:9200"
echo "• 🗄️  MinIO Console:   http://localhost:9001 (intellidoc/[password])"
echo "• 📈 Prometheus:      http://localhost:9090"
echo ""
echo "📝 Useful Commands:"
echo "=================="
echo "• View logs:          docker-compose logs -f [service]"
echo "• Stop all:           docker-compose down"
echo "• Restart service:    docker-compose restart [service]"
echo "• Shell access:       docker-compose exec [service] /bin/bash"
echo ""
echo "🔍 Health Check:"
echo "==============="
echo "• API Health:         curl http://localhost:8000/health"
echo "• Upload test:        curl -X POST -F 'file=@test.pdf' http://localhost:8000/api/v1/upload"
echo ""
echo "💡 Tips:"
echo "========"
echo "• First upload may take longer due to ML model initialization"
echo "• Check logs if you encounter issues: docker-compose logs [service]"
echo "• For production deployment, use: ./scripts/prod-deploy.sh"

# Show resource usage
echo ""
echo "💾 Resource Usage:"
echo "=================="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
