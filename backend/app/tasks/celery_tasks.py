"""
Celery tasks for document processing
Handles asynchronous AI-powered document analysis
"""

import asyncio
import logging
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from celery import current_task
import redis

from app.core.celery_app import celery_app
from app.services import PDFService
from app.services.ollama_ai_service import OllamaAIService
from app.models.schemas import ProcessingStatus
from app.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Redis client for task status storage
settings = get_settings()
redis_client = redis.from_url(settings.REDIS_URL)

class TaskProgressTracker:
    """Helper class to track and update task progress"""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.redis_key = f"task_status:{task_id}"
    
    def update_progress(self, progress: int, status: Optional[str] = None, result: Optional[Dict] = None, error: Optional[str] = None):
        """Update task progress in Redis"""
        task_data = {
            'id': self.task_id,
            'progress': str(min(progress, 100)),
        }
        
        if status:
            task_data['status'] = status
        if result:
            import json
            task_data['result'] = json.dumps(result)  # JSON serialize for Redis
        if error:
            task_data['error'] = error
            
        # Store in Redis with 1 hour expiry
        redis_client.hset(self.redis_key, mapping=task_data)
        redis_client.expire(self.redis_key, 3600)
        
        # Update Celery task meta
        if current_task:
            current_task.update_state(
                state=status or 'PROGRESS',
                meta={
                    'progress': progress,
                    'result': result,
                    'error': error
                }
            )
        
        logger.debug(f"Task {self.task_id} progress: {progress}%")

def get_task_status_from_redis(task_id: str) -> Optional[Dict[str, Any]]:
    """Get task status from Redis"""
    redis_key = f"task_status:{task_id}"
    task_data = redis_client.hgetall(redis_key)
    
    if not task_data:
        return None
    
    # Convert bytes to strings and handle data types
    result = {}
    for k, v in task_data.items():
        key = k.decode() if isinstance(k, bytes) else k
        value = v.decode() if isinstance(v, bytes) else v
        
        # Convert specific fields back to appropriate types
        if key == 'progress':
            result[key] = int(value) if value else 0
        elif key == 'result' and value:
            try:
                import json
                result[key] = json.loads(value)
            except:
                result[key] = value
        elif key in ['error', 'result'] and not value:
            result[key] = None
        else:
            result[key] = value
    
    return result

@celery_app.task(bind=True, name="process_document")
def process_document_task(self, file_path: str, filename: str, task_id: Optional[str] = None):
    """
    Process a document with AI analysis
    
    Args:
        file_path: Path to the uploaded file
        filename: Original filename
        task_id: Optional custom task ID
        
    Returns:
        Dict with processing results
    """
    # Ensure we have a valid task_id
    actual_task_id = task_id if task_id else self.request.id
    
    tracker = TaskProgressTracker(actual_task_id)
    loop = None
    
    # Store initial task info
    initial_data = {
        'id': actual_task_id,
        'filename': filename,
        'file_path': file_path,
        'status': ProcessingStatus.PENDING,
        'progress': '0',
        'result': '',
        'error': ''
    }
    redis_client.hset(f"task_status:{actual_task_id}", mapping=initial_data)
    
    try:
        # Update to processing status
        tracker.update_progress(5, ProcessingStatus.PROCESSING)
        
        # Initialize services
        pdf_service = PDFService()
        ai_service = OllamaAIService()
        
        tracker.update_progress(10)
        
        # Initialize AI service
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ollama_available = False
        
        try:
            ollama_available = loop.run_until_complete(ai_service.initialize_models())
            if ollama_available:
                logger.info("Ollama AI service initialized successfully")
            else:
                logger.warning("Ollama not available, continuing with basic processing")
            tracker.update_progress(20)
        except Exception as e:
            logger.warning(f"Ollama AI service initialization failed: {e}")
            tracker.update_progress(20)
        
        # Process file based on type
        file_path_obj = Path(file_path)
        file_extension = file_path_obj.suffix.lower()
        
        def progress_callback(progress: int):
            # Map processing progress to 20-95% range
            mapped_progress = 20 + int((progress / 100) * 75)
            tracker.update_progress(mapped_progress)
        
        if file_extension == '.pdf':
            result = loop.run_until_complete(
                pdf_service.process_pdf_with_ai(
                    file_path_obj,
                    actual_task_id,
                    ai_service if ollama_available else None,
                    progress_callback=progress_callback
                )
            )
        elif file_extension in ['.png', '.jpg', '.jpeg']:
            result = loop.run_until_complete(
                pdf_service.process_image_with_ai(
                    file_path_obj,
                    actual_task_id,
                    ai_service if ollama_available else None,
                    progress_callback=progress_callback
                )
            )
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Check for errors in result
        if 'error' in result:
            tracker.update_progress(100, ProcessingStatus.ERROR, error=result['error'])
            return {'error': result['error']}
        else:
            tracker.update_progress(100, ProcessingStatus.COMPLETED, result=result)
            logger.info(f"Task {actual_task_id} completed successfully")
            return result
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Task {actual_task_id} failed: {error_msg}")
        tracker.update_progress(100, ProcessingStatus.ERROR, error=error_msg)
        raise self.retry(exc=e, countdown=60, max_retries=3)
    
    finally:
        if loop is not None:
            loop.close()

@celery_app.task(name="cleanup_old_tasks")
def cleanup_old_tasks():
    """Clean up old task results from Redis"""
    try:
        # Find all task keys older than 24 hours
        keys = redis_client.keys("task_status:*")
        cleaned_count = 0
        
        for key in keys:
            ttl = redis_client.ttl(key)
            # If TTL is less than 1 hour remaining (out of 24 hour total), clean it up
            if ttl < 3600:
                redis_client.delete(key)
                cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} old task records")
        return {"cleaned_count": cleaned_count}
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        raise

@celery_app.task(name="health_check")
def health_check():
    """Health check task for monitoring"""
    return {"status": "healthy", "timestamp": str(asyncio.get_event_loop().time())}
