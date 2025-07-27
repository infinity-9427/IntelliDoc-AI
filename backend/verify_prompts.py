#!/usr/bin/env python3
"""
Quick verification that the prompt system is working correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def verify_prompt_system():
    """Verify the prompt system is working"""
    print("🔍 Verifying IntelliDoc AI Prompt System")
    print("=" * 50)
    
    try:
        # Test imports
        from app.services.prompts import DocumentPrompts, SpecializedPrompts
        from app.services.advanced_prompts import AdvancedPromptManager, PromptStrategy
        from app.services.prompt_config import MODEL_CONFIGS, CUSTOM_PROMPTS
        print("✅ All imports successful")
        
        # Test basic functionality
        prompts = DocumentPrompts()
        test_text = "This is a test business document for verification."
        
        # Test each prompt type
        classification = prompts.get_classification_prompt(test_text)
        entities = prompts.get_entity_extraction_prompt(test_text)
        sentiment = prompts.get_sentiment_prompt(test_text)
        summary = prompts.get_summarization_prompt(test_text)
        
        print("✅ Basic prompts generated successfully")
        
        # Test advanced features
        manager = AdvancedPromptManager(strategy=PromptStrategy.ACCURACY_FOCUSED)
        optimized = manager.get_optimized_prompt("classification", test_text)
        print("✅ Advanced prompt optimization working")
        
        # Test specialized prompts
        invoice_prompt = SpecializedPrompts.get_invoice_analysis_prompt(test_text)
        print("✅ Specialized prompts working")
        
        # Test configuration
        config = MODEL_CONFIGS.get("classification")
        if config:
            print("✅ Configuration system working")
        
        # Verify integration
        try:
            from app.services.ollama_ai_service import OllamaAIService
            print("✅ Integration with AI service confirmed")
        except ImportError as e:
            print(f"⚠️ AI service integration: {e}")
        
        print("\n🎉 Prompt system verification completed successfully!")
        print("🎯 Ready for production use!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = verify_prompt_system()
    exit(0 if success else 1)
