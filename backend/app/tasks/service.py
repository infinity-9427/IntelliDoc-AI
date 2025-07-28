"""
Task service factory for document processing
Provides interface to switch between in-memory and Celery task queues
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from app.models.schemas import ProcessingStatus

logger = logging.getLogger(__name__)

class TaskService:
    """Factory service for task queue management"""
    
    def __init__(self):
        self._queue = None
        self._initialize_queue()
    
    def _initialize_queue(self):
        """Initialize the appropriate task queue based on configuration"""
        use_celery = os.getenv("USE_CELERY", "true").lower() == "true"
        
        if use_celery:
            try:
                from app.tasks.celery_queue import celery_task_queue
                self._queue = celery_task_queue
                logger.info("Initialized Celery task queue")
            except ImportError as e:
                logger.warning(f"Failed to import Celery queue: {e}, falling back to in-memory queue")
                use_celery = False
        
        if not use_celery:
            from app.tasks.queue import task_queue
            self._queue = task_queue
            logger.info("Initialized in-memory task queue")
    
    async def submit_task(self, file_path: Path, filename: str) -> str:
        """Submit a new document processing task"""
        return await self._queue.submit_task(file_path, filename)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task"""
        return self._queue.get_task_status(task_id)
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all tasks (limited with Celery)"""
        return self._queue.get_all_tasks()
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task (if supported)"""
        if hasattr(self._queue, 'cancel_task'):
            return self._queue.cancel_task(task_id)
        else:
            logger.warning("Task cancellation not supported by current queue implementation")
            return False

# Global task service instance
task_service = TaskService()
