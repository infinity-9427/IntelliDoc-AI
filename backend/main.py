from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pathlib import Path
import shutil
import uuid
import logging
import asyncio
import io
from typing import Dict, Any, Optional

# Production imports - No fallbacks allowed
from app.models.schemas import DocumentProcessingResponse, ProcessingStatus
from app.tasks.queue import task_queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="IntelliDoc AI - Smart Document Intelligence Platform",
    description="AI-powered document processing and intelligence platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "IntelliDoc AI - Smart Document Intelligence Platform", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "intellidoc-ai-backend"}

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload document for AI-powered processing
    """
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file type. Please upload PDF, PNG, JPG, or JPEG files."
            )
        
        # Create unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        upload_path = UPLOAD_DIR / unique_filename
        
        # Save uploaded file
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded: {upload_path}")
        
        # Submit task to AI processing queue - Production mode only
        job_id = await task_queue.submit_task(upload_path, file.filename)
        return {
            "job_id": job_id,
            "status": ProcessingStatus.PENDING,
            "message": "Document uploaded successfully. AI processing started.",
            "filename": file.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/status/{job_id}")
async def get_processing_status(job_id: str):
    """Get AI processing status for a job"""
    try:
        task_status = task_queue.get_task_status(job_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job_id,
            "status": task_status['status'],
            "progress": task_status['progress'],
            "filename": task_status['filename'],
            "message": f"Processing {task_status['progress']}% complete",
            "result": task_status.get('result'),
            "error": task_status.get('error')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@app.get("/api/results/{job_id}")
async def get_document_results(job_id: str):
    """Get the detailed AI analysis results of a processed document"""
    try:
        task_status = task_queue.get_task_status(job_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if task_status['status'] != ProcessingStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Document processing not completed. Current status: {task_status['status']}"
            )
        
        return task_status.get('result', {})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Results retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Results retrieval failed: {str(e)}")

@app.get("/api/download/{job_id}")
async def download_processed_document(job_id: str, format: str = Query("docx", regex="^(docx|txt)$")):
    """
    Download the processed document in specified format
    """
    try:
        task_status = task_queue.get_task_status(job_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if task_status['status'] != ProcessingStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Document processing not completed. Current status: {task_status['status']}"
            )
        
        result = task_status.get('result')
        if not result:
            raise HTTPException(status_code=404, detail="No processing results found")
        
        # Generate document based on format
        if format == "docx":
            try:
                from app.services.document_service import DocumentGenerator
                doc_buffer = DocumentGenerator.create_docx_from_results(result)
                
                return StreamingResponse(
                    io.BytesIO(doc_buffer.read()),
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": f"attachment; filename={result.get('filename', 'document')}_processed.docx"}
                )
            except ImportError:
                # Fallback if python-docx is not available
                from app.services.document_service import DocumentGenerator
                text_content = DocumentGenerator.create_text_from_results(result)
                return StreamingResponse(
                    io.BytesIO(text_content.encode('utf-8')),
                    media_type="text/plain",
                    headers={"Content-Disposition": f"attachment; filename={result.get('filename', 'document')}_processed.txt"}
                )
        
        elif format == "txt":
            from app.services.document_service import DocumentGenerator
            text_content = DocumentGenerator.create_text_from_results(result)
            
            return StreamingResponse(
                io.BytesIO(text_content.encode('utf-8')),
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename={result.get('filename', 'document')}_processed.txt"}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
