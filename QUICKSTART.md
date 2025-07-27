# Quick Start Guide

## Automatic Setup (Recommended)

The entire application with all AI models will be automatically set up when you run:

```bash
# Clone the repository
git clone <your-repo-url>
cd local-pdf-converter

# Start everything (this will automatically download AI models)
docker compose up --build -d

# For development with debug logging
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

## What happens automatically:

1. **Ollama Service**: Starts and automatically downloads required AI models:
   - `llama3.2:3b` - Main language model for text processing
   - `nomic-embed-text` - Embedding model for semantic search

2. **Backend Services**: FastAPI application with OCR and AI capabilities

3. **Frontend**: Next.js web interface

4. **Infrastructure**: PostgreSQL, Redis, Elasticsearch, MinIO, monitoring stack

## First-time Setup Notes:

- **Initial startup takes 3-5 minutes** due to AI model downloads (~2GB total)
- Models are cached in Docker volumes for faster subsequent startups
- All services will automatically wait for Ollama models to be ready

## Verify Installation:

```bash
# Check all services are running
docker compose ps

# Check AI models are available
docker exec intellidoc-ollama ollama list

# Access the application
open http://localhost:3000
```

## Troubleshooting:

If Ollama fails to download models:
```bash
# Restart just the Ollama service
docker compose restart ollama

# Check logs
docker compose logs ollama
```

## Manual Model Management:

```bash
# Pull additional models
docker exec intellidoc-ollama ollama pull <model-name>

# List available models
docker exec intellidoc-ollama ollama list

# Remove a model
docker exec intellidoc-ollama ollama rm <model-name>
```
