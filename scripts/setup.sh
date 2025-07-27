#!/bin/bash

# IntelliDoc AI Setup Script
# Initializes the development environment

set -e

echo "🚀 IntelliDoc AI - Development Setup"
echo "===================================="

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check system requirements
echo "📊 Checking system requirements..."

# Check available memory
available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
if [ "$available_memory" -lt 6000 ]; then
    echo "⚠️  Warning: Available memory is ${available_memory}MB. Recommended: 8GB+"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check available disk space
available_space=$(df . | awk 'NR==2 {print $4}')
if [ "$available_space" -lt 20971520 ]; then  # 20GB in KB
    echo "⚠️  Warning: Available disk space is low. Recommended: 20GB+"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Prerequisites check passed"

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    
    # Generate secure secrets
    echo "🔐 Generating secure secrets..."
    
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
    
    echo "✅ Environment file created with secure secrets"
else
    echo "✅ Environment file already exists"
fi

# Create storage directories
echo "📁 Creating storage directories..."
mkdir -p backend/storage/{uploads,processed,temp,models,vectors}
mkdir -p ml-models/{classification,entity-extraction,embeddings,language-detection}

# Set permissions
chmod 755 backend/storage/
chmod 755 backend/storage/*
chmod +x ml-models/download-models.sh
chmod +x scripts/*.sh

echo "✅ Storage directories created"

# Download ML models
echo "🤖 Downloading ML models..."
if [ "$1" = "--skip-models" ]; then
    echo "⏭️  Skipping ML models download (can be done later with: ./ml-models/download-models.sh)"
else
    echo "📥 This will download ~1.4GB of ML models. It may take a while..."
    read -p "Download ML models now? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "⏭️  Skipping ML models download (can be done later with: ./ml-models/download-models.sh)"
    else
        cd ml-models
        ./download-models.sh
        cd ..
    fi
fi

# Pull Docker images
echo "🐳 Pulling Docker images..."
docker-compose pull

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "🚀 Quick Start:"
echo "==============="
echo "1. Start development environment:"
echo "   ./scripts/dev-start.sh"
echo ""
echo "2. Access the application:"
echo "   • Frontend: http://localhost:3000"
echo "   • API: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • Grafana: http://localhost:3001 (admin/admin)"
echo ""
echo "3. Stop environment:"
echo "   docker-compose down"
echo ""
echo "📚 For more information, see:"
echo "   • README.md"
echo "   • docs/DEPLOYMENT.md"
echo "   • docs/API.md"
