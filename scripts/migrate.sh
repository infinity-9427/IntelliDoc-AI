#!/bin/bash

# IntelliDoc AI Migration Script
# Handles database migrations and updates

set -e

echo "🔄 IntelliDoc AI - Database Migration"
echo "===================================="

# Check if services are running
COMPOSE_FILE="docker-compose.yml"
if docker-compose -f docker-compose.prod.yml ps postgres 2>/dev/null | grep -q "Up"; then
    COMPOSE_FILE="docker-compose.prod.yml"
    echo "🏭 Using production configuration"
elif docker-compose -f docker-compose.yml ps postgres 2>/dev/null | grep -q "Up"; then
    COMPOSE_FILE="docker-compose.yml"
    echo "🧪 Using development configuration"
else
    echo "❌ No running database found. Please start the services first."
    exit 1
fi

# Function to run alembic commands
run_alembic() {
    docker-compose -f "$COMPOSE_FILE" exec backend alembic "$@"
}

# Function to backup database before migration
backup_before_migration() {
    echo "💾 Creating backup before migration..."
    BACKUP_FILE="pre_migration_backup_$(date +%Y%m%d_%H%M%S).sql"
    docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump \
        -U intellidoc_user \
        -d intellidoc_db \
        --no-owner --no-privileges > "backups/$BACKUP_FILE"
    echo "✅ Backup created: backups/$BACKUP_FILE"
}

# Create backups directory
mkdir -p backups

# Parse command line arguments
COMMAND=${1:-"upgrade"}

case "$COMMAND" in
    "upgrade"|"up")
        echo "⬆️  Running database upgrade..."
        backup_before_migration
        run_alembic upgrade head
        echo "✅ Database upgrade completed"
        ;;
    
    "downgrade"|"down")
        if [ -z "$2" ]; then
            echo "❌ Downgrade requires a revision. Usage: $0 downgrade <revision>"
            echo "   Use 'base' to downgrade to empty database"
            echo "   Use '-1' to downgrade one revision"
            exit 1
        fi
        echo "⬇️  Running database downgrade to $2..."
        backup_before_migration
        run_alembic downgrade "$2"
        echo "✅ Database downgrade completed"
        ;;
    
    "create"|"revision")
        if [ -z "$2" ]; then
            echo "❌ Create revision requires a message. Usage: $0 create '<message>'"
            exit 1
        fi
        echo "📝 Creating new migration revision..."
        run_alembic revision --autogenerate -m "$2"
        echo "✅ Migration revision created"
        ;;
    
    "history")
        echo "📋 Migration history:"
        run_alembic history --verbose
        ;;
    
    "current")
        echo "📍 Current database revision:"
        run_alembic current --verbose
        ;;
    
    "heads")
        echo "🔝 Available migration heads:"
        run_alembic heads --verbose
        ;;
    
    "show")
        if [ -z "$2" ]; then
            echo "❌ Show requires a revision. Usage: $0 show <revision>"
            exit 1
        fi
        echo "🔍 Showing migration details for $2:"
        run_alembic show "$2"
        ;;
    
    "stamp")
        if [ -z "$2" ]; then
            echo "❌ Stamp requires a revision. Usage: $0 stamp <revision>"
            exit 1
        fi
        echo "🏷️  Stamping database with revision $2..."
        run_alembic stamp "$2"
        echo "✅ Database stamped"
        ;;
    
    "init")
        echo "🏗️  Initializing database schema..."
        backup_before_migration
        run_alembic upgrade head
        
        # Create initial admin user if script exists
        if docker-compose -f "$COMPOSE_FILE" exec backend ls app/scripts/create_admin.py >/dev/null 2>&1; then
            echo "👤 Creating initial admin user..."
            docker-compose -f "$COMPOSE_FILE" exec backend python app/scripts/create_admin.py
        fi
        
        echo "✅ Database initialization completed"
        ;;
    
    "reset")
        echo "⚠️  This will completely reset the database!"
        read -p "Are you sure? This cannot be undone. (type 'yes'): " confirmation
        if [ "$confirmation" = "yes" ]; then
            backup_before_migration
            echo "🗑️  Dropping all tables..."
            run_alembic downgrade base
            echo "🏗️  Recreating tables..."
            run_alembic upgrade head
            echo "✅ Database reset completed"
        else
            echo "❌ Reset cancelled"
            exit 1
        fi
        ;;
    
    "check")
        echo "🔍 Checking database status..."
        
        # Check database connection
        if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U intellidoc_user -d intellidoc_db >/dev/null 2>&1; then
            echo "✅ Database connection: OK"
        else
            echo "❌ Database connection: FAILED"
            exit 1
        fi
        
        # Check current revision
        CURRENT_REV=$(run_alembic current 2>/dev/null | grep -o '[a-f0-9]\{12\}' | head -1)
        if [ -n "$CURRENT_REV" ]; then
            echo "✅ Current revision: $CURRENT_REV"
        else
            echo "⚠️  No revision information found"
        fi
        
        # Check if upgrade is needed
        HEAD_REV=$(run_alembic heads 2>/dev/null | grep -o '[a-f0-9]\{12\}' | head -1)
        if [ "$CURRENT_REV" = "$HEAD_REV" ]; then
            echo "✅ Database is up to date"
        else
            echo "⚠️  Database upgrade available (head: $HEAD_REV)"
        fi
        ;;
    
    "help"|"--help"|"-h")
        echo "📖 IntelliDoc AI Migration Script Usage"
        echo "======================================"
        echo ""
        echo "Commands:"
        echo "  upgrade, up          - Upgrade database to latest revision"
        echo "  downgrade, down <rev> - Downgrade database to specific revision"
        echo "  create <message>     - Create new migration revision"
        echo "  history              - Show migration history"
        echo "  current              - Show current database revision"
        echo "  heads                - Show available migration heads"
        echo "  show <revision>      - Show details of specific revision"
        echo "  stamp <revision>     - Mark database as being at specific revision"
        echo "  init                 - Initialize database (first time setup)"
        echo "  reset                - Reset database (destructive!)"
        echo "  check                - Check database status"
        echo "  help                 - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 upgrade                    # Upgrade to latest"
        echo "  $0 create 'Add user table'    # Create new migration"
        echo "  $0 downgrade -1               # Downgrade one revision"
        echo "  $0 show abc123def456          # Show specific migration"
        ;;
    
    *)
        echo "❌ Unknown command: $COMMAND"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

echo ""
echo "✅ Migration operation completed successfully!"
