"""
Celery-based task queue service for document processing
Integrates with Redis backend for scalable task management
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
from celery.result import AsyncResult
from app.core.celery_app import celery_app
from app.tasks.celery_tasks import process_document_task, get_task_status_from_redis
from app.models.schemas import ProcessingStatus

logger = logging.getLogger(__name__)

class CeleryTaskQueue:
    """Celery-based task queue for document processing"""
    
    def __init__(self):
        self.celery_app = celery_app
    
    async def submit_task(self, file_path: Path, filename: str) -> str:
        """Submit a new document processing task to Celery"""
        try:
            # Submit task to Celery
            result = process_document_task.delay(
                file_path=str(file_path),
                filename=filename
            )
            
            task_id = result.id
            logger.info(f"Celery task {task_id} submitted for file: {filename}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to submit task for {filename}: {e}")
            raise
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task from Redis and Celery"""
        try:
            # First try to get from Redis (our custom status)
            redis_status = get_task_status_from_redis(task_id)
            if redis_status:
                return redis_status
            
            # Fallback to Celery result backend
            result = AsyncResult(task_id, app=self.celery_app)
            
            if result.state == 'PENDING':
                return {
                    'id': task_id,
                    'status': ProcessingStatus.PENDING,
                    'progress': 0,
                    'result': None,
                    'error': None
                }
            elif result.state == 'PROGRESS':
                meta = result.info or {}
                return {
                    'id': task_id,
                    'status': ProcessingStatus.PROCESSING,
                    'progress': meta.get('progress', 0),
                    'result': meta.get('result'),
                    'error': meta.get('error')
                }
            elif result.state == 'SUCCESS':
                return {
                    'id': task_id,
                    'status': ProcessingStatus.COMPLETED,
                    'progress': 100,
                    'result': result.result,
                    'error': None
                }
            elif result.state == 'FAILURE':
                return {
                    'id': task_id,
                    'status': ProcessingStatus.ERROR,
                    'progress': 100,
                    'result': None,
                    'error': str(result.info)
                }
            else:
                return {
                    'id': task_id,
                    'status': result.state,
                    'progress': 0,
                    'result': None,
                    'error': None
                }
                
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {e}")
            return None
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all active tasks - limited implementation for Celery"""
        # Note: This is limited with Celery since we can't easily enumerate all tasks
        # In production, you'd want to maintain a separate registry or use Celery monitoring tools
        logger.warning("get_all_tasks() has limited functionality with Celery backend")
        return {}
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            result.revoke(terminate=True)
            logger.info(f"Task {task_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False

# Global Celery task queue instance
celery_task_queue = CeleryTaskQueue()
