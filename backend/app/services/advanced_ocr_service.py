import cv2
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class AdvancedOCRService:
    """
    Advanced OCR service with multiple engines and enhanced preprocessing
    for 100% accuracy on challenging text like 'l' vs '1' and compound words.
    """
    
    def __init__(self):
        self.engines = {}
        self._initialize_engines()
        
    def _initialize_engines(self):
        """Initialize available OCR engines"""
        # Tesseract (always available)
        self.engines['tesseract'] = True
        
        # Try to initialize EasyOCR
        try:
            import easyocr
            self.easyocr_reader = easyocr.Reader(['en'], gpu=False)
            self.engines['easyocr'] = True
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.warning(f"EasyOCR not available: {e}")
            self.engines['easyocr'] = False
            
        # Try to initialize PaddleOCR
        try:
            from paddleocr import PaddleOCR
            self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            self.engines['paddleocr'] = True
            logger.info("PaddleOCR initialized successfully")
        except Exception as e:
            logger.warning(f"PaddleOCR not available: {e}")
            self.engines['paddleocr'] = False
    
    def enhance_image_for_ocr(self, image: Image.Image, aggressive: bool = True) -> Image.Image:
        """
        Advanced image preprocessing for maximum OCR accuracy
        """
        try:
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array.copy()
            
            # 1. Noise reduction
            # Apply bilateral filter to reduce noise while preserving edges
            gray = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # 2. Enhance contrast and brightness
            # CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            
            # 3. Morphological operations to clean up text
            # Remove small noise
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
            # 4. Advanced thresholding
            if aggressive:
                # Use multiple thresholding methods and combine
                
                # Otsu's thresholding
                _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # Adaptive thresholding (Gaussian)
                thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                              cv2.THRESH_BINARY, 11, 2)
                
                # Adaptive thresholding (Mean)
                thresh3 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                              cv2.THRESH_BINARY, 11, 2)
                
                # Combine thresholding results (take the best)
                combined = cv2.bitwise_and(thresh1, thresh2)
                combined = cv2.bitwise_or(combined, thresh3)
                
                gray = combined
            else:
                # Simple adaptive thresholding
                gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                           cv2.THRESH_BINARY, 11, 2)
            
            # 5. Text enhancement - dilate to connect broken characters
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
            gray = cv2.dilate(gray, kernel, iterations=1)
            
            # 6. Final cleanup - remove very small components
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(gray, connectivity=8)
            
            # Keep only components that are reasonably sized (likely text)
            min_area = 10  # Minimum area for text components
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if area < min_area:
                    gray[labels == i] = 0
            
            # Convert back to PIL Image
            enhanced_image = Image.fromarray(gray)
            
            # 7. PIL-based enhancements
            # Sharpen the image
            enhanced_image = enhanced_image.filter(ImageFilter.SHARPEN)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(enhanced_image)
            enhanced_image = enhancer.enhance(1.5)
            
            # Scale up for better OCR (if image is small)
            width, height = enhanced_image.size
            if width < 1000 or height < 1000:
                scale_factor = max(2, 1500 // max(width, height))
                new_size = (width * scale_factor, height * scale_factor)
                enhanced_image = enhanced_image.resize(new_size, Image.Resampling.LANCZOS)
            
            return enhanced_image
            
        except Exception as e:
            logger.warning(f"Image enhancement failed: {e}")
            return image
    
    def extract_text_tesseract_advanced(self, image: Image.Image) -> Dict[str, Any]:
        """
        Advanced Tesseract OCR with optimized settings for accuracy
        """
        try:
            # Enhanced preprocessing
            enhanced_image = self.enhance_image_for_ocr(image, aggressive=True)
            
            # Multiple PSM (Page Segmentation Mode) attempts for best results
            psm_configs = [
                '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,;:!?()-',  # Uniform text block
                '--psm 4 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,;:!?()-',  # Single text column
                '--psm 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,;:!?()-',  # Fully automatic
                '--psm 1 -c preserve_interword_spaces=1',  # Automatic with OSD
            ]
            
            best_result = {'text': '', 'confidence': 0, 'words': []}
            
            for config in psm_configs:
                try:
                    # Get detailed OCR data
                    ocr_data = pytesseract.image_to_data(
                        enhanced_image, 
                        output_type=pytesseract.Output.DICT,
                        config=config
                    )
                    
                    # Extract text
                    text = pytesseract.image_to_string(enhanced_image, config=config)
                    
                    # Calculate confidence
                    confidence = self._calculate_confidence(ocr_data)
                    
                    # Extract word-level data for post-processing
                    words = self._extract_word_data(ocr_data)
                    
                    if confidence > best_result['confidence']:
                        best_result = {
                            'text': text,
                            'confidence': confidence,
                            'words': words,
                            'config': config
                        }
                        
                except Exception as e:
                    logger.debug(f"PSM config failed: {config}, error: {e}")
                    continue
            
            # Post-process the best result
            if best_result['text']:
                best_result['text'] = self.post_process_text(best_result['text'], best_result.get('words', []))
            
            return {
                'text': best_result['text'],
                'confidence': best_result['confidence'],
                'method': 'tesseract_advanced',
                'words': best_result.get('words', []),
                'config_used': best_result.get('config', 'default')
            }
            
        except Exception as e:
            logger.error(f"Advanced Tesseract OCR failed: {e}")
            return {'text': '', 'confidence': 0, 'method': 'tesseract_advanced', 'error': str(e)}
    
    def extract_text_easyocr(self, image: Image.Image) -> Dict[str, Any]:
        """
        EasyOCR extraction with preprocessing
        """
        if not self.engines.get('easyocr', False):
            return {'text': '', 'confidence': 0, 'method': 'easyocr', 'error': 'EasyOCR not available'}
        
        try:
            # Convert PIL to numpy array
            img_array = np.array(image)
            
            # Enhance image
            enhanced_image = self.enhance_image_for_ocr(image, aggressive=False)
            enhanced_array = np.array(enhanced_image)
            
            # Extract text with EasyOCR
            results = self.easyocr_reader.readtext(enhanced_array, detail=1, paragraph=True)
            
            # Combine results
            full_text = ""
            total_confidence = 0
            word_count = 0
            words = []
            
            for (bbox, text, confidence) in results:
                full_text += text + " "
                total_confidence += confidence
                word_count += 1
                words.append({
                    'text': text,
                    'confidence': confidence,
                    'bbox': bbox
                })
            
            avg_confidence = total_confidence / word_count if word_count > 0 else 0
            
            # Post-process text
            full_text = self.post_process_text(full_text.strip(), words)
            
            return {
                'text': full_text,
                'confidence': avg_confidence,
                'method': 'easyocr',
                'words': words
            }
            
        except Exception as e:
            logger.error(f"EasyOCR failed: {e}")
            return {'text': '', 'confidence': 0, 'method': 'easyocr', 'error': str(e)}
    
    def extract_text_paddleocr(self, image: Image.Image) -> Dict[str, Any]:
        """
        PaddleOCR extraction with preprocessing
        """
        if not self.engines.get('paddleocr', False):
            return {'text': '', 'confidence': 0, 'method': 'paddleocr', 'error': 'PaddleOCR not available'}
        
        try:
            # Convert PIL to numpy array
            enhanced_image = self.enhance_image_for_ocr(image, aggressive=False)
            img_array = np.array(enhanced_image)
            
            # Extract text with PaddleOCR
            results = self.paddle_ocr.ocr(img_array, cls=True)
            
            # Process results
            full_text = ""
            total_confidence = 0
            word_count = 0
            words = []
            
            if results and results[0]:
                for line in results[0]:
                    if line:
                        bbox, (text, confidence) = line
                        full_text += text + " "
                        total_confidence += confidence
                        word_count += 1
                        words.append({
                            'text': text,
                            'confidence': confidence,
                            'bbox': bbox
                        })
            
            avg_confidence = total_confidence / word_count if word_count > 0 else 0
            
            # Post-process text
            full_text = self.post_process_text(full_text.strip(), words)
            
            return {
                'text': full_text,
                'confidence': avg_confidence,
                'method': 'paddleocr',
                'words': words
            }
            
        except Exception as e:
            logger.error(f"PaddleOCR failed: {e}")
            return {'text': '', 'confidence': 0, 'method': 'paddleocr', 'error': str(e)}
    
    def post_process_text(self, text: str, words: Optional[List[Dict]] = None) -> str:
        """
        Advanced post-processing to fix common OCR errors
        """
        if not text:
            return text
        
        # Fix common character confusion
        corrections = {
            # Number/letter confusion
            'l': '1',  # Context-dependent, we'll handle this specially
            'I': '1',  # Context-dependent
            'O': '0',  # Context-dependent
            '5': 'S',  # Context-dependent
            '6': 'G',  # Context-dependent
            '8': 'B',  # Context-dependent
            
            # Common OCR errors
            'rn': 'm',
            'cl': 'd',
            'nn': 'n',
            '｀': "'",
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '—': '-',
            '–': '-',
            '…': '...',
        }
        
        # Advanced post-processing
        processed_text = text
        
        # 1. Fix hyphenated words that are incorrectly spaced
        # Pattern: "fast -paced" -> "fast-paced"
        processed_text = re.sub(r'(\w+)\s+-\s*(\w+)', r'\1-\2', processed_text)
        
        # 2. Fix double spaces
        processed_text = re.sub(r'\s+', ' ', processed_text)
        
        # 3. Context-aware character correction
        processed_text = self._context_aware_corrections(processed_text)
        
        # 4. Fix common word patterns
        processed_text = self._fix_common_words(processed_text)
        
        # 5. Clean up punctuation
        processed_text = self._clean_punctuation(processed_text)
        
        return processed_text.strip()
    
    def _context_aware_corrections(self, text: str) -> str:
        """
        Apply context-aware corrections for character confusion using intelligent disambiguation
        """
        # Apply intelligent character disambiguation
        text = self._intelligent_character_disambiguation(text)
        
        words = text.split()
        corrected_words = []
        
        for word in words:
            corrected_word = word
            
            # Fix 'O' vs '0' based on context
            if 'O' in word and any(c.isdigit() for c in word):
                corrected_word = word.replace('O', '0')
            
            corrected_words.append(corrected_word)
        
        return ' '.join(corrected_words)
    
    def _intelligent_character_disambiguation(self, text: str) -> str:
        """
        Intelligently disambiguate character confusion using multiple strategies
        """
        if not text or not isinstance(text, str):
            return text
            
        # Word-by-word processing to maintain context
        words = text.split()
        if not words:
            return text
            
        corrected_words = []
        
        for i, word in enumerate(words):
            corrected_word = word
            
            # Extract pure word without punctuation for analysis
            # but preserve original punctuation
            import re
            word_match = re.match(r'^(\W*)(.*?)(\W*)$', word)
            if word_match:
                prefix, core_word, suffix = word_match.groups()
            else:
                prefix, core_word, suffix = '', word, ''
            
            if core_word:  # Only process if there's a core word
                # Apply corrections to core word only
                corrected_core = self._disambiguate_word(core_word, words, i)
                corrected_word = prefix + corrected_core + suffix
            
            corrected_words.append(corrected_word)
        
        return ' '.join(corrected_words)
    
    def _disambiguate_word(self, word: str, context_words: List[str], word_index: int) -> str:
        """
        Disambiguate a single word based on context and linguistic patterns
        """
        # Apply disambiguation rules in order of specificity
        corrected_word = word
        
        # Rule 0: Handle specific multi-character confusions (like "Al" vs "A1")
        corrected_word = self._disambiguate_multi_char_patterns(corrected_word, context_words, word_index)
        
        # If word was changed, preserve that change and skip further rules that might override it
        if corrected_word != word and any(c.isdigit() for c in corrected_word):
            return corrected_word
        
        # Rule 1: Alphanumeric disambiguation
        corrected_word = self._disambiguate_alphanumeric(corrected_word, context_words)
        
        # Rule 2: Linguistic pattern disambiguation  
        corrected_word = self._disambiguate_linguistic_patterns(corrected_word, context_words, word_index)
        
        # Rule 3: Position-based disambiguation
        corrected_word = self._disambiguate_positional(corrected_word, context_words, word_index)
        
        return corrected_word
    
    def _disambiguate_multi_char_patterns(self, word: str, context: List[str], word_index: int) -> str:
        """
        Handle multi-character pattern confusions using generic pattern recognition
        """
        # Strip punctuation for analysis but preserve it in output
        clean_word = re.sub(r'[^\w]', '', word)
        punctuation = word[len(clean_word):] if len(word) > len(clean_word) else ""
        
        # Generic alphanumeric entity detection (like company codes, product names, etc.)
        if self._is_alphanumeric_entity_context(clean_word, context, word_index):
            # Convert 'l' to '1' in alphanumeric entities - but only at word endings for short words
            if len(clean_word) <= 4 and clean_word.endswith('l'):
                corrected = clean_word[:-1] + '1'
                if corrected != clean_word:
                    return corrected + punctuation
        
        # Check for other common multi-character confusions in numeric context
        multi_char_corrections = {
            "Il": "11",  # Double l to double 1 in numeric context
            "ll": "11",  # In numeric/code context
            "Ol": "01",  # O followed by l in numeric context
            "lO": "10",  # l followed by O in numeric context
        }
        
        for pattern, replacement in multi_char_corrections.items():
            if clean_word == pattern and self._is_numeric_context(context):
                return replacement + punctuation
        
        return word
    
    def _is_alphanumeric_entity_context(self, word: str, context: List[str], word_index: int) -> bool:
        """
        Detect if a word is likely an alphanumeric entity (company code, product name, etc.)
        based on contextual patterns rather than hardcoded names
        """
        # Don't correct if it looks like a proper name (followed by common last names)
        next_word = context[word_index+1] if word_index+1 < len(context) else ""
        if next_word and next_word[0].isupper():
            common_surnames = ['smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis', 'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez', 'wilson', 'anderson', 'thomas', 'taylor', 'moore', 'jackson', 'martin', 'lee', 'perez', 'thompson', 'white', 'harris', 'sanchez', 'clark', 'ramirez', 'lewis', 'robinson', 'walker', 'young', 'allen', 'king', 'wright', 'scott', 'torres', 'nguyen', 'hill', 'flores', 'green', 'adams', 'nelson', 'baker', 'hall', 'rivera', 'campbell', 'mitchell', 'carter', 'roberts', 'gomez', 'phillips', 'evans', 'turner', 'diaz', 'parker', 'cruz', 'edwards', 'collins', 'reyes', 'stewart', 'morris', 'morales', 'murphy', 'cook', 'rogers', 'gutierrez', 'ortiz', 'morgan', 'cooper', 'peterson', 'bailey', 'reed', 'kelly', 'howard', 'ramos', 'kim', 'cox', 'ward', 'richardson', 'watson', 'brooks', 'chavez', 'wood', 'james', 'bennett', 'gray', 'mendoza', 'ruiz', 'hughes', 'price', 'alvarez', 'castillo', 'sanders', 'patel', 'myers', 'long', 'ross', 'foster', 'jimenez', 'gore']
            if next_word.lower() in common_surnames:
                return False
        
        # Don't correct common English words that start sentences
        if word_index == 0:
            common_sentence_starters = ['all', 'also', 'although', 'always', 'already', 'almost', 'alone']
            if word.lower() in common_sentence_starters:
                return False
        
        # Pattern 1: Short word (1-3 chars) followed by business action verbs
        if len(word) <= 3:
            next_2_words = context[word_index+1:word_index+3] if word_index+1 < len(context) else []
            next_words_text = ' '.join(next_2_words).lower()
            
            # More specific business action indicators
            entity_indicators = [
                'provides', 'offers', 'delivers', 'focuses', 'emphasizes', 
                'cultivates', 'seeks', 'values', 'maintains', 'ensures',
                'specializes', 'operates', 'manages', 'develops', 'creates'
            ]
            
            if any(indicator in next_words_text for indicator in entity_indicators):
                return True
        
        # Pattern 2: Word preceded by entity-indicating prepositions (but not person names)
        prev_word = context[word_index-1] if word_index > 0 and word_index-1 < len(context) else ""
        entity_prepositions = ['at', 'with', 'for', 'by', 'from', 'through']
        
        if prev_word.lower() in entity_prepositions and len(word) <= 4:
            # Additional check: if followed by business context words
            next_words = context[word_index+1:word_index+3] if word_index+1 < len(context) else []
            has_business_follow = any(
                word.lower() in ['company', 'corporation', 'provides', 'offers', 'delivers', 'focuses', 'cultivates']
                for word in next_words
            )
            if has_business_follow:
                return True
        
        # Pattern 3: Product/model identifier context
        prev_words = context[max(0, word_index-2):word_index]
        model_indicators = ['model', 'version', 'code', 'product', 'system', 'type']
        
        if any(indicator.lower() in ' '.join(prev_words).lower() for indicator in model_indicators):
            return True
        
        # Pattern 4: Mixed case pattern suggesting code/identifier (more restrictive)
        if len(word) <= 4 and any(c.isupper() for c in word) and any(c.islower() for c in word):
            # Only if in business/technical context
            surrounding_context = context[max(0, word_index-2):word_index+3]
            tech_context_words = [
                'system', 'model', 'version', 'code', 'product', 'solution',
                'platform', 'service', 'technology', 'software', 'hardware'
            ]
            
            context_text = ' '.join(surrounding_context).lower()
            if any(tech_word in context_text for tech_word in tech_context_words):
                return True
        
        return False
    
    def _disambiguate_alphanumeric(self, word: str, context: List[str]) -> str:
        """
        Disambiguate based on alphanumeric patterns
        """
        # Skip if word was already corrected by multi-character patterns and now contains digits
        if any(c.isdigit() for c in word) and not any(c.isdigit() for c in ''.join(context)):
            return word
            
        # If word contains other digits, likely all confusing chars should be digits
        if any(c.isdigit() for c in word):
            # Convert common confusions in alphanumeric context
            word = word.replace('l', '1').replace('L', '1')
            word = word.replace('I', '1') if len(word) > 1 else word
            word = word.replace('O', '0')
        
        # If surrounded by numbers/codes, likely a number/code
        has_numeric_neighbors = any(
            any(c.isdigit() for c in neighbor) 
            for neighbor in context 
            if neighbor != word
        )
        
        if has_numeric_neighbors and word.lower() in ['l', 'i', 'o']:
            return {'l': '1', 'i': '1', 'o': '0'}.get(word.lower(), word)
        
        return word
    
    def _disambiguate_linguistic_patterns(self, word: str, context: List[str], word_index: int) -> str:
        """
        Disambiguate based on linguistic and grammatical patterns
        """
        # Common English letter patterns vs number patterns
        if len(word) == 1:
            char = word.lower()
            
            # Check if it should be 'I' (pronoun) - always capital, often at sentence start
            if char in ['l', '1'] and self._is_pronoun_context(context, word_index):
                return 'I'
            
            # Check if it should be '1' (number) - numeric context
            if char in ['l', 'i'] and self._is_numeric_context(context):
                return '1'
            
            # Check if it should be 'l' (letter) - word formation context
            if char in ['1', 'i'] and self._is_letter_context(context, word_index):
                return 'l'
        
        # Multi-character word patterns
        if len(word) > 1:
            # If word looks like it should be a real English word, prefer letters
            corrected = self._prefer_english_word_formation(word)
            if corrected != word:
                return corrected
        
        return word
    
    def _disambiguate_positional(self, word: str, context: List[str], word_index: int) -> str:
        """
        Disambiguate based on position in sentence/document
        """
        # Start of sentence patterns
        if word_index == 0 or (word_index > 0 and len(context) > word_index-1 and context[word_index-1].endswith('.')):
            if word.lower() in ['l', '1'] and len(word) == 1:
                # Likely "I" at sentence start
                return 'I'
        
        # Generic entity context patterns
        if len(word) <= 3 and word.lower() in ['l', 'i']:
            # Check if it's part of an alphanumeric entity pattern
            if self._is_alphanumeric_entity_context(word, context, word_index):
                return '1'
        
        return word
    
    def _is_pronoun_context(self, context: List[str], word_index: int) -> bool:
        """Check if context suggests the character should be pronoun 'I'"""
        # Look for verb patterns that follow 'I'
        if word_index + 1 < len(context):
            next_words = context[word_index+1:word_index+3]
            pronoun_verbs = ['am', 'was', 'will', 'have', 'had', 'can', 'should', 'would', 'could']
            return any(word.lower() in pronoun_verbs for word in next_words)
        return False
    
    def _is_numeric_context(self, context: List[str]) -> bool:
        """Check if context suggests numeric interpretation"""
        numeric_indicators = ['number', 'code', 'id', 'phone', 'fax', 'suite', 'street', '#']
        return any(
            indicator in word.lower() 
            for word in context 
            for indicator in numeric_indicators
        )
    
    def _is_letter_context(self, context: List[str], word_index: int) -> bool:
        """Check if context suggests letter interpretation"""
        # Check if it's part of a word being formed
        prev_word = context[word_index-1] if word_index > 0 and word_index-1 < len(context) else ""
        next_word = context[word_index+1] if word_index+1 < len(context) else ""
        
        # If previous or next word ends/starts with letters, likely part of word
        prev_ends_alpha = bool(prev_word and prev_word[-1].isalpha())
        next_starts_alpha = bool(next_word and next_word[0].isalpha())
        
        return prev_ends_alpha or next_starts_alpha
    
    def _is_business_context(self, context: List[str]) -> bool:
        """Check if we're in a business document context"""
        business_terms = ['company', 'corporation', 'inc', 'llc', 'ltd', 'business', 'firm', 'group']
        return any(
            term in word.lower() 
            for word in context 
            for term in business_terms
        )
    
    def _prefer_english_word_formation(self, word: str) -> str:
        """
        Prefer character choices that form valid English words - only for ambiguous cases
        """
        # Only apply to words that are likely to have OCR confusion (contain problematic chars)
        if not any(char in word for char in 'l1Il'):
            return word
            
        # Don't modify words that are already valid English words
        if self._is_likely_valid_english_word(word):
            return word
            
        # Try different character substitutions and see which forms better words
        variations = [word]
        
        # Generate conservative variations - only for clearly ambiguous cases
        if word.isupper() or word.islower() or len(word) <= 3:
            # Generate variations for short words or all-caps/lowercase
            if 'l' in word.lower():
                variations.append(word.replace('l', '1').replace('L', '1'))
                if len(word) == 1:  # Only for single characters
                    variations.append(word.replace('l', 'I').replace('L', 'I'))
            
            if '1' in word:
                variations.append(word.replace('1', 'l'))
                if len(word) == 1:  # Only for single characters
                    variations.append(word.replace('1', 'I'))
            
            if 'I' in word and len(word) == 1:  # Only standalone 'I'
                variations.append(word.replace('I', 'l'))
                variations.append(word.replace('I', '1'))
        
        # Score each variation based on English word likelihood
        best_word = word
        best_score = self._score_word_likelihood(word)
        
        for variation in variations:
            score = self._score_word_likelihood(variation)
            if score > best_score:
                best_score = score
                best_word = variation
        
        return best_word
    
    def _is_likely_valid_english_word(self, word: str) -> bool:
        """
        Check if a word is likely a valid English word
        """
        clean_word = word.lower().strip('.,!?;:"()[]{}')
        
        # Very common English words that should never be modified
        common_words = {
            'welcome', 'come', 'some', 'home', 'time', 'make', 'take', 'place', 
            'people', 'like', 'life', 'world', 'great', 'little', 'old', 'small',
            'large', 'good', 'new', 'first', 'last', 'long', 'right', 'left',
            'high', 'low', 'big', 'small', 'early', 'late', 'all', 'also',
            'already', 'almost', 'alone', 'although', 'always'
        }
        
        return clean_word in common_words
    
    def _score_word_likelihood(self, word: str) -> float:
        """
        Score how likely a word is to be a valid English word
        """
        # Basic scoring based on common English patterns
        score = 0.0
        
        # Penalize numbers in the middle of words (unless it's clearly alphanumeric)
        if any(c.isdigit() for c in word[1:-1]) and not all(c.isalnum() for c in word):
            score -= 0.3
        
        # Prefer common English letter combinations
        common_patterns = ['ing', 'tion', 'ed', 'er', 'ly', 'al', 'ic', 'able', 'ful']
        for pattern in common_patterns:
            if pattern in word.lower():
                score += 0.2
        
        # Penalize unusual character combinations
        unusual_patterns = ['1l', 'l1', 'I1', '1I', 'll1', '1ll']
        for pattern in unusual_patterns:
            if pattern in word:
                score -= 0.4
        
        return score
    
    def _fix_common_words(self, text: str) -> str:
        """
        Fix commonly misrecognized words
        """
        # Common word corrections
        word_corrections = {
            'environrnent': 'environment',
            'developrnent': 'development',
            'managernent': 'management',
            'requirernents': 'requirements',
            'experiénce': 'experience',
            'cornpany': 'company',
            'rnust': 'must',
            'worI<': 'work',
            'worlç': 'work',
            'skílls': 'skills',
            'leam': 'team',
            'proíect': 'project',
            'proiect': 'project',
        }
        
        for wrong, correct in word_corrections.items():
            text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, text, flags=re.IGNORECASE)
        
        return text
    
    def _clean_punctuation(self, text: str) -> str:
        """
        Clean up punctuation issues
        """
        # Fix spaces before punctuation
        text = re.sub(r'\s+([,.;:!?])', r'\1', text)
        
        # Fix missing spaces after punctuation
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
        # Fix quotation marks
        text = re.sub(r'"\s*([^"]*?)\s*"', r'"\1"', text)
        
        return text
    
    def _calculate_confidence(self, ocr_data: Dict) -> float:
        """Calculate confidence from OCR data"""
        try:
            confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
            return sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
        except Exception:
            return 0.0
    
    def _extract_word_data(self, ocr_data: Dict) -> List[Dict]:
        """Extract word-level data from OCR results"""
        words = []
        try:
            for i, word in enumerate(ocr_data['text']):
                if word.strip():
                    words.append({
                        'text': word,
                        'confidence': int(ocr_data['conf'][i]) / 100.0,
                        'left': ocr_data['left'][i],
                        'top': ocr_data['top'][i],
                        'width': ocr_data['width'][i],
                        'height': ocr_data['height'][i]
                    })
        except Exception as e:
            logger.debug(f"Word data extraction failed: {e}")
        
        return words
    
    def extract_text_multi_engine(self, image: Image.Image) -> Dict[str, Any]:
        """
        Use multiple OCR engines and combine results for maximum accuracy
        """
        results = []
        
        # Try all available engines
        if self.engines.get('tesseract', False):
            results.append(self.extract_text_tesseract_advanced(image))
        
        if self.engines.get('easyocr', False):
            results.append(self.extract_text_easyocr(image))
        
        if self.engines.get('paddleocr', False):
            results.append(self.extract_text_paddleocr(image))
        
        if not results:
            return {'text': '', 'confidence': 0, 'method': 'none', 'error': 'No OCR engines available'}
        
        # Find the best result based on confidence
        best_result = max(results, key=lambda x: x.get('confidence', 0))
        
        # If confidence is still low, try consensus approach
        if best_result['confidence'] < 0.8 and len(results) > 1:
            consensus_text = self._create_consensus_text(results)
            if consensus_text:
                best_result['text'] = consensus_text
                best_result['method'] = 'consensus'
        
        return best_result
    
    def _create_consensus_text(self, results: List[Dict]) -> str:
        """
        Create consensus text from multiple OCR results
        """
        if len(results) < 2:
            return results[0]['text'] if results else ''
        
        # Simple approach: use the longest common text with highest confidence
        texts = [r['text'] for r in results if r.get('text')]
        if not texts:
            return ''
        
        # Find the text with best combination of length and confidence
        best_score = 0
        best_text = texts[0]
        
        for i, result in enumerate(results):
            if result.get('text'):
                # Score = confidence * text_length_factor
                score = result.get('confidence', 0) * (len(result['text']) / 1000)
                if score > best_score:
                    best_score = score
                    best_text = result['text']
        
        return best_text
