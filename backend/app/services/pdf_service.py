import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import pypdf
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import numpy as np

# Use OpenCV compatibility layer
try:
    from app.utils.cv2_compat import cv2
except ImportError:
    cv2 = None

from app.models.schemas import DocumentAnalysisResult
from app.services.advanced_ocr_service import AdvancedOCRService

logger = logging.getLogger(__name__)

class PDFService:
    """Service for PDF processing with AI enhancement"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.png', '.jpg', '.jpeg']
        # Initialize advanced OCR service
        self.advanced_ocr = AdvancedOCRService()
        
    async def process_pdf_with_ai(
        self, 
        file_path: Path, 
        job_id: str, 
        ai_service=None,
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Process PDF with comprehensive AI analysis and real-time progress
        """
        start_time = time.time()
        
        def update_progress(progress: int):
            if progress_callback:
                progress_callback(progress)
        
        try:
            logger.info(f"Processing PDF: {file_path}")
            update_progress(20)
            
            # Extract text and metadata from PDF (20-40%)
            pdf_info = await self._extract_pdf_info(file_path)
            update_progress(40)
            
            # Perform OCR on PDF pages (40-70%)
            ocr_results = await self._perform_pdf_ocr(file_path, progress_callback=lambda p: update_progress(40 + int(p * 0.3)))
            update_progress(70)
            
            # Combine text from PDF extraction and OCR
            combined_text = self._combine_text_sources(pdf_info['text'], ocr_results['text'])
            update_progress(75)
            
            # Prepare base result
            result = {
                'job_id': job_id,
                'filename': file_path.name,
                'file_type': 'pdf',
                'processing_time': 0,  # Will be updated
                'extracted_text': combined_text,
                'text_confidence': ocr_results.get('confidence', 0.95),
                'page_count': pdf_info.get('page_count', 0),
                'file_size': file_path.stat().st_size,
                'processing_metadata': {
                    'pdf_extraction_success': pdf_info.get('success', False),
                    'ocr_method': ocr_results.get('method', 'tesseract'),
                    'pages_processed': len(ocr_results.get('page_results', []))
                }
            }
            
            # Apply AI enhancement if service is available (75-90%)
            if ai_service and combined_text.strip():
                logger.info("Applying AI enhancement...")
                update_progress(80)
                ai_results = await ai_service.analyze_document(combined_text)
                result.update(ai_results)
                update_progress(90)
            else:
                logger.warning("AI service not available or no text extracted")
                # Calculate basic text statistics even without AI service
                words = combined_text.split() if combined_text else []
                sentences = [s for s in combined_text.split('.') if s.strip()] if combined_text else []
                
                result.update({
                    'document_classification': {'type': 'unknown', 'confidence': 0.0},
                    'entities': [],
                    'sentiment_analysis': {'overall_sentiment': 'neutral', 'confidence': 0.5},
                    'key_information': {},
                    'summary': 'No summary available - insufficient text or AI service unavailable',
                    'text_statistics': {
                        'character_count': len(combined_text) if combined_text else 0,
                        'word_count': len(words),
                        'sentence_count': len(sentences),
                        'average_words_per_sentence': len(words) / len(sentences) if sentences else 0,
                        'average_characters_per_word': len(combined_text) / len(words) if words and combined_text else 0
                    }
                })
                update_progress(90)
            
            # Update processing time (90-95%)
            result['processing_time'] = time.time() - start_time
            update_progress(95)
            
            logger.info(f"PDF processing completed in {result['processing_time']:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"PDF processing error: {str(e)}")
            return {
                'job_id': job_id,
                'filename': file_path.name,
                'file_type': 'pdf',
                'processing_time': time.time() - start_time,
                'error': str(e),
                'status': 'error'
            }
    
    async def process_image_with_ai(
        self, 
        file_path: Path, 
        job_id: str, 
        ai_service=None,
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Process image file with AI enhancement and real-time progress
        """
        start_time = time.time()
        
        def update_progress(progress: int):
            if progress_callback:
                progress_callback(progress)
        
        try:
            logger.info(f"Processing image: {file_path}")
            update_progress(20)
            
            # Perform OCR on image (20-70%)
            ocr_results = await self._perform_image_ocr(file_path)
            update_progress(70)
            
            result = {
                'job_id': job_id,
                'filename': file_path.name,
                'file_type': 'image',
                'processing_time': 0,
                'extracted_text': ocr_results['text'],
                'text_confidence': ocr_results.get('confidence', 0.8),
                'file_size': file_path.stat().st_size,
                'processing_metadata': {
                    'ocr_method': ocr_results.get('method', 'tesseract'),
                    'image_dimensions': ocr_results.get('dimensions')
                }
            }
            update_progress(75)
            
            # Apply AI enhancement (75-90%)
            if ai_service and ocr_results['text'].strip():
                update_progress(80)
                ai_results = await ai_service.analyze_document(ocr_results['text'])
                result.update(ai_results)
                update_progress(90)
            else:
                result.update({
                    'document_classification': {'type': 'unknown', 'confidence': 0.0},
                    'entities': [],
                    'sentiment_analysis': {'overall_sentiment': 'neutral', 'confidence': 0.5},
                    'key_information': {},
                    'summary': 'No summary available'
                })
                update_progress(90)
            
            result['processing_time'] = time.time() - start_time
            update_progress(95)
            return result
            
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            return {
                'job_id': job_id,
                'filename': file_path.name,
                'file_type': 'image',
                'processing_time': time.time() - start_time,
                'error': str(e),
                'status': 'error'
            }
    
    async def _extract_pdf_info(self, file_path: Path) -> Dict[str, Any]:
        """Extract text and metadata directly from PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                text_content = ""
                page_count = len(pdf_reader.pages)
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text_content += f"\\n--- Page {page_num + 1} ---\\n{page_text}\\n"
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                
                return {
                    'text': text_content,
                    'page_count': page_count,
                    'success': True
                }
                
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            return {
                'text': "",
                'page_count': 0,
                'success': False,
                'error': str(e)
            }
    
    async def _perform_pdf_ocr(self, file_path: Path, progress_callback=None) -> Dict[str, Any]:
        """Perform OCR on PDF using pdf2image + tesseract with progress tracking"""
        try:
            # Convert PDF to images
            images = convert_from_path(file_path, dpi=300, fmt='jpeg')
            
            all_text = ""
            confidences = []
            page_results = []
            total_pages = len(images)
            
            for i, image in enumerate(images):
                try:
                    # Update progress for each page
                    if progress_callback:
                        page_progress = 20 + (i / total_pages) * 20  # OCR takes 20-40% of progress
                        progress_callback(int(page_progress))
                    
                    # Use advanced OCR with multiple engines
                    ocr_result = self.advanced_ocr.extract_text_multi_engine(image)
                    
                    page_text = ocr_result.get('text', '')
                    page_confidence = ocr_result.get('confidence', 0.0)
                    
                    all_text += f"\\n--- OCR Page {i + 1} (Method: {ocr_result.get('method', 'unknown')}) ---\\n{page_text}\\n"
                    confidences.append(page_confidence)
                    
                    page_results.append({
                        'page_number': i + 1,
                        'text': page_text,
                        'confidence': page_confidence,
                        'method': ocr_result.get('method', 'unknown'),
                        'words': ocr_result.get('words', [])
                    })
                    
                except Exception as e:
                    logger.warning(f"OCR failed for page {i + 1}: {e}")
                    page_results.append({
                        'page_number': i + 1,
                        'text': "",
                        'confidence': 0.0,
                        'error': str(e)
                    })
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                'text': all_text,
                'confidence': avg_confidence,
                'method': 'tesseract_pdf2image',
                'page_results': page_results
            }
            
        except Exception as e:
            logger.error(f"PDF OCR error: {str(e)}")
            return {
                'text': "",
                'confidence': 0.0,
                'method': 'failed',
                'error': str(e)
            }
    
    async def _perform_image_ocr(self, file_path: Path) -> Dict[str, Any]:
        """Perform OCR on image file"""
        try:
            # Load and preprocess image
            image = Image.open(file_path)
            processed_image = self._preprocess_image_for_ocr(image)
            
            # Get image dimensions
            dimensions = {
                'width': image.width,
                'height': image.height,
                'mode': image.mode
            }
            
            # Use advanced OCR instead of basic pytesseract
            ocr_result = self.advanced_ocr.extract_text_multi_engine(processed_image)
            
            text = ocr_result.get('text', '')
            confidence = ocr_result.get('confidence', 0.0)
            
            return {
                'text': text,
                'confidence': confidence,
                'method': ocr_result.get('method', 'advanced_ocr'),
                'words': ocr_result.get('words', []),
                'dimensions': dimensions
            }
            
        except Exception as e:
            logger.error(f"Image OCR error: {str(e)}")
            return {
                'text': "",
                'confidence': 0.0,
                'method': 'failed',
                'error': str(e)
            }
    
    def _preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Preprocess image to improve OCR accuracy"""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply denoising
            img_array = cv2.fastNlMeansDenoising(img_array)
            
            # Apply adaptive thresholding
            img_array = cv2.adaptiveThreshold(
                img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Convert back to PIL Image
            return Image.fromarray(img_array)
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image  # Return original if preprocessing fails
    
    def _calculate_ocr_confidence(self, ocr_data: Dict) -> float:
        """Calculate average confidence from OCR data"""
        try:
            confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
            return sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
        except Exception:
            return 0.0
    
    def _combine_text_sources(self, pdf_text: str, ocr_text: str) -> str:
        """Intelligently combine text from PDF extraction and OCR"""
        # If PDF text is substantial, prefer it (it's usually more accurate)
        if pdf_text.strip() and len(pdf_text.strip()) > 100:
            # Add OCR as supplementary if it has additional content
            if ocr_text.strip() and len(ocr_text.strip()) > 50:
                return f"{pdf_text}\\n\\n--- OCR Supplementary ---\\n{ocr_text}"
            return pdf_text
        
        # Otherwise, use OCR text
        return ocr_text if ocr_text.strip() else "No text could be extracted from the document."
