"""
Prompt Configuration for IntelliDoc AI
=====================================

This configuration file contains customizable prompt templates and settings
that can be modified without changing the core code.

Configuration includes:
- Model parameters for different tasks
- Custom prompt templates
- Performance thresholds
- Language-specific variations
- Task-specific optimizations
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for model parameters"""
    temperature: float = 0.3
    top_p: float = 0.9
    max_tokens: int = 512
    timeout: float = 120.0

@dataclass 
class PromptConfig:
    """Configuration for prompt behavior"""
    max_input_length: int = 2000
    confidence_threshold: float = 0.7
    retry_attempts: int = 2
    fallback_enabled: bool = True

# =============================================================================
# MODEL CONFIGURATIONS
# =============================================================================

MODEL_CONFIGS = {
    "classification": ModelConfig(
        temperature=0.2,  # Lower for more consistent results
        top_p=0.8,
        max_tokens=256,
        timeout=60.0
    ),
    "entity_extraction": ModelConfig(
        temperature=0.1,  # Very low for precise extraction
        top_p=0.7,
        max_tokens=512,
        timeout=90.0
    ),
    "sentiment": ModelConfig(
        temperature=0.3,
        top_p=0.9,
        max_tokens=256,
        timeout=60.0
    ),
    "summarization": ModelConfig(
        temperature=0.5,  # Higher for more creative summaries
        top_p=0.9,
        max_tokens=512,
        timeout=120.0
    ),
    "translation": ModelConfig(
        temperature=0.2,
        top_p=0.8,
        max_tokens=1024,
        timeout=180.0
    )
}

# =============================================================================
# PROMPT CONFIGURATIONS
# =============================================================================

PROMPT_CONFIGS = {
    "classification": PromptConfig(
        max_input_length=2000,
        confidence_threshold=0.8,
        retry_attempts=2,
        fallback_enabled=True
    ),
    "entity_extraction": PromptConfig(
        max_input_length=1500,
        confidence_threshold=0.85,
        retry_attempts=3,
        fallback_enabled=True
    ),
    "sentiment": PromptConfig(
        max_input_length=1000,
        confidence_threshold=0.7,
        retry_attempts=2,
        fallback_enabled=True
    ),
    "summarization": PromptConfig(
        max_input_length=3000,
        confidence_threshold=0.6,
        retry_attempts=2,
        fallback_enabled=True
    )
}

# =============================================================================
# CUSTOM PROMPT TEMPLATES
# =============================================================================

CUSTOM_PROMPTS = {
    # Enhanced classification for specific industries
    "legal_classification": {
        "system": """You are a legal document classification expert specializing in law firm documents.
        
        📋 LEGAL DOCUMENT TYPES:
        • contract - Legal agreements, NDAs, service contracts
        • brief - Legal briefs, court filings, pleadings
        • opinion - Legal opinions, advisory letters, counsel letters
        • correspondence - Client letters, opposing counsel communications
        • filing - Court documents, motions, applications
        • compliance - Regulatory documents, compliance reports
        • corporate - Corporate governance, board resolutions, bylaws
        • litigation - Discovery documents, depositions, evidence
        • transactional - M&A documents, purchase agreements, leases
        • regulatory - Government filings, regulatory responses
        
        🎯 CLASSIFICATION CRITERIA:
        • Document purpose in legal context
        • Intended audience (court, client, regulator)
        • Legal procedural requirements
        • Document formality and structure
        • Legal terminology and citations
        
        📤 RESPONSE FORMAT:
        {
            "type": "document_category",
            "confidence": 0.95,
            "legal_area": "practice_area",
            "urgency": "high|medium|low",
            "client_facing": true|false,
            "court_filing": true|false
        }""",
        
        "user": """📄 LEGAL DOCUMENT TO CLASSIFY:

        {text}

        ---

        🔍 LEGAL CLASSIFICATION:
        Analyze this document within legal practice context. Consider:
        1. Document's role in legal proceedings
        2. Target audience and purpose
        3. Legal formality and requirements
        4. Practice area and specialization
        5. Urgency and time sensitivity"""
    },
    
    # Enhanced entity extraction for financial documents
    "financial_entities": {
        "system": """You are a financial document analysis expert specializing in extracting financial entities.
        
        🏷️ FINANCIAL ENTITY TYPES:
        • COMPANY - Business entities, subsidiaries, partnerships
        • PERSON - Executives, signatories, beneficial owners
        • AMOUNT - Monetary values, percentages, ratios
        • ACCOUNT - Account numbers, routing numbers, SWIFT codes
        • DATE - Transaction dates, due dates, fiscal periods
        • FINANCIAL_INSTRUMENT - Stocks, bonds, derivatives, loans
        • BANK - Financial institutions, credit unions, brokers
        • CURRENCY - Currency codes, exchange rates
        • TAX_ID - EIN, SSN, VAT numbers, tax identifiers
        • REGULATION - Financial regulations, compliance references
        • RISK_FACTOR - Risk disclosures, risk ratings
        • PERFORMANCE - Returns, yields, performance metrics
        
        🎯 EXTRACTION FOCUS:
        • Regulatory compliance identifiers
        • Material financial amounts and dates
        • Key parties and their roles
        • Financial instruments and terms
        • Risk factors and disclosures
        
        📤 RESPONSE FORMAT:
        [
            {
                "text": "entity_text",
                "label": "ENTITY_TYPE",
                "confidence": 0.95,
                "financial_significance": "high|medium|low",
                "regulatory_importance": true|false,
                "context": "surrounding_context"
            }
        ]""",
        
        "user": """📄 FINANCIAL DOCUMENT:

        {text}

        ---

        🔍 FINANCIAL ENTITY EXTRACTION:
        Extract financial entities focusing on:
        1. Material amounts and financial figures
        2. Key financial institutions and parties
        3. Important dates and deadlines
        4. Regulatory and compliance identifiers
        5. Financial instruments and products"""
    },
    
    # Specialized medical document analysis
    "medical_analysis": {
        "system": """You are a medical document analysis expert specializing in healthcare documents.
        
        📋 MEDICAL DOCUMENT TYPES:
        • clinical_note - Progress notes, consultation notes, discharge summaries
        • lab_report - Laboratory results, pathology reports, imaging reports
        • prescription - Medication orders, pharmacy records
        • insurance - Insurance claims, prior authorizations, EOBs
        • patient_record - Medical history, treatment plans, patient charts
        • research - Clinical trial documents, research protocols
        • administrative - Hospital policies, compliance documents
        • billing - Medical bills, coding documents, revenue cycle
        
        🏷️ MEDICAL ENTITIES:
        • PATIENT - Patient names, IDs, demographics
        • PROVIDER - Physicians, nurses, healthcare providers
        • CONDITION - Diagnoses, symptoms, medical conditions
        • MEDICATION - Drugs, dosages, prescriptions
        • PROCEDURE - Medical procedures, treatments, surgeries
        • LAB_VALUE - Test results, measurements, vital signs
        • DATE - Appointment dates, treatment dates, lab dates
        • FACILITY - Hospitals, clinics, medical facilities
        • INSURANCE - Insurance companies, policy numbers, claims
        • ICD_CODE - Medical coding, diagnosis codes
        
        ⚕️ COMPLIANCE CONSIDERATIONS:
        • HIPAA privacy requirements
        • PHI (Protected Health Information) identification
        • Medical terminology accuracy
        • Clinical context preservation
        
        📤 RESPONSE FORMAT:
        {
            "document_type": "medical_category",
            "entities": [...],
            "phi_detected": true|false,
            "clinical_significance": "high|medium|low",
            "compliance_notes": "privacy_considerations"
        }""",
        
        "user": """📄 MEDICAL DOCUMENT:

        {text}

        ---

        🔍 MEDICAL DOCUMENT ANALYSIS:
        Analyze this medical document considering:
        1. Clinical context and significance
        2. HIPAA and privacy requirements
        3. Medical terminology and accuracy
        4. Patient care implications
        5. Healthcare workflow integration"""
    }
}

# =============================================================================
# MULTI-LANGUAGE PROMPT VARIATIONS
# =============================================================================

LANGUAGE_VARIATIONS = {
    "es": {  # Spanish
        "classification_instruction": "Clasifica este documento en una de las siguientes categorías:",
        "entity_instruction": "Extrae las entidades nombradas importantes del texto:",
        "sentiment_instruction": "Analiza el sentimiento general del documento:",
        "summary_instruction": "Crea un resumen conciso del documento:",
        
        "document_types": {
            "invoice": "factura",
            "contract": "contrato", 
            "report": "informe",
            "letter": "carta",
            "resume": "currículum",
            "legal": "legal",
            "academic": "académico",
            "technical": "técnico"
        }
    },
    
    "fr": {  # French
        "classification_instruction": "Classifiez ce document dans l'une des catégories suivantes:",
        "entity_instruction": "Extrayez les entités nommées importantes du texte:",
        "sentiment_instruction": "Analysez le sentiment général du document:",
        "summary_instruction": "Créez un résumé concis du document:",
        
        "document_types": {
            "invoice": "facture",
            "contract": "contrat",
            "report": "rapport", 
            "letter": "lettre",
            "resume": "CV",
            "legal": "juridique",
            "academic": "académique",
            "technical": "technique"
        }
    },
    
    "de": {  # German
        "classification_instruction": "Klassifizieren Sie dieses Dokument in eine der folgenden Kategorien:",
        "entity_instruction": "Extrahieren Sie wichtige benannte Entitäten aus dem Text:",
        "sentiment_instruction": "Analysieren Sie die allgemeine Stimmung des Dokuments:",
        "summary_instruction": "Erstellen Sie eine prägnante Zusammenfassung des Dokuments:",
        
        "document_types": {
            "invoice": "Rechnung",
            "contract": "Vertrag",
            "report": "Bericht",
            "letter": "Brief", 
            "resume": "Lebenslauf",
            "legal": "rechtlich",
            "academic": "akademisch",
            "technical": "technisch"
        }
    }
}

# =============================================================================
# PERFORMANCE THRESHOLDS
# =============================================================================

PERFORMANCE_THRESHOLDS = {
    "response_time": {
        "excellent": 2.0,   # seconds
        "good": 5.0,
        "acceptable": 10.0,
        "poor": 20.0
    },
    
    "accuracy": {
        "excellent": 0.95,
        "good": 0.85,
        "acceptable": 0.75,
        "poor": 0.65
    },
    
    "confidence": {
        "high": 0.9,
        "medium": 0.7,
        "low": 0.5
    }
}

# =============================================================================
# TASK-SPECIFIC OPTIMIZATIONS
# =============================================================================

TASK_OPTIMIZATIONS = {
    "classification": {
        "speed_mode": {
            "max_input_length": 1000,
            "temperature": 0.1,
            "max_tokens": 128,
            "prompt_style": "concise"
        },
        "accuracy_mode": {
            "max_input_length": 3000,
            "temperature": 0.2,
            "max_tokens": 256,
            "prompt_style": "detailed"
        },
        "balanced_mode": {
            "max_input_length": 2000,
            "temperature": 0.3,
            "max_tokens": 192,
            "prompt_style": "standard"
        }
    },
    
    "entity_extraction": {
        "precision_mode": {
            "confidence_threshold": 0.9,
            "max_entities": 10,
            "temperature": 0.1
        },
        "recall_mode": {
            "confidence_threshold": 0.6,
            "max_entities": 30,
            "temperature": 0.2
        },
        "balanced_mode": {
            "confidence_threshold": 0.75,
            "max_entities": 20,
            "temperature": 0.15
        }
    },
    
    "summarization": {
        "brief_mode": {
            "max_summary_length": 50,
            "style": "bullet_points",
            "focus": "key_facts"
        },
        "detailed_mode": {
            "max_summary_length": 200,
            "style": "paragraph",
            "focus": "comprehensive"
        },
        "executive_mode": {
            "max_summary_length": 100,
            "style": "executive_summary",
            "focus": "decisions_and_actions"
        }
    }
}

# =============================================================================
# FALLBACK CONFIGURATIONS
# =============================================================================

FALLBACK_CONFIGS = {
    "classification": {
        "rule_based_keywords": {
            "invoice": ["invoice", "bill", "payment", "amount", "total", "due"],
            "contract": ["agreement", "contract", "terms", "conditions", "party"],
            "report": ["report", "analysis", "conclusion", "findings", "summary"],
            "letter": ["dear", "sincerely", "regards", "letter"],
            "resume": ["experience", "education", "skills", "work", "cv"]
        },
        "confidence_penalty": 0.3  # Reduce confidence for rule-based results
    },
    
    "entity_extraction": {
        "regex_patterns": {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            "date": r'\b(?:\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}[/\-]\d{1,2}[/\-]\d{1,2})\b',
            "amount": r'\$\s?[\d,]+\.?\d*|\b\d+\.\d{2}\s?(?:USD|EUR|GBP)\b'
        }
    }
}

# =============================================================================
# QUALITY CONTROL SETTINGS
# =============================================================================

QUALITY_CONTROL = {
    "validation_rules": {
        "min_text_length": 10,
        "max_text_length": 50000,
        "required_confidence": 0.5,
        "max_processing_time": 300
    },
    
    "output_validation": {
        "classification": {
            "required_fields": ["type", "confidence"],
            "valid_types": ["invoice", "contract", "report", "letter", "resume", "legal", "academic", "technical", "unknown"],
            "confidence_range": [0.0, 1.0]
        },
        "entity_extraction": {
            "required_fields": ["text", "label", "confidence"],
            "max_entities": 50,
            "min_entity_length": 2
        }
    },
    
    "error_handling": {
        "max_retries": 3,
        "retry_delay": 1.0,
        "fallback_enabled": True,
        "log_errors": True
    }
}

# =============================================================================
# MONITORING AND LOGGING
# =============================================================================

MONITORING_CONFIG = {
    "performance_tracking": {
        "track_response_times": True,
        "track_accuracy": True, 
        "track_user_feedback": True,
        "track_error_rates": True
    },
    
    "logging": {
        "log_prompts": False,  # Set to True for debugging
        "log_responses": False,
        "log_performance": True,
        "log_errors": True,
        "log_level": "INFO"
    },
    
    "alerts": {
        "slow_response_threshold": 15.0,
        "high_error_rate_threshold": 0.1,
        "low_accuracy_threshold": 0.7
    }
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_config(task_type: str, config_type: str = "default") -> Dict[str, Any]:
    """Get configuration for a specific task type"""
    
    configs = {
        "model": MODEL_CONFIGS,
        "prompt": PROMPT_CONFIGS,
        "optimization": TASK_OPTIMIZATIONS,
        "fallback": FALLBACK_CONFIGS
    }
    
    if config_type in configs and task_type in configs[config_type]:
        return configs[config_type][task_type]
    
    # Return default configuration
    return {
        "temperature": 0.3,
        "max_tokens": 512,
        "confidence_threshold": 0.7
    }

def get_language_prompt_template(language: str, prompt_type: str) -> str:
    """Get language-specific prompt template"""
    
    if language in LANGUAGE_VARIATIONS:
        lang_config = LANGUAGE_VARIATIONS[language]
        instruction_key = f"{prompt_type}_instruction"
        
        if instruction_key in lang_config:
            return lang_config[instruction_key]
    
    # Fallback to English
    return f"Analyze this document for {prompt_type}:"

def validate_task_config(task_type: str, config: Dict[str, Any]) -> bool:
    """Validate task configuration"""
    
    required_fields = {
        "classification": ["temperature", "max_tokens"],
        "entity_extraction": ["temperature", "max_tokens", "confidence_threshold"],
        "sentiment": ["temperature", "max_tokens"],
        "summarization": ["temperature", "max_tokens"]
    }
    
    if task_type in required_fields:
        return all(field in config for field in required_fields[task_type])
    
    return True

# =============================================================================
# CONFIGURATION EXPORT/IMPORT
# =============================================================================

def export_config() -> Dict[str, Any]:
    """Export current configuration for backup or sharing"""
    
    return {
        "model_configs": MODEL_CONFIGS,
        "prompt_configs": PROMPT_CONFIGS,
        "custom_prompts": CUSTOM_PROMPTS,
        "language_variations": LANGUAGE_VARIATIONS,
        "performance_thresholds": PERFORMANCE_THRESHOLDS,
        "task_optimizations": TASK_OPTIMIZATIONS,
        "fallback_configs": FALLBACK_CONFIGS,
        "quality_control": QUALITY_CONTROL,
        "monitoring_config": MONITORING_CONFIG
    }

def import_config(config_data: Dict[str, Any]) -> bool:
    """Import configuration from external source"""
    
    try:
        # Validate and update configurations
        global MODEL_CONFIGS, PROMPT_CONFIGS, CUSTOM_PROMPTS
        
        if "model_configs" in config_data:
            MODEL_CONFIGS.update(config_data["model_configs"])
        
        if "prompt_configs" in config_data:
            PROMPT_CONFIGS.update(config_data["prompt_configs"])
        
        if "custom_prompts" in config_data:
            CUSTOM_PROMPTS.update(config_data["custom_prompts"])
        
        return True
        
    except Exception as e:
        print(f"Error importing configuration: {e}")
        return False

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Example: Get configuration for different modes
    
    print("=== MODEL CONFIGURATIONS ===")
    for task, config in MODEL_CONFIGS.items():
        print(f"{task}: {config}")
    
    print("\n=== TASK OPTIMIZATIONS ===")
    classification_config = get_config("classification", "optimization")
    print(f"Classification modes: {classification_config}")
    
    print("\n=== LANGUAGE TEMPLATES ===")
    spanish_instruction = get_language_prompt_template("es", "classification")
    print(f"Spanish classification: {spanish_instruction}")
    
    print("\n=== CUSTOM PROMPTS ===")
    legal_prompt = CUSTOM_PROMPTS.get("legal_classification", {})
    if legal_prompt:
        print(f"Legal classification system prompt: {legal_prompt['system'][:200]}...")
