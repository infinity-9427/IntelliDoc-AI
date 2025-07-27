# Multi-stage Dockerfile for cross-platform OCR support
FROM python:3.12.11-alpine3.22

# Install system dependencies for OCR
RUN apk update && apk add --no-cache \
    # Tesseract OCR with language packs
    tesseract-ocr \
    tesseract-ocr-data-eng \
    tesseract-ocr-data-fra \
    tesseract-ocr-data-deu \
    tesseract-ocr-data-spa \
    tesseract-ocr-data-ita \
    # Image processing libraries
    mesa-gl \
    glib \
    libsm \
    libxext \
    libxrender \
    libgomp \
    # PDF processing
    poppler-utils \
    # Build tools for Python packages
    build-base \
    pkgconfig \
    hdf5-dev \
    linux-headers \
    # OpenCV system dependencies (using system package instead of pip package)
    opencv \
    opencv-dev \
    py3-opencv \
    # Additional tools
    curl \
    wget \
    git

# Set Tesseract data path
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install uv
# Install essential dependencies first for Alpine compatibility
RUN pip install numpy>=1.24.0 Pillow>=10.0.0
RUN pip install setuptools wheel
# Install core dependencies without heavy packages
RUN pip install fastapi uvicorn python-multipart websockets sqlalchemy alembic psycopg2-binary redis celery minio
# Install document processing dependencies
RUN pip install pdf2image pypdf pytesseract python-docx reportlab openpyxl
# Install AI and ML lightweight dependencies  
RUN pip install ollama langdetect textblob
# Install monitoring and utility dependencies
RUN pip install elasticsearch prometheus-client structlog python-jose passlib pydantic pydantic-settings httpx aiofiles python-magic

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads storage/processed storage/temp

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
