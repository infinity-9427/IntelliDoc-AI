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

## � Our Solution
IntelliDoc AI provides:
- **Intelligent Document Processing** - Automatically extract text, entities, and insights from any document
- **Multi-Language Support** - Process documents in 100+ languages seamlessly
- **Privacy-First Design** - All processing happens on your infrastructure
- **Enterprise Features** - Advanced analytics, batch processing, and API integration
- **Zero Licensing Costs** - Completely free and open-source

## 🚀 Quick Start

### Prerequisites
- Docker installed on your system
- 8GB RAM minimum
- 10GB free disk space

### Setup & Launch
```bash
# 1. Clone the repository
git clone <repository-url>
cd local-pdf-converter

# 2. Initialize the system
./scripts/setup.sh

# 3. Start the application
./scripts/dev-start.sh
```

### Access Your Application
- **Web Interface**: http://localhost:3000 (Available in 6 languages)
- **API Documentation**: http://localhost:8000/docs
- **Monitoring Dashboard**: http://localhost:3001

**Language Access**: Simply add the language code to the URL:
- English: http://localhost:3000/en
- Spanish: http://localhost:3000/es  
- German: http://localhost:3000/de
- French: http://localhost:3000/fr
- Italian: http://localhost:3000/it
- Portuguese: http://localhost:3000/pr

## 🌍 International Features

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
