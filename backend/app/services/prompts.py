"""
IntelliDoc AI - Prompt Engineering Configuration
===============================================

This module contains all the prompts used for AI-powered document analysis.
Prompts are organized by functionality and can be easily customized for different use cases.

Features:
- Document classification prompts
- Entity extraction prompts  
- Sentiment analysis prompts
- Summarization prompts
- Multi-language support prompts
- Custom task prompts

Usage:
    from app.services.prompts import DocumentPrompts
    
    prompts = DocumentPrompts()
    classification_prompt = prompts.get_classification_prompt(text)
"""

from typing import Dict, List, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)

class DocumentPrompts:
    """
    Centralized prompt management for IntelliDoc AI
    """
    
    def __init__(self, language: str = "en"):
        self.language = language
        self.version = "1.0.0"
        
    # =============================================================================
    # DOCUMENT CLASSIFICATION PROMPTS
    # =============================================================================
    
    def get_classification_system_prompt(self) -> str:
        """System prompt for document classification"""
        return """You are an expert document classifier specializing in business and legal documents. 

Your task is to analyze documents and classify them into one of these categories:

📋 DOCUMENT TYPES:
• invoice - Bills, payment receipts, invoices, billing statements
• contract - Legal agreements, contracts, terms of service, NDAs
• report - Business reports, analysis documents, research findings, assessments
• letter - Personal/business correspondence, memos, communications
• resume - CVs, job applications, professional profiles, portfolios
• legal - Legal documents, court papers, legal briefs, compliance documents
• academic - Research papers, studies, academic content, theses
• technical - Technical documentation, specifications, manuals, guides
• form - Application forms, surveys, questionnaires, templates
• financial - Financial statements, balance sheets, tax documents
• unknown - Documents that don't fit the above categories

🎯 ANALYSIS CRITERIA:
• Document structure and layout patterns
• Key terminology and vocabulary used
• Purpose and intent of the document
• Target audience and formal level
• Industry-specific language and concepts

📤 RESPONSE FORMAT:
Respond with ONLY a JSON object in this exact format:
{
    "type": "document_category",
    "confidence": 0.95,
    "reasoning": "Brief explanation of classification decision",
    "secondary_type": "alternative_category_if_applicable",
    "key_indicators": ["term1", "term2", "term3"]
}

🔍 QUALITY REQUIREMENTS:
• Confidence should reflect actual certainty (0.0-1.0)
• Reasoning should be specific and evidence-based
• Include 2-5 key indicators that influenced the decision
• Be conservative with high confidence scores (>0.9)"""

    def get_classification_prompt(self, text: str, max_length: int = 2000) -> str:
        """Generate classification prompt for document text"""
        # Truncate text if too long
        sample_text = text[:max_length] if len(text) > max_length else text
        
        prompt = f"""📄 DOCUMENT TO CLASSIFY:

{sample_text}

---

🔍 CLASSIFICATION TASK:
Analyze the above document and determine its category. Consider:
1. Document purpose and function
2. Language patterns and terminology
3. Structure and formatting clues
4. Target audience and context

Provide classification with confidence score and reasoning."""
        
        return prompt
    
    # =============================================================================
    # ENTITY EXTRACTION PROMPTS
    # =============================================================================
    
    def get_entity_extraction_system_prompt(self) -> str:
        """System prompt for named entity recognition"""
        return """You are an expert in Named Entity Recognition (NER) specializing in business and legal documents.

Your task is to identify and extract important entities from text.

🏷️ ENTITY CATEGORIES:
• PERSON - Full names of individuals (e.g., "John Smith", "Dr. Sarah Johnson")
• ORG - Organizations, companies, institutions (e.g., "Microsoft Corp", "Harvard University")
• LOC - Locations, addresses, places (e.g., "New York", "123 Main Street")
• DATE - Dates and times (e.g., "January 15, 2024", "Q4 2023")
• MONEY - Monetary amounts (e.g., "$1,000", "€500.50")
• PHONE - Phone numbers (e.g., "+1-555-123-4567")
• EMAIL - Email addresses (e.g., "contact@company.com")
• URL - Web addresses (e.g., "https://example.com")
• ID - Identification numbers, codes (e.g., "INV-2024-001", "SSN: 123-45-6789")
• MISC - Other important terms specific to the document type

🎯 EXTRACTION CRITERIA:
• Focus on entities that are contextually important
• Include full entity text (complete names, full addresses)
• Avoid extracting common words or partial matches
• Prioritize entities that appear multiple times or in important positions
• Consider document type when determining importance

📤 RESPONSE FORMAT:
Respond with ONLY a JSON array of entities in this exact format:
[
    {
        "text": "entity_text_as_it_appears",
        "label": "ENTITY_CATEGORY",
        "confidence": 0.95,
        "context": "surrounding_context_if_helpful"
    }
]

🔍 QUALITY REQUIREMENTS:
• Maximum 20 entities to avoid noise
• Confidence should reflect extraction certainty
• Include context for ambiguous entities
• Ensure entity text exactly matches document text"""

    def get_entity_extraction_prompt(self, text: str, max_length: int = 1500) -> str:
        """Generate entity extraction prompt for document text"""
        sample_text = text[:max_length] if len(text) > max_length else text
        
        prompt = f"""📄 DOCUMENT FOR ENTITY EXTRACTION:

{sample_text}

---

🔍 EXTRACTION TASK:
Extract all important named entities from the above text. Focus on:
1. People, organizations, and places
2. Dates, amounts, and contact information
3. Important identifiers and codes
4. Context-specific terms and references

Provide entities with their categories and confidence scores."""
        
        return prompt
    
    # =============================================================================
    # SENTIMENT ANALYSIS PROMPTS
    # =============================================================================
    
    def get_sentiment_system_prompt(self) -> str:
        """System prompt for sentiment analysis"""
        return """You are an expert in sentiment analysis specializing in business and formal documents.

Your task is to analyze the overall emotional tone and sentiment of documents.

😊 SENTIMENT CATEGORIES:
• positive - Optimistic, favorable, encouraging, satisfied, enthusiastic
• negative - Critical, unfavorable, concerned, dissatisfied, pessimistic  
• neutral - Objective, factual, balanced, professional, informational
• mixed - Contains both positive and negative elements

🎯 ANALYSIS CRITERIA:
• Overall emotional tone and attitude
• Word choice and language intensity
• Context and purpose of communication
• Presence of emotional indicators
• Professional vs. personal tone
• Urgency and importance markers

📊 CONFIDENCE SCORING:
• 0.9-1.0: Very clear sentiment indicators
• 0.7-0.9: Strong but some ambiguity
• 0.5-0.7: Moderate confidence
• 0.3-0.5: Weak or conflicting signals
• 0.0-0.3: Very unclear or neutral

📤 RESPONSE FORMAT:
Respond with ONLY a JSON object in this exact format:
{
    "sentiment": "positive|negative|neutral|mixed",
    "confidence": 0.85,
    "reasoning": "Explanation of sentiment determination",
    "key_phrases": ["phrase1", "phrase2", "phrase3"],
    "intensity": "low|medium|high",
    "subjectivity": 0.75
}

🔍 SPECIAL CONSIDERATIONS:
• Legal documents tend to be neutral by design
• Marketing materials lean positive
• Complaint documents are typically negative
• Financial reports are usually neutral/factual"""

    def get_sentiment_prompt(self, text: str, max_length: int = 1000) -> str:
        """Generate sentiment analysis prompt for document text"""
        sample_text = text[:max_length] if len(text) > max_length else text
        
        prompt = f"""📄 DOCUMENT FOR SENTIMENT ANALYSIS:

{sample_text}

---

🔍 SENTIMENT ANALYSIS TASK:
Analyze the emotional tone and sentiment of the above text. Consider:
1. Word choice and emotional language
2. Overall attitude and perspective
3. Professional vs. personal tone
4. Context and document purpose

Determine sentiment category with confidence and supporting evidence."""
        
        return prompt
    
    # =============================================================================
    # SUMMARIZATION PROMPTS
    # =============================================================================
    
    def get_summarization_system_prompt(self) -> str:
        """System prompt for document summarization"""
        return """You are an expert document summarizer specializing in creating concise, accurate summaries.

Your task is to create clear, informative summaries that capture the essential information.

📝 SUMMARIZATION PRINCIPLES:
• Focus on main ideas and key information
• Maintain original meaning and context
• Use clear, professional language
• Include important details like dates, amounts, names
• Preserve critical action items or decisions
• Maintain logical flow and structure

🎯 SUMMARY TYPES BY DOCUMENT:
• Reports: Key findings, conclusions, recommendations
• Contracts: Parties, terms, obligations, dates
• Invoices: Amounts, due dates, services/products
• Letters: Purpose, main message, action items
• Legal: Key provisions, requirements, deadlines
• Academic: Research question, methodology, findings

📏 LENGTH GUIDELINES:
• Short documents (<500 words): 2-3 sentences
• Medium documents (500-2000 words): 1 paragraph (50-100 words)
• Long documents (>2000 words): 2-3 paragraphs (100-200 words)

📤 RESPONSE FORMAT:
Provide ONLY the summary text without additional formatting or explanations.

🔍 QUALITY REQUIREMENTS:
• Accurate representation of content
• No information not present in original
• Professional tone appropriate to document type
• Include specific details when important
• Avoid generic or vague statements"""

    def get_summarization_prompt(self, text: str, max_length: int = 3000) -> str:
        """Generate summarization prompt for document text"""
        sample_text = text[:max_length] if len(text) > max_length else text
        word_count = len(text.split())
        
        # Determine target summary length based on input length
        if word_count < 100:
            target_length = "1-2 sentences"
        elif word_count < 500:
            target_length = "2-3 sentences"
        elif word_count < 1500:
            target_length = "1 paragraph (50-80 words)"
        else:
            target_length = "2-3 paragraphs (100-150 words)"
        
        prompt = f"""📄 DOCUMENT TO SUMMARIZE:

{sample_text}

---

🔍 SUMMARIZATION TASK:
Create a comprehensive summary of the above document. Your summary should:
1. Capture the main purpose and key information
2. Include important specifics (dates, amounts, names, etc.)
3. Maintain the professional tone of the original
4. Be approximately {target_length}

Focus on what a reader needs to know to understand the document's content and significance."""
        
        return prompt
    
    # =============================================================================
    # SPECIALIZED TASK PROMPTS
    # =============================================================================
    
    def get_key_information_extraction_prompt(self, text: str, info_type: str = "general") -> str:
        """Generate prompt for extracting specific types of key information"""
        
        info_types = {
            "financial": {
                "focus": "amounts, dates, payment terms, account numbers, transaction details",
                "examples": "total amounts, due dates, payment methods, account information"
            },
            "legal": {
                "focus": "parties, obligations, deadlines, legal references, jurisdiction",
                "examples": "contracting parties, key obligations, important dates, legal citations"
            },
            "contact": {
                "focus": "names, addresses, phone numbers, email addresses, company information",
                "examples": "contact persons, business addresses, communication details"
            },
            "general": {
                "focus": "key facts, important dates, significant amounts, main parties",
                "examples": "essential information that someone would need to reference later"
            }
        }
        
        info_config = info_types.get(info_type, info_types["general"])
        
        system_prompt = f"""Extract key {info_type} information from the document.

Focus on: {info_config['focus']}
Examples: {info_config['examples']}

Return a JSON object with relevant fields based on what you find."""
        
        prompt = f"""📄 DOCUMENT:

{text[:2000]}

---

🔍 KEY INFORMATION EXTRACTION:
Extract {info_type} information focusing on {info_config['focus']}.

Provide structured data in JSON format with appropriate field names."""
        
        return prompt
    
    def get_question_answering_prompt(self, text: str, question: str) -> str:
        """Generate prompt for answering questions about document content"""
        
        system_prompt = """You are a document analysis expert. Answer questions about document content accurately and concisely.

GUIDELINES:
• Only use information present in the document
• If information is not available, state "Information not found in document"
• Provide specific quotes or references when possible
• Be precise and factual in your responses"""
        
        prompt = f"""📄 DOCUMENT:

{text[:2500]}

---

❓ QUESTION: {question}

🔍 TASK:
Answer the question based solely on the information provided in the document above. 
If the answer is not explicitly stated in the document, indicate that the information is not available."""
        
        return prompt
    
    def get_document_comparison_prompt(self, doc1: str, doc2: str, comparison_type: str = "general") -> str:
        """Generate prompt for comparing two documents"""
        
        comparison_types = {
            "differences": "key differences and variations",
            "similarities": "common elements and shared content", 
            "changes": "modifications and updates between versions",
            "general": "similarities, differences, and notable variations"
        }
        
        focus = comparison_types.get(comparison_type, comparison_types["general"])
        
        prompt = f"""📄 DOCUMENT 1:

{doc1[:1500]}

📄 DOCUMENT 2:

{doc2[:1500]}

---

🔍 COMPARISON TASK:
Compare these two documents and identify {focus}.

Provide a structured analysis highlighting:
1. Key similarities
2. Important differences  
3. Notable changes or variations
4. Overall relationship between documents"""
        
        return prompt
    
    # =============================================================================
    # MULTI-LANGUAGE SUPPORT
    # =============================================================================
    
    def get_language_detection_prompt(self, text: str) -> str:
        """Generate prompt for language detection"""
        sample_text = text[:500] if len(text) > 500 else text
        
        prompt = f"""Identify the primary language of this text:

{sample_text}

Respond with only the ISO 639-1 language code (e.g., 'en', 'es', 'fr', 'de', 'it', 'pt')."""
        
        return prompt
    
    def get_translation_prompt(self, text: str, target_language: str) -> str:
        """Generate prompt for document translation"""
        
        language_names = {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese'
        }
        
        target_lang_name = language_names.get(target_language, target_language)
        
        prompt = f"""Translate the following document content to {target_lang_name}.

GUIDELINES:
• Maintain professional tone and formatting
• Preserve technical terms and proper names
• Keep document structure and meaning intact
• Use appropriate business/formal language

📄 DOCUMENT TO TRANSLATE:

{text[:2000]}

---

Provide the translation in {target_lang_name}:"""
        
        return prompt
    
    # =============================================================================
    # PROMPT CUSTOMIZATION AND UTILITIES
    # =============================================================================
    
    def customize_prompt(self, base_prompt: str, customizations: Dict[str, Any]) -> str:
        """Apply customizations to a base prompt"""
        
        custom_prompt = base_prompt
        
        # Apply variable substitutions
        if 'variables' in customizations:
            for var, value in customizations['variables'].items():
                custom_prompt = custom_prompt.replace(f"{{{var}}}", str(value))
        
        # Add custom instructions
        if 'additional_instructions' in customizations:
            custom_prompt += f"\n\nADDITIONAL INSTRUCTIONS:\n{customizations['additional_instructions']}"
        
        # Modify response format
        if 'response_format' in customizations:
            custom_prompt += f"\n\nRESPONSE FORMAT:\n{customizations['response_format']}"
        
        return custom_prompt
    
    def get_prompt_metadata(self, prompt_type: str) -> Dict[str, Any]:
        """Get metadata about a specific prompt type"""
        
        metadata = {
            "classification": {
                "description": "Classifies documents into predefined categories",
                "input_requirements": ["document_text"],
                "output_format": "JSON with type, confidence, reasoning",
                "max_input_length": 2000,
                "typical_response_time": "2-5 seconds"
            },
            "entity_extraction": {
                "description": "Extracts named entities from document text",
                "input_requirements": ["document_text"],
                "output_format": "JSON array of entities with labels",
                "max_input_length": 1500,
                "typical_response_time": "3-7 seconds"
            },
            "sentiment": {
                "description": "Analyzes emotional tone and sentiment",
                "input_requirements": ["document_text"],
                "output_format": "JSON with sentiment, confidence, reasoning",
                "max_input_length": 1000,
                "typical_response_time": "2-4 seconds"
            },
            "summarization": {
                "description": "Creates concise summaries of document content",
                "input_requirements": ["document_text"],
                "output_format": "Plain text summary",
                "max_input_length": 3000,
                "typical_response_time": "5-10 seconds"
            }
        }
        
        return metadata.get(prompt_type, {})
    
    def validate_prompt_input(self, prompt_type: str, input_text: str) -> Dict[str, Any]:
        """Validate input for a specific prompt type"""
        
        metadata = self.get_prompt_metadata(prompt_type)
        max_length = metadata.get("max_input_length", 2000)
        
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        # Check text length
        if len(input_text) == 0:
            validation_result["valid"] = False
            validation_result["errors"].append("Input text is empty")
        
        if len(input_text) > max_length:
            validation_result["warnings"].append(f"Input text ({len(input_text)} chars) exceeds recommended length ({max_length} chars). Text will be truncated.")
        
        # Check for very short text
        if len(input_text) < 50:
            validation_result["warnings"].append("Input text is very short. Results may be limited.")
        
        # Check for non-text content indicators
        if "�" in input_text:
            validation_result["warnings"].append("Input contains non-standard characters that may affect analysis.")
        
        return validation_result
    
    # =============================================================================
    # QUALITY CONTROL AND TESTING
    # =============================================================================
    

    
    def log_prompt_usage(self, prompt_type: str, input_length: int, response_time: Optional[float] = None):
        """Log prompt usage for monitoring and optimization"""
        
        log_data = {
            "prompt_type": prompt_type,
            "input_length": input_length,
            "timestamp": "auto-generated",
            "version": self.version
        }
        
        if response_time:
            log_data["response_time"] = response_time
        
        logger.info(f"Prompt usage: {json.dumps(log_data)}")

# =============================================================================
# PROMPT TEMPLATES FOR SPECIFIC DOCUMENT TYPES
# =============================================================================

class SpecializedPrompts:
    """Specialized prompts for specific document types"""
    
    @staticmethod
    def get_invoice_analysis_prompt(text: str) -> str:
        """Specialized prompt for invoice analysis"""
        return f"""
        Analyze this invoice and extract key information:
        
        📄 INVOICE DOCUMENT:
        {text[:2000]}
        
        🔍 EXTRACT:
        • Invoice number and date
        • Vendor and customer information
        • Line items with quantities and prices
        • Total amount and tax information
        • Payment terms and due date
        
        Return as structured JSON with invoice-specific fields.
        """
    
    @staticmethod
    def get_contract_analysis_prompt(text: str) -> str:
        """Specialized prompt for contract analysis"""
        return f"""
        Analyze this contract and identify key elements:
        
        📄 CONTRACT DOCUMENT:
        {text[:2500]}
        
        🔍 EXTRACT:
        • Contracting parties
        • Contract type and purpose
        • Key obligations and responsibilities
        • Important dates and deadlines
        • Financial terms and conditions
        • Termination clauses
        
        Return as structured JSON with contract-specific fields.
        """
    
    @staticmethod
    def get_resume_analysis_prompt(text: str) -> str:
        """Specialized prompt for resume/CV analysis"""
        return f"""
        Analyze this resume/CV and extract professional information:
        
        📄 RESUME/CV DOCUMENT:
        {text[:2000]}
        
        🔍 EXTRACT:
        • Personal information (name, contact)
        • Work experience and positions
        • Education and qualifications
        • Skills and competencies
        • Certifications and achievements
        
        Return as structured JSON with resume-specific fields.
        """


