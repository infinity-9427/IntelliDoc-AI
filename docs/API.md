# API Documentation

## Overview

IntelliDoc AI provides a comprehensive RESTful API for document processing and intelligence. The API follows OpenAPI 3.0 standards and provides interactive documentation.

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com/api
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Rate Limiting

- Free tier: 100 requests per minute
- Authenticated users: 1000 requests per minute
- Batch processing: 10 concurrent jobs

## Endpoints

### Upload & Processing

#### Upload Document
```http
POST /api/v1/upload
Content-Type: multipart/form-data

{
  "file": <binary-file>,
  "language": "auto", // optional
  "features": ["ocr", "classification", "entities"] // optional
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Document uploaded successfully",
  "estimated_processing_time": 30
}
```

#### Get Job Status
```http
GET /api/v1/jobs/{job_id}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45.5,
  "total_pages": 10,
  "processed_pages": 4,
  "confidence_score": 87.3,
  "created_at": "2025-07-26T10:30:00Z",
  "started_at": "2025-07-26T10:30:15Z",
  "estimated_completion": "2025-07-26T10:32:00Z"
}
```

#### Download Results
```http
GET /api/v1/jobs/{job_id}/download?format=docx
```

Supported formats:
- `docx` - Microsoft Word document
- `txt` - Plain text
- `json` - Structured JSON with metadata
- `pdf` - Searchable PDF

### Document Intelligence

#### Get Document Analysis
```http
GET /api/v1/jobs/{job_id}/analysis
```

**Response:**
```json
{
  "document_type": "invoice",
  "confidence": 94.2,
  "language": {
    "detected": "en",
    "confidence": 98.5
  },
  "entities": [
    {
      "type": "PERSON",
      "text": "John Doe",
      "confidence": 92.1,
      "position": [150, 200, 220, 215]
    }
  ],
  "key_information": {
    "dates": ["2025-07-26"],
    "amounts": ["$1,234.56"],
    "emails": ["john@example.com"]
  },
  "sentiment": {
    "overall": "neutral",
    "confidence": 76.8
  },
  "summary": "Invoice for professional services...",
  "quality_score": 88.5
}
```

### Search & Discovery

#### Semantic Search
```http
POST /api/v1/search
Content-Type: application/json

{
  "query": "invoices from Q4 2024 over $1000",
  "filters": {
    "document_type": "invoice",
    "date_range": {
      "start": "2024-10-01",
      "end": "2024-12-31"
    }
  },
  "limit": 20
}
```

#### Similar Documents
```http
GET /api/v1/jobs/{job_id}/similar?limit=10
```

### Batch Processing

#### Create Batch Job
```http
POST /api/v1/batch
Content-Type: multipart/form-data

{
  "files": [<file1>, <file2>, ...],
  "processing_options": {
    "language": "auto",
    "features": ["ocr", "classification"],
    "output_format": "docx"
  }
}
```

#### Get Batch Status
```http
GET /api/v1/batch/{batch_id}
```

### Analytics

#### Get Processing Statistics
```http
GET /api/v1/analytics/stats?period=30d
```

#### Get Quality Metrics
```http
GET /api/v1/analytics/quality?job_id={job_id}
```

### Webhooks

#### Register Webhook
```http
POST /api/v1/webhooks
Content-Type: application/json

{
  "url": "https://your-app.com/webhook",
  "events": ["job.completed", "job.failed"],
  "secret": "your-webhook-secret"
}
```

#### Webhook Payload
```json
{
  "event": "job.completed",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-07-26T10:32:00Z",
  "data": {
    "status": "completed",
    "confidence": 89.5,
    "total_pages": 10,
    "processing_time": 45.2
  }
}
```

## Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `413` - File Too Large
- `429` - Rate Limited
- `500` - Internal Server Error

Error responses include detailed information:

```json
{
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "File format not supported",
    "details": "Supported formats: PDF, PNG, JPG, TIFF",
    "timestamp": "2025-07-26T10:30:00Z"
  }
}
```

## SDK Examples

### Python
```python
import requests

# Upload document
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/upload',
        files={'file': f},
        headers={'Authorization': 'Bearer your-token'}
    )
    job_id = response.json()['job_id']

# Check status
status = requests.get(
    f'http://localhost:8000/api/v1/jobs/{job_id}',
    headers={'Authorization': 'Bearer your-token'}
).json()

# Download result
if status['status'] == 'completed':
    result = requests.get(
        f'http://localhost:8000/api/v1/jobs/{job_id}/download?format=docx',
        headers={'Authorization': 'Bearer your-token'}
    )
    with open('result.docx', 'wb') as f:
        f.write(result.content)
```

### JavaScript
```javascript
// Upload document
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('/api/v1/upload', {
  method: 'POST',
  body: formData,
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const { job_id } = await response.json();

// Check status with polling
const checkStatus = async () => {
  const statusResponse = await fetch(`/api/v1/jobs/${job_id}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const status = await statusResponse.json();
  
  if (status.status === 'completed') {
    // Download result
    window.open(`/api/v1/jobs/${job_id}/download?format=docx`);
  } else if (status.status === 'processing') {
    setTimeout(checkStatus, 2000); // Check again in 2 seconds
  }
};

checkStatus();
```

### curl
```bash
# Upload document
curl -X POST \
  -H "Authorization: Bearer your-token" \
  -F "file=@document.pdf" \
  http://localhost:8000/api/v1/upload

# Check status
curl -H "Authorization: Bearer your-token" \
  http://localhost:8000/api/v1/jobs/{job_id}

# Download result
curl -H "Authorization: Bearer your-token" \
  -o result.docx \
  "http://localhost:8000/api/v1/jobs/{job_id}/download?format=docx"
```

## Interactive Documentation

Visit the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Rate Limits and Quotas

| Feature | Free Tier | Authenticated | Premium |
|---------|-----------|---------------|---------|
| API Requests/min | 100 | 1,000 | 10,000 |
| File Size | 10MB | 50MB | 100MB |
| Concurrent Jobs | 2 | 10 | 50 |
| Storage | 1GB | 10GB | 100GB |
| Webhook Endpoints | 1 | 5 | 20 |

## Changelog

### v1.0.0 (2025-07-26)
- Initial API release
- Document upload and OCR processing
- Multi-language support
- Document classification and entity extraction
- Webhooks support
- Batch processing capabilities
