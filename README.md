# IntelliDoc AI - Smart Document Intelligence Platform

## 🚀 Overview
Transform any document into actionable insights using cutting-edge AI. Built for global organizations that need enterprise-grade document processing without the enterprise costs. Features a fully internationalized interface supporting 6 languages with seamless document processing in 100+ languages.

## 🎯 The Problem
Organizations struggle with:
- Manual document processing that takes hours
- Extracting structured data from unstructured documents
- Language barriers in global document workflows
- High costs of enterprise document processing solutions
- Data privacy concerns with cloud-based services

## ✨ Our Solution
IntelliDoc AI provides:
- **Intelligent Document Processing** - Automatically extract text, entities, and insights from any document
- **Multi-Language Support** - Process documents in 100+ languages seamlessly
- **Privacy-First Design** - All processing happens on your infrastructure
- **Enterprise Features** - Advanced analytics, batch processing, and API integration
- **Zero Licensing Costs** - Completely free and open-source

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- 8GB RAM minimum (16GB recommended)
- 15GB free disk space (for AI models)
- Internet connection for initial model download

### One-Command Setup
```bash
# 1. Clone the repository
git clone https://github.com/infinity-9427/IntelliDoc-AI.git
cd IntelliDoc-AI

# 2. Start everything (includes automatic AI model download)
docker compose up --build -d
```

**That's it!** 🎉 

### What Happens Automatically:
1. **Infrastructure Setup** - PostgreSQL, Redis, Elasticsearch, MinIO
2. **AI Model Download** - LLaMA 3.2:3b (2GB) + Embedding models (274MB)
3. **Service Startup** - Backend, Frontend, and all components
4. **Health Checks** - Ensures everything is running correctly

### Initial Setup Time:
- **First run**: 5-8 minutes (includes model downloads)
- **Subsequent runs**: 30-60 seconds

### Access Your Application
- **Web Interface**: http://localhost:3000 (Available in 6 languages)
- **API Documentation**: http://localhost:8000/docs
- **Monitoring Dashboard**: http://localhost:3001 (Grafana)
- **System Metrics**: http://localhost:9090 (Prometheus)

**Language Access**: Simply add the language code to the URL:
- English: http://localhost:3000/en
- Spanish: http://localhost:3000/es  
- German: http://localhost:3000/de
- French: http://localhost:3000/fr
- Italian: http://localhost:3000/it
- Portuguese: http://localhost:3000/pr

## 🐳 Docker Architecture

### Container Services
The application runs as a multi-container Docker stack:

#### Core Services
- **Backend** (`intellidoc-backend`) - FastAPI application with OCR and AI capabilities
- **Frontend** (`intellidoc-frontend`) - Next.js web interface
- **Ollama** (`intellidoc-ollama`) - LLM inference server with auto-model download

#### Infrastructure Services  
- **PostgreSQL** (`intellidoc-postgres`) - Primary database
- **Redis** (`intellidoc-redis`) - Caching and session storage
- **Elasticsearch** (`intellidoc-elasticsearch`) - Document search and indexing
- **MinIO** (`intellidoc-minio`) - Object storage for files

#### Monitoring Stack
- **Prometheus** (`intellidoc-prometheus`) - Metrics collection
- **Grafana** (`intellidoc-grafana`) - Monitoring dashboards

### Container Health & Status
```bash
# Check all services status
docker compose ps

# View service logs
docker compose logs [service-name]

# Check AI models availability
docker exec intellidoc-ollama ollama list
```

### Development Mode
For development with debug logging and faster restart:
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

## 🔧 Troubleshooting

### Common Issues

#### Models Not Downloaded
```bash
# Restart Ollama service to retry model download
docker compose restart ollama

# Check download progress
docker logs intellidoc-ollama -f
```

#### Port Conflicts
If ports are already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Change frontend port
  - "8001:8000"  # Change backend port
```

#### Memory Issues
For systems with limited RAM:
```bash
# Monitor resource usage
docker stats

# Stop non-essential services
docker compose stop grafana prometheus
```

#### Complete Reset
```bash
# Stop and remove all containers and volumes
docker compose down -v

# Rebuild everything from scratch
docker compose up --build -d
```

### Verification Steps
1. **Check Container Health**: `docker compose ps`
2. **Verify AI Models**: `docker exec intellidoc-ollama ollama list`
3. **Test Frontend**: Visit http://localhost:3000
4. **Test Backend API**: Visit http://localhost:8000/docs
5. **Upload Test Document**: Use the web interface to process a sample PDF

### Comprehensive Localization
- **6 Fully Translated Languages** - Complete interface localization
- **Smart Language Switcher** - Seamless switching between languages
- **URL-Based Routing** - Bookmarkable language-specific URLs
- **Native Language Display** - Language names shown in their native script
- **Cultural Adaptation** - Date, number, and currency formatting per locale

### Global Document Processing
- **100+ Language OCR** - Extract text from documents in any language
- **Mixed-Language Documents** - Handle documents with multiple languages
- **Unicode Support** - Full support for all character sets and scripts
- **Right-to-Left Text** - Proper handling of RTL languages like Arabic and Hebrew

## ✨ Key Features

### Document Intelligence
- **Smart Classification** - Automatically identify document types (invoices, contracts, reports, resumes)
- **Entity Extraction** - Extract names, dates, amounts, addresses, and other key information
- **Content Analysis** - Generate summaries, analyze sentiment, and detect key insights
- **Quality Assessment** - Confidence scoring and processing recommendations

### Multi-Language Processing & Interface
- **Document Processing** - Process documents in 100+ languages with advanced OCR
- **Internationalized Interface** - Complete UI translation in 6 languages:
  - 🇺🇸 **English** - Full interface support
  - 🇪🇸 **Spanish** - Complete Spanish localization  
  - 🇩🇪 **German** - Full German interface
  - 🇫🇷 **French** - Complete French translation
  - 🇮🇹 **Italian** - Full Italian localization
  - 🇵🇹 **Portuguese** - Complete Portuguese interface
- **Smart Language Detection** - Automatic language identification for documents
- **Cross-Language Search** - Find content across different languages
- **Global Accessibility** - Seamless language switching with URL-based routing

### Advanced Capabilities
- **Batch Processing** - Handle thousands of documents efficiently
- **Semantic Search** - Find similar documents using AI-powered search
- **Real-Time Processing** - Live progress updates and instant results
- **API Integration** - Complete REST API for system integration

## 🛡️ Security & Privacy
- **Local Processing** - All data stays on your infrastructure
- **Enterprise Security** - JWT authentication and role-based access
- **Audit Trails** - Complete processing history and logging
- **Compliance Ready** - GDPR and HIPAA compatible design

## � Getting Started

For developers and system administrators:

### Development Setup
```bash
cd backend
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn app.main:app --reload
```

```bash
cd frontend
pnpm install && pnpm dev
```

### Production Deployment
```bash
./scripts/prod-deploy.sh
```

## 📊 Performance & Monitoring
- **Real-time Dashboards** - Monitor system performance and usage
- **Health Checks** - Automated system status monitoring  
- **Resource Optimization** - Intelligent load balancing and scaling

## 🤝 Support & Documentation
- **Complete API Documentation** - Interactive Swagger/OpenAPI docs
- **Developer Guides** - Comprehensive setup and integration guides
- **Community Support** - Active development and issue resolution

## 📄 License
MIT License - Free for commercial and personal use
