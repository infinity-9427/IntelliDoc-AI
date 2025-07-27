# Contributing to IntelliDoc AI

Thank you for your interest in contributing to IntelliDoc AI! This document provides guidelines and information for contributors.

## 🤝 Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## 🚀 Quick Start for Contributors

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/your-username/local-pdf-converter.git
cd local-pdf-converter

# Add upstream remote
git remote add upstream https://github.com/original-repo/local-pdf-converter.git
```

### 2. Development Setup

```bash
# Copy environment file
cp .env.example .env

# Start development environment
docker-compose up -d

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### 3. Development Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ...

# Run tests
./scripts/test.sh

# Commit changes
git add .
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## 📝 How to Contribute

### Ways to Contribute

1. **Bug Reports** - Report issues and bugs
2. **Feature Requests** - Suggest new features
3. **Code Contributions** - Fix bugs or implement features
4. **Documentation** - Improve documentation
5. **Testing** - Write tests or test new features
6. **Translations** - Add support for new languages
7. **ML Models** - Contribute new AI models or improvements

### What We're Looking For

- 🐛 Bug fixes
- 🚀 Performance improvements
- 📚 Documentation improvements
- 🧪 Test coverage improvements
- 🌍 Multi-language support
- 🤖 New AI/ML capabilities
- 🔒 Security enhancements
- ♿ Accessibility improvements

## 🐛 Reporting Bugs

### Before Submitting a Bug Report

1. Check the [existing issues](https://github.com/repo/issues)
2. Update to the latest version
3. Try to reproduce in a clean environment

### Bug Report Template

```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Docker version: [e.g., 20.10.0]
- Browser: [e.g., Chrome 91.0]

**Additional Context**
- Error logs
- Screenshots
- Configuration files (redacted)
```

## 💡 Requesting Features

### Feature Request Template

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Problem Statement**
What problem does this solve?

**Proposed Solution**
How would you like this feature to work?

**Alternatives Considered**
Other solutions you've considered.

**Additional Context**
- Use cases
- Examples from other tools
- Mockups or diagrams
```

## 🔧 Development Guidelines

### Project Structure

```
local-pdf-converter/
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
├── ml-models/        # ML model downloads
├── monitoring/       # Prometheus/Grafana
├── scripts/          # Automation scripts
└── docs/            # Documentation
```

### Backend Development

#### Setting Up Backend Development

```bash
cd backend

# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Backend Code Style

```python
# Use type hints
from typing import List, Dict, Optional
from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    confidence: Optional[float] = None

# Use async/await for I/O operations
async def process_document(file_path: str) -> DocumentResponse:
    """Process a document and return results."""
    result = await ocr_service.process(file_path)
    return DocumentResponse(**result)

# Use logging
import logging
logger = logging.getLogger(__name__)

def some_function():
    logger.info("Processing started")
    try:
        # ... code ...
        logger.info("Processing completed")
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise
```

#### Adding New API Endpoints

```python
# backend/app/api/routes/new_feature.py
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user
from app.models.schemas import NewFeatureRequest, NewFeatureResponse

router = APIRouter()

@router.post("/new-feature", response_model=NewFeatureResponse)
async def create_new_feature(
    request: NewFeatureRequest,
    current_user = Depends(get_current_user)
):
    """Create a new feature."""
    try:
        result = await service.create_feature(request, current_user)
        return NewFeatureResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add new feature table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Frontend Development

#### Setting Up Frontend Development

```bash
cd frontend

# Install dependencies
pnpm install

# Run development server
pnpm dev
```

#### Frontend Code Style

```tsx
// Use TypeScript
interface DocumentProps {
  id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

// Use functional components with hooks
export const DocumentCard: React.FC<DocumentProps> = ({ id, filename, status }) => {
  const [loading, setLoading] = useState(false);
  
  const handleDownload = useCallback(async () => {
    setLoading(true);
    try {
      await downloadDocument(id);
    } catch (error) {
      console.error('Download failed:', error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  return (
    <div className="document-card">
      <h3>{filename}</h3>
      <p>Status: {status}</p>
      <button onClick={handleDownload} disabled={loading}>
        {loading ? 'Downloading...' : 'Download'}
      </button>
    </div>
  );
};
```

#### Adding New Components

```tsx
// components/ui/NewComponent.tsx
import { cn } from '@/lib/utils';

interface NewComponentProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'secondary';
}

export const NewComponent: React.FC<NewComponentProps> = ({
  children,
  className,
  variant = 'default'
}) => {
  return (
    <div
      className={cn(
        'base-styles',
        {
          'variant-default-styles': variant === 'default',
          'variant-secondary-styles': variant === 'secondary',
        },
        className
      )}
    >
      {children}
    </div>
  );
};
```

### Testing Guidelines

#### Backend Testing

```python
# tests/test_ocr_service.py
import pytest
from app.services.ocr_service import FreeOCRService

@pytest.fixture
def ocr_service():
    return FreeOCRService()

@pytest.fixture
def sample_image():
    # Return a sample image for testing
    pass

@pytest.mark.asyncio
async def test_extract_text_tesseract(ocr_service, sample_image):
    """Test Tesseract text extraction."""
    result = await ocr_service.extract_text_tesseract(sample_image)
    
    assert 'text' in result
    assert 'confidence' in result
    assert result['engine'] == 'tesseract'
    assert isinstance(result['confidence'], (int, float))

@pytest.mark.asyncio
async def test_extract_text_with_invalid_image(ocr_service):
    """Test OCR with invalid image."""
    result = await ocr_service.extract_text_tesseract(None)
    
    assert result['text'] == ''
    assert result['confidence'] == 0
    assert 'error' in result
```

#### Frontend Testing

```tsx
// __tests__/components/DocumentCard.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DocumentCard } from '@/components/DocumentCard';

jest.mock('@/lib/api', () => ({
  downloadDocument: jest.fn(),
}));

describe('DocumentCard', () => {
  const mockProps = {
    id: '123',
    filename: 'test.pdf',
    status: 'completed' as const,
  };

  it('renders document information', () => {
    render(<DocumentCard {...mockProps} />);
    
    expect(screen.getByText('test.pdf')).toBeInTheDocument();
    expect(screen.getByText('Status: completed')).toBeInTheDocument();
  });

  it('handles download click', async () => {
    const mockDownload = require('@/lib/api').downloadDocument;
    mockDownload.mockResolvedValue({});

    render(<DocumentCard {...mockProps} />);
    
    const downloadButton = screen.getByText('Download');
    fireEvent.click(downloadButton);

    expect(downloadButton).toBeDisabled();
    expect(screen.getByText('Downloading...')).toBeInTheDocument();

    await waitFor(() => {
      expect(mockDownload).toHaveBeenCalledWith('123');
    });
  });
});
```

#### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
pnpm test

# Run all tests
./scripts/test.sh
```

### ML Model Contributions

#### Adding New Models

```python
# backend/app/ai/models/new_model.py
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class NewAIModel:
    """New AI model for specific task."""
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the model from disk or download if needed."""
        try:
            # Model loading logic
            logger.info("New AI model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    async def predict(self, input_data: Any) -> Dict[str, Any]:
        """Make prediction using the model."""
        try:
            if not self.model:
                raise ValueError("Model not loaded")
            
            # Prediction logic
            result = self.model.predict(input_data)
            
            return {
                'prediction': result,
                'confidence': 0.95,
                'model_version': '1.0.0'
            }
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return {
                'prediction': None,
                'confidence': 0.0,
                'error': str(e)
            }
```

#### Model Download Script

```bash
#!/bin/bash
# ml-models/download-new-model.sh

MODEL_DIR="ml-models/new-model"
MODEL_URL="https://huggingface.co/model-repo/model-name"

echo "Downloading new model..."

mkdir -p $MODEL_DIR

# Download model files
wget -O "$MODEL_DIR/model.bin" "$MODEL_URL/resolve/main/model.bin"
wget -O "$MODEL_DIR/config.json" "$MODEL_URL/resolve/main/config.json"

echo "Model downloaded successfully to $MODEL_DIR"
```

## 📊 Performance Guidelines

### Backend Performance

- Use async/await for I/O operations
- Implement proper caching strategies
- Use database indexes appropriately
- Implement pagination for large datasets
- Use connection pooling

```python
# Good: Async I/O
async def process_documents(file_paths: List[str]) -> List[Dict]:
    tasks = [process_single_document(path) for path in file_paths]
    results = await asyncio.gather(*tasks)
    return results

# Good: Caching
@cache(expire=3600)  # Cache for 1 hour
async def get_document_stats(document_id: str) -> Dict:
    return await database.fetch_stats(document_id)
```

### Frontend Performance

- Use React.memo for expensive components
- Implement virtual scrolling for large lists
- Lazy load components and routes
- Optimize images and assets

```tsx
// Good: Memoized component
export const ExpensiveComponent = React.memo<Props>(({ data }) => {
  const processedData = useMemo(() => {
    return expensiveProcessing(data);
  }, [data]);

  return <div>{processedData}</div>;
});

// Good: Lazy loading
const DocumentViewer = lazy(() => import('@/components/DocumentViewer'));
```

## 🔒 Security Guidelines

### Input Validation

```python
# Always validate and sanitize inputs
from pydantic import BaseModel, validator

class UploadRequest(BaseModel):
    filename: str
    file_size: int
    
    @validator('filename')
    def validate_filename(cls, v):
        if not v or len(v) > 255:
            raise ValueError('Invalid filename')
        # Check for malicious patterns
        if any(char in v for char in ['..', '/', '\\']):
            raise ValueError('Invalid characters in filename')
        return v
    
    @validator('file_size')
    def validate_file_size(cls, v):
        if v <= 0 or v > 50 * 1024 * 1024:  # 50MB limit
            raise ValueError('Invalid file size')
        return v
```

### Secure File Handling

```python
import os
import uuid
from pathlib import Path

def secure_filename(filename: str) -> str:
    """Generate a secure filename."""
    # Remove path components
    filename = os.path.basename(filename)
    # Generate unique name
    name, ext = os.path.splitext(filename)
    secure_name = f"{uuid.uuid4()}{ext}"
    return secure_name

def validate_file_type(file_path: str, allowed_types: List[str]) -> bool:
    """Validate file type using magic numbers."""
    import magic
    file_type = magic.from_file(file_path, mime=True)
    return file_type in allowed_types
```

## 📚 Documentation Guidelines

### Code Documentation

```python
def process_document(
    file_path: str,
    language: str = 'auto',
    features: List[str] = None
) -> Dict[str, Any]:
    """
    Process a document using OCR and AI analysis.
    
    Args:
        file_path: Path to the document file
        language: Language code for OCR (default: auto-detect)
        features: List of features to extract (default: all)
    
    Returns:
        Dictionary containing:
            - text: Extracted text
            - confidence: OCR confidence score
            - entities: Extracted entities
            - analysis: Document analysis results
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is not supported
        
    Example:
        >>> result = process_document('document.pdf', language='en')
        >>> print(result['text'])
        'Document content...'
    """
    # Implementation...
```

### API Documentation

Use OpenAPI/Swagger annotations:

```python
@router.post(
    "/process",
    response_model=ProcessResponse,
    summary="Process Document",
    description="Upload and process a document with OCR and AI analysis",
    responses={
        200: {"description": "Processing started successfully"},
        400: {"description": "Invalid file or parameters"},
        413: {"description": "File too large"},
    }
)
async def process_document(
    file: UploadFile = File(..., description="Document file to process"),
    language: str = Query("auto", description="Language for OCR processing"),
    features: List[str] = Query(None, description="Features to extract")
):
    """Process uploaded document."""
    # Implementation...
```

## 🚀 Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Pre-release**
   - [ ] Update version numbers
   - [ ] Update CHANGELOG.md
   - [ ] Run full test suite
   - [ ] Update documentation
   - [ ] Security scan

2. **Release**
   - [ ] Create release branch
   - [ ] Tag release
   - [ ] Build and push Docker images
   - [ ] Deploy to staging
   - [ ] Test staging deployment
   - [ ] Deploy to production

3. **Post-release**
   - [ ] Monitor error rates
   - [ ] Update documentation site
   - [ ] Announce release
   - [ ] Close related issues

### Changelog Format

```markdown
# Changelog

## [1.2.0] - 2025-07-26

### Added
- New document classification feature
- Multi-language support for 50+ languages
- Batch processing API

### Changed
- Improved OCR accuracy by 15%
- Updated UI design
- Enhanced error handling

### Fixed
- Fixed memory leak in PDF processing
- Resolved authentication issues
- Fixed broken download links

### Security
- Updated dependencies with security patches
- Improved input validation
```

## 🎉 Recognition

### Contributors

We maintain a [CONTRIBUTORS.md](CONTRIBUTORS.md) file to recognize all contributors.

### Hall of Fame

- 🏆 **Top Contributors**: Regular high-impact contributions
- 🐛 **Bug Hunters**: Finding and reporting critical bugs
- 📚 **Documentation Heroes**: Improving documentation
- 🌟 **Feature Champions**: Implementing major features
- 🔒 **Security Guardians**: Security improvements

## 📞 Getting Help

### Community Channels

- **GitHub Discussions**: General questions and discussions
- **GitHub Issues**: Bug reports and feature requests
- **Discord**: Real-time chat with the community
- **Stack Overflow**: Tag questions with `intellidoc-ai`

### Maintainer Contact

For security issues or urgent matters, contact the maintainers directly:
- Email: security@intellidoc-ai.com
- Encrypted: Use our PGP key for sensitive reports

## 📄 License

By contributing to IntelliDoc AI, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Thank you for contributing to IntelliDoc AI! Your contributions help make document intelligence accessible to everyone. 🚀
