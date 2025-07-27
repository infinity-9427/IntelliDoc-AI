#!/bin/bash

# IntelliDoc AI Backup Script
# Creates backups of database and file storage

set -e

echo "💾 IntelliDoc AI - Backup Script"
echo "================================"

# Configuration
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="intellidoc_backup_$TIMESTAMP"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# Create backup directory
mkdir -p "$BACKUP_PATH"

echo "📁 Creating backup: $BACKUP_NAME"

# Check if services are running
COMPOSE_FILE="docker-compose.yml"
if [ -f "docker-compose.prod.yml" ] && docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    COMPOSE_FILE="docker-compose.prod.yml"
    echo "🏭 Using production configuration"
else
    echo "🧪 Using development configuration"
fi

# Backup PostgreSQL database
echo "🗄️  Backing up PostgreSQL database..."
if docker-compose -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
    docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump \
        -U intellidoc_user \
        -d intellidoc_db \
        --verbose \
        --no-owner \
        --no-privileges > "$BACKUP_PATH/database.sql"
    
    # Compress database backup
    gzip "$BACKUP_PATH/database.sql"
    echo "✅ Database backup created: $BACKUP_PATH/database.sql.gz"
else
    echo "⚠️  PostgreSQL is not running, skipping database backup"
fi

# Backup file storage
echo "📄 Backing up file storage..."
if [ -d "backend/storage" ]; then
    tar -czf "$BACKUP_PATH/storage.tar.gz" \
        -C backend/ storage/ \
        --exclude="storage/temp/*" \
        --exclude="storage/logs/*"
    echo "✅ Storage backup created: $BACKUP_PATH/storage.tar.gz"
else
    echo "⚠️  Storage directory not found, skipping file backup"
fi

# Backup configuration
echo "⚙️  Backing up configuration..."
cp .env "$BACKUP_PATH/env.backup" 2>/dev/null || echo "⚠️  .env file not found"
cp docker-compose.yml "$BACKUP_PATH/" 2>/dev/null || true
cp docker-compose.prod.yml "$BACKUP_PATH/" 2>/dev/null || true

# Backup ML models info (not the models themselves - too large)
if [ -f "ml-models/model-info.json" ]; then
    cp ml-models/model-info.json "$BACKUP_PATH/"
    echo "✅ ML models info backed up"
fi

# Backup monitoring configuration
if [ -d "monitoring" ]; then
    tar -czf "$BACKUP_PATH/monitoring.tar.gz" monitoring/
    echo "✅ Monitoring configuration backed up"
fi

# Create backup metadata
cat > "$BACKUP_PATH/backup_info.json" << EOF
{
  "backup_name": "$BACKUP_NAME",
  "timestamp": "$TIMESTAMP",
  "date": "$(date -Iseconds)",
  "hostname": "$(hostname)",
  "compose_file": "$COMPOSE_FILE",
  "services_status": "$(docker-compose -f "$COMPOSE_FILE" ps --services 2>/dev/null || echo 'unknown')",
  "backup_size": "$(du -sh "$BACKUP_PATH" | cut -f1)",
  "contents": {
    "database": $([ -f "$BACKUP_PATH/database.sql.gz" ] && echo "true" || echo "false"),
    "storage": $([ -f "$BACKUP_PATH/storage.tar.gz" ] && echo "true" || echo "false"),
    "configuration": $([ -f "$BACKUP_PATH/env.backup" ] && echo "true" || echo "false"),
    "monitoring": $([ -f "$BACKUP_PATH/monitoring.tar.gz" ] && echo "true" || echo "false")
  }
}
EOF

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_PATH" | cut -f1)

echo ""
echo "✅ Backup completed successfully!"
echo ""
echo "📊 Backup Summary:"
echo "=================="
echo "• Backup location: $BACKUP_PATH"
echo "• Backup size: $BACKUP_SIZE"
echo "• Timestamp: $(date)"
echo ""
echo "📁 Backup contents:"
if [ -f "$BACKUP_PATH/database.sql.gz" ]; then
    echo "  ✅ Database backup"
fi
if [ -f "$BACKUP_PATH/storage.tar.gz" ]; then
    echo "  ✅ File storage backup"
fi
if [ -f "$BACKUP_PATH/env.backup" ]; then
    echo "  ✅ Configuration backup"
fi
if [ -f "$BACKUP_PATH/monitoring.tar.gz" ]; then
    echo "  ✅ Monitoring configuration backup"
fi

# Cleanup old backups (keep last 7 days)
echo ""
echo "🧹 Cleaning up old backups..."
find "$BACKUP_DIR" -type d -name "intellidoc_backup_*" -mtime +7 -exec rm -rf {} \; 2>/dev/null || true
echo "✅ Old backups cleaned up (keeping last 7 days)"

echo ""
echo "💡 Backup Tips:"
echo "==============="
echo "• Store backups in a secure, off-site location"
echo "• Test backup restoration regularly"
echo "• Consider encrypting sensitive backups"
echo "• Set up automated backup scheduling"
echo ""
echo "📋 Restore commands:"
echo "==================="
echo "• Database: gunzip < $BACKUP_PATH/database.sql.gz | docker-compose exec -T postgres psql -U intellidoc_user -d intellidoc_db"
echo "• Storage: tar -xzf $BACKUP_PATH/storage.tar.gz -C backend/"
echo "• Full restore: ./scripts/restore.sh $BACKUP_NAME"
