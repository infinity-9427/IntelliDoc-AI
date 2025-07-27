import asyncio
import logging
import uuid
from typing import Dict, Any, Optional
from pathlib import Path
from app.services import PDFService
from app.services.ollama_ai_service import OllamaAIService
from app.models.schemas import ProcessingStatus

logger = logging.getLogger(__name__)

class TaskQueue:
    """Simple in-memory task queue for document processing"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.pdf_service = PDFService()
        self.ai_service = OllamaAIService()
        self._ai_initialized = False
    
    async def submit_task(self, file_path: Path, filename: str) -> str:
        """Submit a new document processing task"""
        task_id = str(uuid.uuid4())
        
        self.tasks[task_id] = {
            'id': task_id,
            'filename': filename,
            'file_path': file_path,
            'status': ProcessingStatus.PENDING,
            'progress': 0,
            'result': None,
            'error': None,
            'created_at': asyncio.get_event_loop().time()
        }
        
        # Start processing in background
        asyncio.create_task(self._process_document(task_id))
        
        logger.info(f"Task {task_id} submitted for file: {filename}")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all tasks"""
        return self.tasks
    
    async def _process_document(self, task_id: str):
        """Process a document in the background with real-time progress"""
        task = self.tasks.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return
            
        def update_progress(progress: int):
            """Helper to update task progress"""
            if task_id in self.tasks:
                self.tasks[task_id]['progress'] = min(progress, 100)
                logger.debug(f"Task {task_id} progress: {progress}%")
            
        try:
            file_path = Path(task['file_path'])
            
            # Update status to processing
            task['status'] = ProcessingStatus.PROCESSING
            update_progress(5)
            
            # Initialize AI service if not done yet (5-15%)
            if not self._ai_initialized:
                try:
                    update_progress(8)
                    ollama_available = await self.ai_service.initialize_models()
                    if ollama_available:
                        self._ai_initialized = True
                        logger.info("Ollama AI service initialized successfully")
                    else:
                        logger.warning("Ollama not available, continuing with basic processing")
                    update_progress(15)
                except Exception as e:
                    logger.warning(f"Ollama AI service initialization failed: {e}")
                    update_progress(15)
            else:
                update_progress(15)
            
            # Determine file type and process accordingly (15-95%)
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.pdf':
                result = await self.pdf_service.process_pdf_with_ai(
                    file_path, 
                    task_id, 
                    self.ai_service if self._ai_initialized else None,
                    progress_callback=update_progress
                )
            elif file_extension in ['.png', '.jpg', '.jpeg']:
                result = await self.pdf_service.process_image_with_ai(
                    file_path, 
                    task_id, 
                    self.ai_service if self._ai_initialized else None,
                    progress_callback=update_progress
                )
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            update_progress(95)
            
            # Update task with results (95-100%)
            if 'error' in result:
                task['status'] = ProcessingStatus.ERROR
                task['error'] = result['error']
            else:
                task['status'] = ProcessingStatus.COMPLETED
                task['result'] = result
            
            update_progress(100)
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}")
            task['status'] = ProcessingStatus.ERROR
            task['error'] = str(e)
            update_progress(100)

# Global task queue instance
task_queue = TaskQueue()
