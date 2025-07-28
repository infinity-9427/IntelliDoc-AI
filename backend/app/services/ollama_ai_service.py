import asyncio
import logging
import re
import json
import os
from typing import Dict, Any, List, Optional
import httpx
from textblob import TextBlob
from langdetect import detect
from .prompts import DocumentPrompts

logger = logging.getLogger(__name__)

class OllamaAIService:
    """AI Service using local Ollama/Llama3 for document analysis"""
    
    def __init__(self, ollama_host: Optional[str] = None, model_name: Optional[str] = None):
        # Read from environment variables with fallbacks
        self.ollama_host = (ollama_host or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip('/')
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.embed_model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        self.timeout = float(os.getenv("OLLAMA_TIMEOUT", "120.0"))
        
        # HTTP client for async requests
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(self.timeout))
        
        # Initialize prompts manager
        self.prompts = DocumentPrompts()
        
        logger.info(f"Initialized Ollama AI Service with host: {ollama_host}")
        
    async def initialize_models(self):
        """Check if Ollama is available and model is loaded"""
        try:
            # Test connection to Ollama
            response = await self.client.get(f"{self.ollama_host}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                logger.info(f"Available Ollama models: {available_models}")
                
                # Check if our configured model is available
                model_found = False
                for model in available_models:
                    if self.model_name in model or model in self.model_name:
                        self.model_name = model  # Use the exact model name from Ollama
                        model_found = True
                        break
                
                if not model_found:
                    logger.warning(f"Configured model '{self.model_name}' not found. Available models: {available_models}")
                    # Check for llama3 variants
                    for model in available_models:
                        if 'llama3' in model.lower():
                            self.model_name = model
                            model_found = True
                            logger.info(f"Using similar model: {self.model_name}")
                            break
                    
                    if not model_found and available_models:
                        self.model_name = available_models[0]  # Use first available as fallback
                        logger.info(f"Using fallback model: {self.model_name}")
                
                logger.info(f"Using Ollama model: {self.model_name}")
                return True
            else:
                logger.error(f"Ollama not accessible: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {str(e)}")
            return False
    
    async def analyze_document(self, text: str) -> Dict[str, Any]:
        """Comprehensive document analysis using local Llama3"""
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            if not cleaned_text.strip():
                return self._empty_analysis_result()
            
            # Detect language first (lightweight operation)
            language = await self._detect_language(cleaned_text)
            
            # Run AI analysis tasks
            analysis_tasks = await asyncio.gather(
                self._classify_document_with_llama(cleaned_text),
                self._extract_entities_with_llama(cleaned_text),
                self._analyze_sentiment_with_llama(cleaned_text),
                self._generate_summary_with_llama(cleaned_text),
                return_exceptions=True
            )
            
            # Extract key information using regex (lightweight)
            key_info = await self._extract_key_information(cleaned_text)
            
            # Combine results
            analysis_result = {
                'document_classification': analysis_tasks[0] if not isinstance(analysis_tasks[0], Exception) else {'type': 'unknown', 'confidence': 0.0},
                'entities': analysis_tasks[1] if not isinstance(analysis_tasks[1], Exception) else [],
                'sentiment_analysis': analysis_tasks[2] if not isinstance(analysis_tasks[2], Exception) else {'overall_sentiment': 'neutral', 'confidence': 0.5},
                'summary': analysis_tasks[3] if not isinstance(analysis_tasks[3], Exception) else 'Summary generation failed',
                'key_information': key_info,
                'language': language,
                'text_statistics': self._calculate_text_statistics(cleaned_text)
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Document analysis error: {str(e)}")
            return self._empty_analysis_result(error=str(e))
    
    async def _query_llama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Send a query to local Llama3 and get response"""
        try:
            # Prepare the request payload
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more consistent results
                    "top_p": 0.9,
                    "num_predict": 512   # Limit response length
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            # Send request to Ollama
            response = await self.client.post(
                f"{self.ollama_host}/api/generate",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama request failed: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Llama query error: {str(e)}")
            return ""
    
    async def _classify_document_with_llama(self, text: str) -> Dict[str, Any]:
        """Classify document type using Llama3"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Generate prompts using centralized prompt manager
            system_prompt = self.prompts.get_classification_system_prompt()
            user_prompt = self.prompts.get_classification_prompt(text)
            
            # Log prompt usage
            self.prompts.log_prompt_usage("classification", len(text))
            
            response = await self._query_llama(user_prompt, system_prompt)
            
            if response:
                # Try to parse JSON response
                try:
                    result = json.loads(response)
                    response_time = asyncio.get_event_loop().time() - start_time
                    self.prompts.log_prompt_usage("classification", len(text), response_time)
                    
                    return {
                        'type': result.get('type', 'unknown'),
                        'confidence': float(result.get('confidence', 0.5)),
                        'reasoning': result.get('reasoning', ''),
                        'secondary_type': result.get('secondary_type', ''),
                        'key_indicators': result.get('key_indicators', [])
                    }
                except json.JSONDecodeError:
                    # Fallback parsing
                    type_match = re.search(r'"type":\s*"([^"]+)"', response)
                    conf_match = re.search(r'"confidence":\s*([0-9.]+)', response)
                    
                    return {
                        'type': type_match.group(1) if type_match else 'unknown',
                        'confidence': float(conf_match.group(1)) if conf_match else 0.5
                    }
            
            # Fallback to simple rule-based classification
            return await self._simple_classify_document(text)
            
        except Exception as e:
            logger.error(f"Document classification error: {str(e)}")
            return {'type': 'unknown', 'confidence': 0.0}
    
    async def _extract_entities_with_llama(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using Llama3"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Generate prompts using centralized prompt manager
            system_prompt = self.prompts.get_entity_extraction_system_prompt()
            user_prompt = self.prompts.get_entity_extraction_prompt(text)
            
            # Log prompt usage
            self.prompts.log_prompt_usage("entity_extraction", len(text))
            
            response = await self._query_llama(user_prompt, system_prompt)
            
            if response:
                try:
                    # Try to parse JSON response
                    entities = json.loads(response)
                    if isinstance(entities, list):
                        response_time = asyncio.get_event_loop().time() - start_time
                        self.prompts.log_prompt_usage("entity_extraction", len(text), response_time)
                        return entities[:20]  # Limit to top 20
                except json.JSONDecodeError:
                    # Try to extract entities using regex
                    entity_matches = re.findall(r'"text":\s*"([^"]+)"[^}]*"label":\s*"([^"]+)"', response)
                    return [{'text': text, 'label': label, 'confidence': 0.8} for text, label in entity_matches[:20]]
            
            return []
            
        except Exception as e:
            logger.error(f"Entity extraction error: {str(e)}")
            return []
    
    async def _analyze_sentiment_with_llama(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using Llama3"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Generate prompts using centralized prompt manager
            system_prompt = self.prompts.get_sentiment_system_prompt()
            user_prompt = self.prompts.get_sentiment_prompt(text)
            
            # Log prompt usage
            self.prompts.log_prompt_usage("sentiment", len(text))
            
            response = await self._query_llama(user_prompt, system_prompt)
            
            if response:
                try:
                    result = json.loads(response)
                    sentiment = result.get('sentiment', 'neutral')
                    confidence = float(result.get('confidence', 0.5))
                    
                    response_time = asyncio.get_event_loop().time() - start_time
                    self.prompts.log_prompt_usage("sentiment", len(text), response_time)
                    
                    return {
                        'overall_sentiment': sentiment,
                        'confidence': confidence,
                        'reasoning': result.get('reasoning', ''),
                        'key_phrases': result.get('key_phrases', []),
                        'intensity': result.get('intensity', 'medium'),
                        'polarity': 0.5 if sentiment == 'positive' else (-0.5 if sentiment == 'negative' else 0.0),
                        'subjectivity': result.get('subjectivity', confidence)
                    }
                except (json.JSONDecodeError, ValueError):
                    # Fallback parsing
                    if 'positive' in response.lower():
                        sentiment = 'positive'
                    elif 'negative' in response.lower():
                        sentiment = 'negative'
                    else:
                        sentiment = 'neutral'
                    
                    return {
                        'overall_sentiment': sentiment,
                        'confidence': 0.7,
                        'polarity': 0.5 if sentiment == 'positive' else (-0.5 if sentiment == 'negative' else 0.0),
                        'subjectivity': 0.7
                    }
            
            # Fallback to TextBlob
            return await self._simple_analyze_sentiment(text)
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return await self._simple_analyze_sentiment(text)
    
    async def _generate_summary_with_llama(self, text: str) -> str:
        """Generate summary using Llama3"""
        try:
            # For very short texts, return as-is
            if len(text) < 200:
                return text[:150] + "..." if len(text) > 150 else text
            
            start_time = asyncio.get_event_loop().time()
            
            # Generate prompts using centralized prompt manager
            system_prompt = self.prompts.get_summarization_system_prompt()
            user_prompt = self.prompts.get_summarization_prompt(text)
            
            # Log prompt usage
            self.prompts.log_prompt_usage("summarization", len(text))
            
            response = await self._query_llama(user_prompt, system_prompt)
            
            if response and len(response.strip()) > 10:
                # Clean up the response
                summary = response.strip()
                # Remove any JSON artifacts
                summary = re.sub(r'^[{}\[\]"]*', '', summary)
                summary = re.sub(r'[{}\[\]"]*$', '', summary)
                
                response_time = asyncio.get_event_loop().time() - start_time
                self.prompts.log_prompt_usage("summarization", len(text), response_time)
                
                return summary[:500] + "..." if len(summary) > 500 else summary
            
            # Fallback to extractive summarization
            return await self._simple_generate_summary(text)
            
        except Exception as e:
            logger.error(f"Summary generation error: {str(e)}")
            return await self._simple_generate_summary(text)
    
    # Fallback methods using simpler approaches
    async def _simple_classify_document(self, text: str) -> Dict[str, Any]:
        """Simple rule-based document classification"""
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
        
        best_type = max(scores.keys(), key=lambda k: scores[k])
        confidence = scores[best_type]
        
        return {
            'type': best_type if confidence > 0.1 else 'unknown',
            'confidence': min(confidence, 1.0)
        }
    
    async def _simple_analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Simple sentiment analysis using TextBlob"""
        try:
            blob = TextBlob(text[:1000])
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
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
        except Exception:
            return {
                'overall_sentiment': 'neutral',
                'confidence': 0.5,
                'polarity': 0.0,
                'subjectivity': 0.0
            }
    
    async def _simple_generate_summary(self, text: str) -> str:
        """Simple extractive summarization"""
        try:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
            
            if len(sentences) <= 3:
                return " ".join(sentences)
            
            # Take first, middle, and potentially last sentence
            summary_sentences = [sentences[0]]
            
            if len(sentences) > 2:
                middle_idx = len(sentences) // 2
                summary_sentences.append(sentences[middle_idx])
            
            if len(sentences) > 1:
                last_sentence = sentences[-1]
                if any(word in last_sentence.lower() for word in ['conclusion', 'summary', 'total', 'result']):
                    summary_sentences.append(last_sentence)
            
            summary = " ".join(summary_sentences)
            return summary[:500] + "..." if len(summary) > 500 else summary
            
        except Exception:
            return "Unable to generate summary."
    
    async def _extract_key_information(self, text: str) -> Dict[str, Any]:
        """Extract key information using regex patterns"""
        try:
            key_info = {}
            
            # Email addresses
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            if emails:
                key_info['emails'] = list(set(emails))
            
            # Phone numbers
            phones = re.findall(r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', text)
            if phones:
                key_info['phone_numbers'] = [f"({area}){exchange}-{number}" for area, exchange, number in phones]
            
            # Dates
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
            
            # Potential names
            potential_names = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', text)
            if potential_names:
                key_info['potential_names'] = list(set(potential_names))
            
            return key_info
            
        except Exception as e:
            logger.error(f"Key information extraction error: {str(e)}")
            return {}
    
    async def _detect_language(self, text: str) -> str:
        """Detect the language of the text"""
        try:
            sample_text = text[:1000] if len(text) > 1000 else text
            language = detect(sample_text)
            return language
        except Exception:
            return 'en'
    
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
    
    def _empty_analysis_result(self, error: Optional[str] = None) -> Dict[str, Any]:
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
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
