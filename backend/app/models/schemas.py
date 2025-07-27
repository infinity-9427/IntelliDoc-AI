from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class DocumentProcessingRequest(BaseModel):
    """Request model for document processing"""
    filename: str
    file_type: str
    ai_features: Optional[List[str]] = ["ocr", "classification", "entities", "sentiment"]
    output_formats: Optional[List[str]] = ["json"]

class DocumentProcessingResponse(BaseModel):
    """Response model for document processing"""
    job_id: str
    status: ProcessingStatus
    message: str
    filename: Optional[str] = None
    processed_files: Optional[List[str]] = None
    results: Optional[Dict[str, Any]] = None

class DocumentAnalysisResult(BaseModel):
    """Model for AI analysis results"""
    job_id: str
    filename: str
    file_type: str
    processing_time: float
    
    # OCR Results
    extracted_text: str
    text_confidence: float
    language_detected: Optional[str] = None
    
    # AI Analysis
    document_classification: Optional[Dict[str, Any]] = None
    entities: Optional[List[Dict[str, Any]]] = None
    sentiment_analysis: Optional[Dict[str, Any]] = None
    key_information: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    
    # Technical Info
    page_count: Optional[int] = None
    file_size: int
    processing_metadata: Optional[Dict[str, Any]] = None

class EntityResult(BaseModel):
    """Model for entity extraction results"""
    text: str
    label: str
    confidence: float
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None

class SentimentResult(BaseModel):
    """Model for sentiment analysis results"""
    overall_sentiment: str
    confidence: float
    emotions: Optional[Dict[str, float]] = None
    recommendation: Optional[str] = None
