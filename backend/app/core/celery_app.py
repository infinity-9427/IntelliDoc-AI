"""
Celery application configuration for IntelliDoc AI
Handles asynchronous document processing tasks
"""

import os
from celery import Celery
from app.config import get_settings

# Get application settings
settings = get_settings()

# Create Celery instance
celery_app = Celery(
    "intellidoc_ai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.celery_tasks"]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.tasks.celery_tasks.*": {"queue": "document_processing"},
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
        "retry_policy": {
            "timeout": 5.0
        }
    },
    
    # Task execution settings
    task_time_limit=1800,  # 30 minutes
    task_soft_time_limit=1500,  # 25 minutes
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-old-tasks": {
            "task": "app.tasks.celery_tasks.cleanup_old_tasks",
            "schedule": 3600.0,  # Run every hour
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks()

if __name__ == "__main__":
    celery_app.start()
