# 🚀 IntelliDoc AI - Quick Start Guide

## ⚡ One-Command Deployment

```bash
# 1. Clone the repository
git clone <repository-url>
cd local-pdf-converter

# 2. Run the automated setup
./start.sh
```

**That's it!** The system will automatically handle everything.

## 🔧 What Happens Automatically

### ✅ System Check
- Verifies Docker installation
- Checks available memory (8GB+ recommended)
- Confirms disk space (10GB+ needed)

### ✅ Environment Setup
- Generates secure passwords and secrets
- Creates required directories
- Sets up configuration files

### ✅ Service Deployment
- Builds all Docker containers
- Starts infrastructure (PostgreSQL, Redis, Elasticsearch, MinIO)
- Downloads AI models (LLaMA 3.2:3b + nomic-embed-text)
- Launches application services (Backend, Frontend, Celery workers)
- Starts monitoring (Prometheus, Grafana)

### ✅ Health Verification
- Confirms all services are running
- Verifies AI models are loaded
- Validates API endpoints

## 📊 Access Points

After setup completes (8-12 minutes first time):

- **📱 Main Application**: http://localhost:3000
- **📋 API Documentation**: http://localhost:8000/docs
- **📈 Monitoring Dashboard**: http://localhost:3001
- **💾 Storage Interface**: http://localhost:9001

## 🔧 Management Commands

```bash
# View all services status
docker compose ps

# Check service logs
docker compose logs -f [service-name]

# Stop all services
docker compose down

# Restart specific service
docker compose restart [service-name]

# Verify AI models
docker exec intellidoc-ollama ollama list
```

## 🆘 Troubleshooting

### AI Models Not Loading
```bash
# Restart Ollama service
docker compose restart ollama

# Check Ollama logs
docker compose logs ollama

# Manually pull models
docker exec intellidoc-ollama ollama pull llama3.2:3b
docker exec intellidoc-ollama ollama pull nomic-embed-text
```

### Service Issues
```bash
# Check which services are unhealthy
docker compose ps

# View detailed logs for specific service
docker compose logs --tail=100 [service-name]

# Restart all services
docker compose restart
```

### Complete Reset
```bash
# Stop and remove everything
docker compose down --volumes --remove-orphans

# Clean up Docker system
docker system prune -f

# Start fresh
./start.sh
```

## 🎯 Alternative: Manual Docker Compose

If you prefer standard Docker Compose:

```bash
# Start with automatic build
docker compose up --build -d

# For development mode
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

## ⏱️ Timing Expectations

- **First deployment**: 8-12 minutes (includes model downloads)
- **Subsequent starts**: 1-2 minutes  
- **AI model downloads**: ~2.3GB total
- **Container builds**: 3-5 minutes

## 🌍 Multi-Language Support

Access the application in different languages:
- English: http://localhost:3000/en
- Spanish: http://localhost:3000/es
- German: http://localhost:3000/de
- French: http://localhost:3000/fr
- Italian: http://localhost:3000/it
- Portuguese: http://localhost:3000/pr
