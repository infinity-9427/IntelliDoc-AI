import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    pipeline, AutoModelForTokenClassification
)
from sentence_transformers import SentenceTransformer
import numpy as np
from textblob import TextBlob
from langdetect import detect

logger = logging.getLogger(__name__)

class AIService:
    """AI Service for document analysis using transformer models"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Model configurations
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        
        # Initialize models asynchronously when needed
        self._models_loaded = False
        
    async def initialize_models(self):
        """Initialize AI models"""
        if self._models_loaded:
            return
            
        try:
            logger.info("Initializing AI models...")
            
            # Document classification pipeline
            self.pipelines['classification'] = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                return_all_scores=True,
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Named Entity Recognition
            self.pipelines['ner'] = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Sentiment Analysis
            self.pipelines['sentiment'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True,
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Text Summarization
            self.pipelines['summarization'] = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Sentence embeddings for similarity
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            self._models_loaded = True
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {str(e)}")
            raise
    
    async def analyze_document(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive document analysis using AI models
        """
        if not self._models_loaded:
            await self.initialize_models()
        
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            if not cleaned_text.strip():
                return self._empty_analysis_result()
            
            # Detect language
            language = await self._detect_language(cleaned_text)
            
            # Run analysis tasks in parallel
            tasks = [
                self._classify_document(cleaned_text),
                self._extract_entities(cleaned_text),
                self._analyze_sentiment(cleaned_text),
                self._extract_key_information(cleaned_text),
                self._generate_summary(cleaned_text),
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            analysis_result = {
                'document_classification': results[0] if not isinstance(results[0], Exception) else {'type': 'unknown', 'confidence': 0.0},
                'entities': results[1] if not isinstance(results[1], Exception) else [],
                'sentiment_analysis': results[2] if not isinstance(results[2], Exception) else {'overall_sentiment': 'neutral', 'confidence': 0.5},
                'key_information': results[3] if not isinstance(results[3], Exception) else {},
                'summary': results[4] if not isinstance(results[4], Exception) else 'Summary generation failed',
                'language': language,
                'text_statistics': self._calculate_text_statistics(cleaned_text)
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Document analysis error: {str(e)}")
            return self._empty_analysis_result(error=str(e))
    
    async def _classify_document(self, text: str) -> Dict[str, Any]:
        """Classify document type"""
        try:
            # Truncate text for classification
            max_length = 512
            truncated_text = text[:max_length] if len(text) > max_length else text
            
            # Simple rule-based classification for now
            document_types = {
                'invoice': ['invoice', 'bill', 'payment', 'amount', 'total', 'due'],
                'contract': ['agreement', 'contract', 'terms', 'conditions', 'party'],
                'report': ['report', 'analysis', 'conclusion', 'findings', 'summary'],
                'letter': ['dear', 'sincerely', 'regards', 'letter'],
                'resume': ['experience', 'education', 'skills', 'work', 'cv'],
                'legal': ['law', 'legal', 'court', 'jurisdiction', 'whereas'],
                'academic': ['abstract', 'introduction', 'methodology', 'references'],
                'technical': ['technical', 'specification', 'implementation', 'system']
            }
            
            text_lower = text.lower()
            scores = {}
            
            for doc_type, keywords in document_types.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                scores[doc_type] = score / len(keywords)
            
            # Find best match
            best_type = max(scores, key=scores.get)
            confidence = scores[best_type]
            
            return {
                'type': best_type if confidence > 0.1 else 'unknown',
                'confidence': min(confidence, 1.0),
                'all_scores': scores
            }
            
        except Exception as e:
            logger.error(f"Document classification error: {str(e)}")
            return {'type': 'unknown', 'confidence': 0.0}
    
    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text"""
        try:
            # Truncate text if too long
            max_length = 512
            chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            
            all_entities = []
            
            for chunk in chunks[:3]:  # Process max 3 chunks
                try:
                    entities = self.pipelines['ner'](chunk)
                    
                    for entity in entities:
                        all_entities.append({
                            'text': entity['word'],
                            'label': entity['entity_group'],
                            'confidence': entity['score'],
                            'start': entity.get('start', 0),
                            'end': entity.get('end', 0)
                        })
                except Exception as e:
                    logger.warning(f"NER failed for chunk: {str(e)}")
                    continue
            
            # Remove duplicates and sort by confidence
            unique_entities = []
            seen_texts = set()
            
            for entity in sorted(all_entities, key=lambda x: x['confidence'], reverse=True):
                if entity['text'].lower() not in seen_texts:
                    unique_entities.append(entity)
                    seen_texts.add(entity['text'].lower())
            
            return unique_entities[:20]  # Return top 20 entities
            
        except Exception as e:
            logger.error(f"Entity extraction error: {str(e)}")
            return []
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the document"""
        try:
            # Use TextBlob for basic sentiment analysis
            blob = TextBlob(text[:1000])  # Analyze first 1000 chars
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Convert polarity to sentiment label
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            confidence = abs(polarity) if abs(polarity) > 0.1 else 0.5
            
            return {
                'overall_sentiment': sentiment,
                'confidence': min(confidence, 1.0),
                'polarity': polarity,
                'subjectivity': subjectivity
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {
                'overall_sentiment': 'neutral',
                'confidence': 0.5,
                'polarity': 0.0,
                'subjectivity': 0.0
            }
    
    async def _extract_key_information(self, text: str) -> Dict[str, Any]:
        """Extract key information using regex patterns"""
        try:
            key_info = {}
            
            # Email addresses
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            if emails:
                key_info['emails'] = list(set(emails))
            
            # Phone numbers (various formats)
            phones = re.findall(r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', text)
            if phones:
                key_info['phone_numbers'] = [f"({area}){exchange}-{number}" for area, exchange, number in phones]
            
            # Dates (MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD)
            dates = re.findall(r'\b(?:\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}[/\-]\d{1,2}[/\-]\d{1,2})\b', text)
            if dates:
                key_info['dates'] = list(set(dates))
            
            # Currency amounts
            amounts = re.findall(r'\$\s?[\d,]+\.?\d*|\b\d+\.\d{2}\s?(?:USD|EUR|GBP)\b', text)
            if amounts:
                key_info['monetary_amounts'] = list(set(amounts))
            
            # URLs
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
            if urls:
                key_info['urls'] = list(set(urls))
            
            # Extract potential names (capitalized words)
            potential_names = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', text)
            if potential_names:
                key_info['potential_names'] = list(set(potential_names))
            
            return key_info
            
        except Exception as e:
            logger.error(f"Key information extraction error: {str(e)}")
            return {}
    
    async def _generate_summary(self, text: str) -> str:
        """Generate a summary of the document"""
        try:
            # If text is short, return it as is
            if len(text) < 200:
                return text[:150] + "..." if len(text) > 150 else text
            
            # For longer texts, use extractive summarization
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
            
            if len(sentences) <= 3:
                return " ".join(sentences)
            
            # Simple extractive summarization - take first, middle, and key sentences
            summary_sentences = []
            
            # Add first sentence
            if sentences:
                summary_sentences.append(sentences[0])
            
            # Add middle sentence
            if len(sentences) > 2:
                middle_idx = len(sentences) // 2
                summary_sentences.append(sentences[middle_idx])
            
            # Add last sentence if it looks conclusive
            if len(sentences) > 1:
                last_sentence = sentences[-1]
                if any(word in last_sentence.lower() for word in ['conclusion', 'summary', 'total', 'result']):
                    summary_sentences.append(last_sentence)
            
            summary = " ".join(summary_sentences)
            
            # Truncate if too long
            return summary[:500] + "..." if len(summary) > 500 else summary
            
        except Exception as e:
            logger.error(f"Summary generation error: {str(e)}")
            return "Unable to generate summary."
    
    async def _detect_language(self, text: str) -> str:
        """Detect the language of the text"""
        try:
            # Use first 1000 characters for language detection
            sample_text = text[:1000] if len(text) > 1000 else text
            language = detect(sample_text)
            return language
        except Exception as e:
            logger.warning(f"Language detection failed: {str(e)}")
            return 'en'  # Default to English
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
        
        return text.strip()
    
    def _calculate_text_statistics(self, text: str) -> Dict[str, Any]:
        """Calculate basic text statistics"""
        try:
            words = text.split()
            sentences = re.split(r'[.!?]+', text)
            sentences = [s for s in sentences if s.strip()]
            
            return {
                'character_count': len(text),
                'word_count': len(words),
                'sentence_count': len(sentences),
                'average_words_per_sentence': len(words) / len(sentences) if sentences else 0,
                'average_characters_per_word': len(text) / len(words) if words else 0
            }
        except Exception:
            return {
                'character_count': len(text),
                'word_count': 0,
                'sentence_count': 0,
                'average_words_per_sentence': 0,
                'average_characters_per_word': 0
            }
    
    def _empty_analysis_result(self, error: str = None) -> Dict[str, Any]:
        """Return empty analysis result structure"""
        result = {
            'document_classification': {'type': 'unknown', 'confidence': 0.0},
            'entities': [],
            'sentiment_analysis': {'overall_sentiment': 'neutral', 'confidence': 0.5},
            'key_information': {},
            'summary': 'No analysis available',
            'language': 'unknown',
            'text_statistics': {
                'character_count': 0,
                'word_count': 0,
                'sentence_count': 0,
                'average_words_per_sentence': 0,
                'average_characters_per_word': 0
            }
        }
        
        if error:
            result['error'] = error
            
        return result
