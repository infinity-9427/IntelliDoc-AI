# Deployment Guide

## Overview

This guide covers deployment options for IntelliDoc AI, from local development to production environments.

## Prerequisites

- Docker and Docker Compose
- 8GB RAM minimum (16GB recommended for production)
- 50GB free disk space
- SSL certificates (for production)

## Quick Deployment

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd local-pdf-converter

# Copy environment file
cp .env.example .env

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

Access points:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Grafana**: http://localhost:3001

### Production Deployment

```bash
# Clone repository
git clone <repository-url>
cd local-pdf-converter

# Configure environment
cp .env.example .env
# Edit .env with production values

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
./scripts/health-check.sh
```

## Environment Configuration

### Required Environment Variables

```bash
# Database
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=intellidoc_db
POSTGRES_USER=intellidoc_user

# Security
SECRET_KEY=your_32_character_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# Storage
MINIO_SECRET_KEY=your_minio_secret_key

# Monitoring
GRAFANA_ADMIN_PASSWORD=your_grafana_password
```

### Optional Configuration

```bash
# Email notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Webhooks
WEBHOOK_SECRET=your_webhook_secret

# Performance
CELERY_WORKER_CONCURRENCY=8
MAX_CONCURRENT_JOBS=20
```

## Infrastructure Requirements

### Minimum Requirements (Development)
- **CPU**: 2 cores
- **RAM**: 8GB
- **Storage**: 20GB
- **Network**: 10 Mbps

### Recommended (Production)
- **CPU**: 8 cores
- **RAM**: 32GB
- **Storage**: 500GB SSD
- **Network**: 100 Mbps

### Component Resource Usage

| Service | CPU | RAM | Storage |
|---------|-----|-----|---------|
| PostgreSQL | 1 core | 2GB | 10GB |
| Redis | 0.5 core | 1GB | 1GB |
| Elasticsearch | 2 cores | 4GB | 20GB |
| MinIO | 0.5 core | 1GB | 50GB+ |
| Backend | 2 cores | 4GB | 5GB |
| Celery Workers | 4 cores | 8GB | 2GB |
| Frontend | 1 core | 1GB | 1GB |
| Monitoring | 1 core | 2GB | 5GB |

## Container Orchestration

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml intellidoc

# Scale services
docker service scale intellidoc_celery-worker=4
docker service scale intellidoc_backend=2
```

### Kubernetes

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: intellidoc-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: intellidoc-backend
  template:
    metadata:
      labels:
        app: intellidoc-backend
    spec:
      containers:
      - name: backend
        image: intellidoc/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: intellidoc-secrets
              key: database-url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
```

Deploy to Kubernetes:
```bash
kubectl apply -f k8s/
kubectl get pods -l app=intellidoc
```

## Cloud Deployment

### AWS

#### Using ECS Fargate

```bash
# Build and push images
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

docker build -t intellidoc/backend ./backend
docker tag intellidoc/backend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/intellidoc/backend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/intellidoc/backend:latest

# Deploy using ECS CLI
ecs-cli compose --file docker-compose.aws.yml service up
```

#### Using EKS

```bash
# Create EKS cluster
eksctl create cluster --name intellidoc --region us-east-1 --nodes 3

# Deploy application
kubectl apply -f k8s/
```

### Google Cloud

#### Using Cloud Run

```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/PROJECT_ID/intellidoc-backend ./backend
gcloud run deploy intellidoc-backend --image gcr.io/PROJECT_ID/intellidoc-backend --platform managed

# Deploy frontend
gcloud builds submit --tag gcr.io/PROJECT_ID/intellidoc-frontend ./frontend
gcloud run deploy intellidoc-frontend --image gcr.io/PROJECT_ID/intellidoc-frontend --platform managed
```

#### Using GKE

```bash
# Create GKE cluster
gcloud container clusters create intellidoc --num-nodes=3

# Deploy application
kubectl apply -f k8s/
```

### Azure

#### Using Container Instances

```bash
# Create resource group
az group create --name intellidoc-rg --location eastus

# Deploy containers
az container create \
  --resource-group intellidoc-rg \
  --file docker-compose.azure.yml
```

#### Using AKS

```bash
# Create AKS cluster
az aks create --resource-group intellidoc-rg --name intellidoc-aks --node-count 3

# Deploy application
kubectl apply -f k8s/
```

## Database Setup

### PostgreSQL Configuration

```sql
-- Create database and user
CREATE DATABASE intellidoc_db;
CREATE USER intellidoc_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE intellidoc_db TO intellidoc_user;

-- Enable required extensions
\c intellidoc_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "vector"; -- for vector search
```

### Migration

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Create initial admin user
docker-compose exec backend python -m app.scripts.create_admin
```

## SSL/TLS Configuration

### Using Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificates
sudo certbot --nginx -d your-domain.com

# Auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### Custom Certificates

```nginx
# nginx/nginx.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Load Balancing

### Nginx Configuration

```nginx
upstream backend_servers {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

upstream frontend_servers {
    server frontend1:3000;
    server frontend2:3000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location / {
        proxy_pass http://frontend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### HAProxy Configuration

```
global
    daemon

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend intellidoc_frontend
    bind *:80
    default_backend intellidoc_backend

backend intellidoc_backend
    balance roundrobin
    server backend1 backend1:8000 check
    server backend2 backend2:8000 check
    server backend3 backend3:8000 check
```

## Monitoring Setup

### Prometheus Configuration

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'intellidoc-backend'
    static_configs:
      - targets: ['backend:8000']
    
  - job_name: 'intellidoc-postgres'
    static_configs:
      - targets: ['postgres:5432']
    
  - job_name: 'intellidoc-redis'
    static_configs:
      - targets: ['redis:6379']
```

### Grafana Dashboards

Import pre-built dashboards:
- Application metrics: `dashboards/application.json`
- Infrastructure metrics: `dashboards/infrastructure.json`
- Business metrics: `dashboards/business.json`

## Backup Strategy

### Database Backup

```bash
#!/bin/bash
# scripts/backup-db.sh

BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup
docker-compose exec -T postgres pg_dump -U intellidoc_user intellidoc_db > "$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### File Storage Backup

```bash
#!/bin/bash
# scripts/backup-files.sh

BACKUP_DIR="/backups/files"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup MinIO data
docker run --rm -v minio_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/minio_$TIMESTAMP.tar.gz /data

# Backup processed files
tar czf "$BACKUP_DIR/storage_$TIMESTAMP.tar.gz" backend/storage/
```

## Security Hardening

### Docker Security

```dockerfile
# Run as non-root user
FROM python:3.11-slim
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

# Read-only file system
docker run --read-only --tmpfs /tmp intellidoc/backend

# Security scanning
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image intellidoc/backend:latest
```

### Network Security

```yaml
# docker-compose.yml
networks:
  frontend:
    driver: bridge
    internal: false
  backend:
    driver: bridge
    internal: true
  database:
    driver: bridge
    internal: true

services:
  frontend:
    networks:
      - frontend
  
  backend:
    networks:
      - frontend
      - backend
  
  postgres:
    networks:
      - database
```

## Troubleshooting

### Common Issues

1. **Out of Memory**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase limits
   echo 'vm.max_map_count=262144' >> /etc/sysctl.conf
   sysctl -p
   ```

2. **Disk Space**
   ```bash
   # Clean up Docker
   docker system prune -a
   
   # Monitor disk usage
   df -h
   du -sh /var/lib/docker/
   ```

3. **Database Connection Issues**
   ```bash
   # Check database logs
   docker-compose logs postgres
   
   # Test connection
   docker-compose exec postgres psql -U intellidoc_user -d intellidoc_db
   ```

### Health Checks

```bash
#!/bin/bash
# scripts/health-check.sh

echo "Checking IntelliDoc AI health..."

# Check services
services=("postgres" "redis" "elasticsearch" "backend" "frontend")
for service in "${services[@]}"; do
    if docker-compose ps $service | grep -q "Up"; then
        echo "✓ $service is running"
    else
        echo "✗ $service is not running"
        exit 1
    fi
done

# Check API health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ API is healthy"
else
    echo "✗ API is not responding"
    exit 1
fi

echo "All services are healthy!"
```

## Performance Optimization

### Database Tuning

```sql
-- postgresql.conf optimizations
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
work_mem = 64MB
```

### Caching Strategy

```python
# Redis caching configuration
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'redis:6379',
        'OPTIONS': {
            'DB': 0,
            'COMPRESSOR': 'redis_cache.compressors.ZLibCompressor',
        },
        'TIMEOUT': 3600,  # 1 hour default
    }
}
```

### CDN Configuration

```nginx
# Static file caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary Accept-Encoding;
    gzip_static on;
}
```

This deployment guide provides comprehensive instructions for deploying IntelliDoc AI across various environments and platforms, ensuring reliable and scalable operation.
