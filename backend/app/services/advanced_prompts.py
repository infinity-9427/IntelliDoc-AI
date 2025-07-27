"""
Advanced Prompt Engineering Configuration for IntelliDoc AI
==========================================================

This module provides advanced prompt engineering capabilities including:
- Dynamic prompt generation based on document type
- Multi-language prompt templates
- A/B testing for prompt optimization
- Custom prompt chains for complex analysis
- Performance monitoring and optimization

Usage:
    from app.services.advanced_prompts import AdvancedPromptManager
    
    prompt_manager = AdvancedPromptManager()
    prompt = prompt_manager.get_optimized_prompt("classification", document_text, document_type="invoice")
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from .prompts import DocumentPrompts, SpecializedPrompts

logger = logging.getLogger(__name__)

class PromptStrategy(Enum):
    """Prompt strategy types for different use cases"""
    ACCURACY_FOCUSED = "accuracy"
    SPEED_OPTIMIZED = "speed"
    DETAIL_ORIENTED = "detail"
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"

@dataclass
class PromptPerformance:
    """Data class to track prompt performance metrics"""
    prompt_id: str
    response_time: float
    accuracy_score: float
    user_satisfaction: float
    error_rate: float
    usage_count: int
    last_updated: datetime

class AdvancedPromptManager:
    """
    Advanced prompt management with optimization and testing capabilities
    """
    
    def __init__(self, strategy: PromptStrategy = PromptStrategy.ACCURACY_FOCUSED):
        self.base_prompts = DocumentPrompts()
        self.specialized_prompts = SpecializedPrompts()
        self.strategy = strategy
        self.performance_data: Dict[str, PromptPerformance] = {}
        self.custom_templates: Dict[str, Any] = {}
        self.prompt_chains: Dict[str, Any] = {}
        
        # Language-specific prompt variations
        self.language_prompts = {
            'en': DocumentPrompts('en'),
            'es': DocumentPrompts('es'), 
            'fr': DocumentPrompts('fr'),
            'de': DocumentPrompts('de'),
            'it': DocumentPrompts('it'),
            'pt': DocumentPrompts('pt')
        }
    
    # =============================================================================
    # DYNAMIC PROMPT GENERATION
    # =============================================================================
    
    def get_optimized_prompt(self, 
                           prompt_type: str, 
                           text: str, 
                           document_type: Optional[str] = None,
                           context: Optional[Dict[str, Any]] = None) -> str:
        """
        Get optimized prompt based on document type and context
        """
        try:
            # Validate input
            validation = self.base_prompts.validate_prompt_input(prompt_type, text)
            if not validation["valid"]:
                logger.warning(f"Invalid prompt input: {validation['errors']}")
            
            # Select appropriate prompt template based on document type
            if document_type and hasattr(self.specialized_prompts, f"get_{document_type}_analysis_prompt"):
                method = getattr(self.specialized_prompts, f"get_{document_type}_analysis_prompt")
                return method(text)
            
            # Apply strategy-based optimizations
            if self.strategy == PromptStrategy.SPEED_OPTIMIZED:
                return self._get_speed_optimized_prompt(prompt_type, text)
            elif self.strategy == PromptStrategy.DETAIL_ORIENTED:
                return self._get_detailed_prompt(prompt_type, text)
            elif self.strategy == PromptStrategy.CONSERVATIVE:
                return self._get_conservative_prompt(prompt_type, text)
            else:
                return self._get_standard_prompt(prompt_type, text, context)
                
        except Exception as e:
            logger.error(f"Error generating optimized prompt: {str(e)}")
            return self._get_fallback_prompt(prompt_type, text)
    
    def get_multi_language_prompt(self, 
                                prompt_type: str, 
                                text: str, 
                                target_language: str = "en") -> str:
        """
        Get prompt in specified language
        """
        try:
            if target_language in self.language_prompts:
                prompts_manager = self.language_prompts[target_language]
                method_name = f"get_{prompt_type}_prompt"
                
                if hasattr(prompts_manager, method_name):
                    method = getattr(prompts_manager, method_name)
                    return method(text)
            
            # Fallback to English
            return self._get_standard_prompt(prompt_type, text)
            
        except Exception as e:
            logger.error(f"Error generating multi-language prompt: {str(e)}")
            return self._get_standard_prompt(prompt_type, text)
    
    def create_prompt_chain(self, 
                          chain_name: str, 
                          steps: List[Dict[str, Any]]) -> str:
        """
        Create a chain of prompts for complex analysis
        """
        try:
            chain_id = self._generate_chain_id(chain_name, steps)
            
            chain_prompt = f"# {chain_name.upper()} ANALYSIS CHAIN\\n\\n"
            
            for i, step in enumerate(steps, 1):
                step_type = step.get('type', 'analysis')
                step_description = step.get('description', f'Step {i}')
                
                chain_prompt += f"## STEP {i}: {step_description}\\n"
                
                if step_type == 'classification':
                    chain_prompt += self.base_prompts.get_classification_system_prompt()
                elif step_type == 'entity_extraction':
                    chain_prompt += self.base_prompts.get_entity_extraction_system_prompt()
                elif step_type == 'sentiment':
                    chain_prompt += self.base_prompts.get_sentiment_system_prompt()
                elif step_type == 'summarization':
                    chain_prompt += self.base_prompts.get_summarization_system_prompt()
                
                chain_prompt += "\\n\\n"
            
            # Store chain for reuse
            self.prompt_chains[chain_id] = {
                'name': chain_name,
                'steps': steps,
                'prompt': chain_prompt,
                'created': datetime.now()
            }
            
            return chain_prompt
            
        except Exception as e:
            logger.error(f"Error creating prompt chain: {str(e)}")
            return ""
    
    # =============================================================================
    # STRATEGY-BASED PROMPT OPTIMIZATION
    # =============================================================================
    
    def _get_speed_optimized_prompt(self, prompt_type: str, text: str) -> str:
        """Generate speed-optimized prompts with shorter instructions"""
        
        speed_prompts = {
            'classification': f"""Classify this document type quickly:

{text[:1000]}

Categories: invoice, contract, report, letter, resume, legal, academic, technical, unknown
Respond with JSON: {{"type": "category", "confidence": 0.9}}""",
            
            'entity_extraction': f"""Extract key entities:

{text[:800]}

Find: names, organizations, dates, amounts, emails, phones
JSON format: [{{"text": "entity", "label": "TYPE"}}]""",
            
            'sentiment': f"""Quick sentiment analysis:

{text[:600]}

Classify: positive, negative, neutral
JSON: {{"sentiment": "type", "confidence": 0.8}}""",
            
            'summarization': f"""Brief summary in 2-3 sentences:

{text[:1500]}

Focus on main points only."""
        }
        
        return speed_prompts.get(prompt_type, self._get_standard_prompt(prompt_type, text))
    
    def _get_detailed_prompt(self, prompt_type: str, text: str) -> str:
        """Generate detailed prompts for thorough analysis"""
        
        if prompt_type == 'classification':
            return f"""{self.base_prompts.get_classification_system_prompt()}

ADDITIONAL ANALYSIS REQUIREMENTS:
• Provide confidence reasoning with specific evidence
• Identify document sub-categories when applicable
• Note any unusual or unique characteristics
• Consider document quality and completeness
• Suggest alternative classifications if uncertain

{self.base_prompts.get_classification_prompt(text, max_length=3000)}

ENHANCED RESPONSE FORMAT:
{{
    "type": "primary_category",
    "confidence": 0.95,
    "reasoning": "detailed_explanation_with_evidence",
    "sub_category": "specific_subtype",
    "alternative_types": ["type1", "type2"],
    "quality_assessment": "high|medium|low",
    "unique_characteristics": ["feature1", "feature2"],
    "processing_recommendations": "suggestions_for_handling"
}}"""
        
        elif prompt_type == 'entity_extraction':
            return f"""{self.base_prompts.get_entity_extraction_system_prompt()}

ENHANCED EXTRACTION REQUIREMENTS:
• Extract entity relationships and connections
• Identify entity roles and importance levels
• Note entity disambiguation when needed
• Extract implicit entities from context
• Provide entity validation confidence

{self.base_prompts.get_entity_extraction_prompt(text, max_length=2500)}

ENHANCED RESPONSE FORMAT:
[{{
    "text": "entity_text",
    "label": "ENTITY_TYPE",
    "confidence": 0.95,
    "context": "surrounding_context",
    "role": "entity_role_in_document",
    "importance": "high|medium|low",
    "relationships": ["related_entity1", "related_entity2"],
    "disambiguation": "clarification_if_needed"
}}]"""
        
        return self._get_standard_prompt(prompt_type, text)
    
    def _get_conservative_prompt(self, prompt_type: str, text: str) -> str:
        """Generate conservative prompts with high confidence thresholds"""
        
        conservative_instructions = {
            'classification': "Only classify if you are very confident (>0.8). Use 'unknown' if uncertain.",
            'entity_extraction': "Only extract entities you are very confident about (>0.85). Focus on clear, unambiguous entities.",
            'sentiment': "Be conservative with sentiment classification. Use 'neutral' if sentiment is not clearly positive or negative.",
            'summarization': "Create conservative summaries focusing only on explicitly stated facts."
        }
        
        base_prompt = self._get_standard_prompt(prompt_type, text)
        conservative_instruction = conservative_instructions.get(prompt_type, "")
        
        return f"{base_prompt}\\n\\nCONSERVATIVE APPROACH: {conservative_instruction}"
    
    def _get_standard_prompt(self, prompt_type: str, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate standard prompts using base prompt manager"""
        
        method_map = {
            'classification': self.base_prompts.get_classification_prompt,
            'entity_extraction': self.base_prompts.get_entity_extraction_prompt,
            'sentiment': self.base_prompts.get_sentiment_prompt,
            'summarization': self.base_prompts.get_summarization_prompt
        }
        
        if prompt_type in method_map:
            return method_map[prompt_type](text)
        
        return f"Analyze this text for {prompt_type}:\\n\\n{text[:2000]}"
    
    def _get_fallback_prompt(self, prompt_type: str, text: str) -> str:
        """Generate simple fallback prompt"""
        return f"Please analyze this text for {prompt_type}:\\n\\n{text[:1000]}"
    
    # =============================================================================
    # PROMPT TESTING AND OPTIMIZATION
    # =============================================================================
    
    def run_prompt_ab_test(self, 
                          prompt_a: str, 
                          prompt_b: str, 
                          test_documents: List[str],
                          evaluation_criteria: Dict[str, float]) -> Dict[str, Any]:
        """
        Run A/B test between two prompts
        """
        try:
            results = {
                'prompt_a': {'responses': [], 'scores': []},
                'prompt_b': {'responses': [], 'scores': []},
                'winner': None,
                'confidence': 0.0
            }
            
            # This would integrate with your AI service to get actual responses
            # For now, returning test structure
            
            logger.info(f"A/B test setup for {len(test_documents)} documents")
            
            # In real implementation, you would:
            # 1. Send each test document through both prompts
            # 2. Collect responses and evaluate them
            # 3. Calculate scores based on evaluation criteria
            # 4. Determine statistical significance
            
            return results
            
        except Exception as e:
            logger.error(f"Error running A/B test: {str(e)}")
            return {'error': str(e)}
    
    def optimize_prompt_for_accuracy(self, 
                                   base_prompt: str, 
                                   test_cases: List[Dict[str, Any]]) -> str:
        """
        Optimize prompt for accuracy using test cases
        """
        try:
            # Generate prompt variations
            variations = self._generate_prompt_variations(base_prompt)
            
            best_prompt = base_prompt
            best_score = 0.0
            
            for variation in variations:
                score = self._evaluate_prompt_accuracy(variation, test_cases)
                if score > best_score:
                    best_score = score
                    best_prompt = variation
            
            logger.info(f"Optimized prompt achieved {best_score:.2f} accuracy score")
            return best_prompt
            
        except Exception as e:
            logger.error(f"Error optimizing prompt: {str(e)}")
            return base_prompt
    
    def _generate_prompt_variations(self, base_prompt: str) -> List[str]:
        """Generate variations of a base prompt for testing"""
        
        variations = [base_prompt]  # Include original
        
        # Add variations with different instruction styles
        variations.extend([
            f"Instructions: {base_prompt}",
            f"Task: {base_prompt}",
            f"Please {base_prompt.lower()}",
            f"Your goal is to {base_prompt.lower()}"
        ])
        
        # Add variations with different emphasis
        if "analyze" in base_prompt.lower():
            variations.append(base_prompt.replace("analyze", "carefully examine"))
            variations.append(base_prompt.replace("analyze", "thoroughly review"))
        
        return variations[:10]  # Limit to reasonable number
    
    def _evaluate_prompt_accuracy(self, prompt: str, test_cases: List[Dict[str, Any]]) -> float:
        """
        Evaluate prompt accuracy against test cases
        This would integrate with your actual AI service
        """
        # Placeholder evaluation logic
        # In real implementation, you would:
        # 1. Run prompt against test cases
        # 2. Compare outputs to expected results
        # 3. Calculate accuracy metrics
        
        return 0.85  # Placeholder score
    
    # =============================================================================
    # PERFORMANCE MONITORING
    # =============================================================================
    
    def track_prompt_performance(self, 
                               prompt_id: str, 
                               response_time: float,
                               accuracy_score: float = 0.0,
                               user_feedback: Optional[float] = None):
        """Track performance metrics for prompt optimization"""
        
        try:
            if prompt_id not in self.performance_data:
                self.performance_data[prompt_id] = PromptPerformance(
                    prompt_id=prompt_id,
                    response_time=response_time,
                    accuracy_score=accuracy_score,
                    user_satisfaction=user_feedback or 0.0,
                    error_rate=0.0,
                    usage_count=1,
                    last_updated=datetime.now()
                )
            else:
                perf = self.performance_data[prompt_id]
                perf.usage_count += 1
                # Update running averages
                perf.response_time = (perf.response_time + response_time) / 2
                if accuracy_score > 0:
                    perf.accuracy_score = (perf.accuracy_score + accuracy_score) / 2
                if user_feedback:
                    perf.user_satisfaction = (perf.user_satisfaction + user_feedback) / 2
                perf.last_updated = datetime.now()
            
            logger.info(f"Updated performance for prompt {prompt_id}")
            
        except Exception as e:
            logger.error(f"Error tracking prompt performance: {str(e)}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report for all tracked prompts"""
        
        try:
            report = {
                'total_prompts': len(self.performance_data),
                'average_response_time': 0.0,
                'average_accuracy': 0.0,
                'top_performing_prompts': [],
                'recommendations': []
            }
            
            if self.performance_data:
                # Calculate averages
                total_response_time = sum(p.response_time for p in self.performance_data.values())
                total_accuracy = sum(p.accuracy_score for p in self.performance_data.values())
                
                report['average_response_time'] = total_response_time / len(self.performance_data)
                report['average_accuracy'] = total_accuracy / len(self.performance_data)
                
                # Find top performers
                sorted_prompts = sorted(
                    self.performance_data.values(),
                    key=lambda p: p.accuracy_score * p.user_satisfaction,
                    reverse=True
                )
                
                report['top_performing_prompts'] = [
                    {
                        'prompt_id': p.prompt_id,
                        'accuracy': p.accuracy_score,
                        'satisfaction': p.user_satisfaction,
                        'usage_count': p.usage_count
                    }
                    for p in sorted_prompts[:5]
                ]
                
                # Generate recommendations
                if report['average_response_time'] > 10.0:
                    report['recommendations'].append("Consider using speed-optimized prompts")
                
                if report['average_accuracy'] < 0.8:
                    report['recommendations'].append("Review prompt engineering for accuracy improvements")
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {str(e)}")
            return {'error': str(e)}
    
    # =============================================================================
    # UTILITIES
    # =============================================================================
    
    def _generate_chain_id(self, name: str, steps: List[Dict[str, Any]]) -> str:
        """Generate unique ID for prompt chain"""
        content = f"{name}_{json.dumps(steps, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def export_prompt_templates(self, format: str = "json") -> Union[str, Dict[str, Any]]:
        """Export prompt templates for backup or sharing"""
        
        try:
            templates = {
                'base_prompts': {
                    'classification_system': self.base_prompts.get_classification_system_prompt(),
                    'entity_extraction_system': self.base_prompts.get_entity_extraction_system_prompt(),
                    'sentiment_system': self.base_prompts.get_sentiment_system_prompt(),
                    'summarization_system': self.base_prompts.get_summarization_system_prompt()
                },
                'custom_templates': self.custom_templates,
                'prompt_chains': self.prompt_chains,
                'performance_data': {
                    pid: {
                        'prompt_id': p.prompt_id,
                        'response_time': p.response_time,
                        'accuracy_score': p.accuracy_score,
                        'usage_count': p.usage_count
                    }
                    for pid, p in self.performance_data.items()
                },
                'metadata': {
                    'strategy': self.strategy.value,
                    'export_date': datetime.now().isoformat(),
                    'version': '1.0.0'
                }
            }
            
            if format.lower() == 'json':
                return json.dumps(templates, indent=2, default=str)
            else:
                return templates
                
        except Exception as e:
            logger.error(f"Error exporting templates: {str(e)}")
            return {}
    
    def import_prompt_templates(self, templates: Union[str, Dict[str, Any]]):
        """Import prompt templates from backup or external source"""
        
        try:
            if isinstance(templates, str):
                templates = json.loads(templates)
            
            if isinstance(templates, dict):
                custom_templates = templates.get('custom_templates')
                if custom_templates and isinstance(custom_templates, dict):
                    self.custom_templates.update(custom_templates)
                
                prompt_chains = templates.get('prompt_chains')
                if prompt_chains and isinstance(prompt_chains, dict):
                    self.prompt_chains.update(prompt_chains)
            
            logger.info("Successfully imported prompt templates")
            
        except Exception as e:
            logger.error(f"Error importing templates: {str(e)}")

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    # Example usage of advanced prompt manager
    
    manager = AdvancedPromptManager(strategy=PromptStrategy.ACCURACY_FOCUSED)
    
    # Test document
    sample_doc = """
    INVOICE #INV-2024-12345
    Date: January 15, 2024
    
    Bill To: XYZ Corporation
    Attn: John Smith
    123 Business Ave
    Suite 100
    New York, NY 10001
    
    Description          Qty    Rate      Amount
    Web Development      40hrs  $125/hr   $5,000.00
    Project Management   10hrs  $150/hr   $1,500.00
    
    Subtotal:                            $6,500.00
    Tax (8.5%):                          $552.50
    Total Amount:                        $7,052.50
    
    Payment Due: February 15, 2024
    Terms: Net 30 days
    """
    
    # Test optimized prompt generation
    print("=== OPTIMIZED CLASSIFICATION PROMPT ===")
    prompt = manager.get_optimized_prompt("classification", sample_doc, document_type="invoice")
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    
    print("\\n=== MULTI-LANGUAGE PROMPT (Spanish) ===")
    es_prompt = manager.get_multi_language_prompt("classification", sample_doc, "es")
    print(es_prompt[:300] + "..." if len(es_prompt) > 300 else es_prompt)
    
    # Test prompt chain creation
    print("\\n=== PROMPT CHAIN ===")
    chain_steps = [
        {"type": "classification", "description": "Document Type Classification"},
        {"type": "entity_extraction", "description": "Extract Key Entities"},
        {"type": "summarization", "description": "Generate Summary"}
    ]
    chain = manager.create_prompt_chain("Complete Document Analysis", chain_steps)
    print(chain[:400] + "..." if len(chain) > 400 else chain)
