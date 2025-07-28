"""
Configuration settings for IntelliDoc AI Backend
"""
import os
from typing import Optional, List

class Settings:
    """Application settings"""
    
    # Ollama Configuration
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    OLLAMA_EMBED_MODEL: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    OLLAMA_TIMEOUT: float = float(os.getenv("OLLAMA_TIMEOUT", "300.0"))
    
    # AI Service Configuration
    AI_SERVICE_TYPE: str = os.getenv("AI_SERVICE_TYPE", "ollama")  # "ollama" or "transformers"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://intellidoc_user:intellidoc_password@localhost:5432/intellidoc_db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    
    # MinIO Configuration
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "intellidoc")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "intellidoc123")
    
    # File Processing
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    PROCESSED_DIR: str = os.getenv("PROCESSED_DIR", "storage/processed")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "storage/temp")
    MODELS_DIR: str = os.getenv("MODELS_DIR", "storage/models")
    VECTORS_DIR: str = os.getenv("VECTORS_DIR", "storage/vectors")
    
    # OCR Settings
    OCR_LANGUAGES: List[str] = ["eng", "fra", "deu", "spa", "ita"]
    OCR_DPI: int = int(os.getenv("OCR_DPI", "300"))
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://frontend:3000"
    ]
    
    # AI Processing Settings
    ENABLE_TEXT_EXTRACTION: bool = os.getenv("ENABLE_TEXT_EXTRACTION", "true").lower() == "true"
    ENABLE_DOCUMENT_CLASSIFICATION: bool = os.getenv("ENABLE_DOCUMENT_CLASSIFICATION", "true").lower() == "true"
    ENABLE_ENTITY_EXTRACTION: bool = os.getenv("ENABLE_ENTITY_EXTRACTION", "true").lower() == "true"
    ENABLE_SENTIMENT_ANALYSIS: bool = os.getenv("ENABLE_SENTIMENT_ANALYSIS", "true").lower() == "true"
    ENABLE_SUMMARIZATION: bool = os.getenv("ENABLE_SUMMARIZATION", "true").lower() == "true"
    ENABLE_KEY_INFO_EXTRACTION: bool = os.getenv("ENABLE_KEY_INFO_EXTRACTION", "true").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings instance"""
    return settings
