#!/bin/bash

# IntelliDoc AI - Complete Deployment Script
# One-click setup and deployment for the entire platform

echo "🚀 IntelliDoc AI - Complete Platform Deployment"
echo "==============================================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "Make sure you have both 'backend' and 'frontend' directories"
    exit 1
fi

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}This will set up the complete IntelliDoc AI platform with:${NC}"
echo "  ✓ PostgreSQL database"
echo "  ✓ Redis cache and task queue"
echo "  ✓ Elasticsearch search engine"
echo "  ✓ MinIO object storage"
echo "  ✓ Ollama AI models (LLaMA 3.2 + embeddings)"
echo "  ✓ Celery async task processing"
echo "  ✓ FastAPI backend with intelligent document processing"
echo "  ✓ Next.js frontend with real-time UI"
echo "  ✓ Grafana monitoring dashboard"
echo ""

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Run the comprehensive setup script
echo -e "${GREEN}Starting complete platform setup...${NC}"
echo ""

# Make setup script executable if not already
chmod +x scripts/setup.sh

# Run setup with any passed arguments
./scripts/setup.sh "$@"

# Deployment complete
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 IntelliDoc AI is fully operational!${NC}"
    echo -e "${GREEN}📄 Upload documents at http://localhost:3000 for AI-powered analysis${NC}"
fi
