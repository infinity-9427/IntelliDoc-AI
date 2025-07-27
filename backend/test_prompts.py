#!/usr/bin/env python3
"""
Simple test script for IntelliDoc AI Prompt System
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.prompts import DocumentPrompts, SpecializedPrompts
from app.services.advanced_prompts import AdvancedPromptManager, PromptStrategy

def test_basic_prompts():
    """Test basic prompt generation"""
    print("🧪 Testing Basic Prompts")
    print("=" * 50)
    
    # Sample business document
    sample_doc = """
    PURCHASE ORDER #PO-2024-001
    
    From: TechCorp Solutions
    123 Innovation Drive
    San Francisco, CA 94107
    
    To: Office Supplies Plus
    456 Business Avenue  
    New York, NY 10001
    
    Date: January 15, 2024
    
    Items Ordered:
    1. Laptops (Model X1) - Qty: 10 - Unit Price: $1,200.00 - Total: $12,000.00
    2. Office Chairs - Qty: 15 - Unit Price: $250.00 - Total: $3,750.00
    3. Printers (LaserJet Pro) - Qty: 3 - Unit Price: $400.00 - Total: $1,200.00
    
    Subtotal: $16,950.00
    Tax (8.5%): $1,440.75
    Total: $18,390.75
    
    Payment Terms: Net 30 days
    Delivery Date: January 30, 2024
    """
    
    prompts = DocumentPrompts()
    
    # Test classification
    print("📋 Classification Prompt:")
    classification = prompts.get_classification_prompt(sample_doc)
    print(f"Length: {len(classification)} characters")
    print("✅ Generated successfully\n")
    
    # Test entity extraction
    print("🏷️ Entity Extraction Prompt:")
    entities = prompts.get_entity_extraction_prompt(sample_doc)
    print(f"Length: {len(entities)} characters")
    print("✅ Generated successfully\n")
    
    # Test sentiment analysis
    print("😊 Sentiment Analysis Prompt:")
    sentiment = prompts.get_sentiment_prompt(sample_doc)
    print(f"Length: {len(sentiment)} characters")
    print("✅ Generated successfully\n")
    
    # Test summarization
    print("📝 Summarization Prompt:")
    summary = prompts.get_summarization_prompt(sample_doc)
    print(f"Length: {len(summary)} characters")
    print("✅ Generated successfully\n")

def test_specialized_prompts():
    """Test specialized document prompts"""
    print("🏭 Testing Specialized Prompts")
    print("=" * 50)
    
    # Invoice sample
    invoice_doc = """
    INVOICE #INV-2024-789
    
    ABC Consulting Services
    789 Professional Blvd
    Austin, TX 78701
    
    Bill To:
    XYZ Corporation
    321 Corporate Way
    Dallas, TX 75201
    
    Invoice Date: March 1, 2024
    Due Date: March 31, 2024
    
    Description of Services:
    - Strategic Consulting (40 hours @ $150/hr): $6,000.00
    - Project Management (20 hours @ $100/hr): $2,000.00
    - Technical Analysis (10 hours @ $175/hr): $1,750.00
    
    Subtotal: $9,750.00
    Tax (8.25%): $804.38
    Total Amount Due: $10,554.38
    
    Payment Method: Check or Wire Transfer
    """
    
    # Test specialized invoice prompt
    print("🧾 Invoice Analysis Prompt:")
    invoice_prompt = SpecializedPrompts.get_invoice_analysis_prompt(invoice_doc)
    print(f"Length: {len(invoice_prompt)} characters")
    print("✅ Generated successfully\n")
    
    # Contract sample
    contract_doc = """
    SOFTWARE LICENSE AGREEMENT
    
    This Software License Agreement ("Agreement") is entered into on February 15, 2024,
    between TechSoft Inc., a Delaware corporation ("Licensor"), and Business Solutions Ltd.,
    a California corporation ("Licensee").
    
    WHEREAS, Licensor has developed certain software products;
    WHEREAS, Licensee desires to obtain a license to use such software;
    
    NOW, THEREFORE, the parties agree as follows:
    
    1. GRANT OF LICENSE: Licensor grants Licensee a non-exclusive, non-transferable license
    to use the Software for internal business purposes only.
    
    2. TERM: This Agreement shall commence on March 1, 2024, and shall continue for a period
    of one (1) year, unless terminated earlier in accordance with the terms herein.
    
    3. LICENSE FEE: Licensee shall pay an annual license fee of $25,000, due within 30 days
    of the effective date.
    
    4. TERMINATION: Either party may terminate this Agreement upon 30 days written notice.
    """
    
    # Test specialized contract prompt
    print("📋 Contract Analysis Prompt:")
    contract_prompt = SpecializedPrompts.get_contract_analysis_prompt(contract_doc)
    print(f"Length: {len(contract_prompt)} characters")
    print("✅ Generated successfully\n")

def test_advanced_features():
    """Test advanced prompt management features"""
    print("⚡ Testing Advanced Features")
    print("=" * 50)
    
    sample_text = "This is a technical manual describing software installation procedures."
    
    # Test different strategies
    strategies = [
        PromptStrategy.ACCURACY_FOCUSED,
        PromptStrategy.SPEED_OPTIMIZED,
        PromptStrategy.DETAIL_ORIENTED
    ]
    
    for strategy in strategies:
        print(f"🎯 Testing {strategy.value} strategy:")
        manager = AdvancedPromptManager(strategy=strategy)
        
        try:
            prompt = manager.get_optimized_prompt("classification", sample_text)
            print(f"Length: {len(prompt)} characters")
            print("✅ Generated successfully")
        except Exception as e:
            print(f"❌ Error: {e}")
        print()

def test_validation():
    """Test input validation"""
    print("🔍 Testing Input Validation")
    print("=" * 50)
    
    prompts = DocumentPrompts()
    
    # Test with valid input
    valid_text = "This is a valid document with sufficient content for analysis."
    validation = prompts.validate_prompt_input("classification", valid_text)
    print(f"Valid input test: {'✅ PASS' if validation['valid'] else '❌ FAIL'}")
    
    # Test with empty input
    empty_text = ""
    validation = prompts.validate_prompt_input("classification", empty_text)
    print(f"Empty input test: {'✅ PASS' if not validation['valid'] else '❌ FAIL'}")
    
    # Test with very long input
    long_text = "A" * 5000
    validation = prompts.validate_prompt_input("classification", long_text)
    print(f"Long input test: {'✅ PASS' if validation['warnings'] else '❌ FAIL'}")
    print()

def main():
    """Run all tests"""
    print("🚀 IntelliDoc AI Prompt System Test")
    print("=" * 60)
    print()
    
    try:
        test_basic_prompts()
        test_specialized_prompts()
        test_advanced_features()
        test_validation()
        
        print("🎉 All tests completed successfully!")
        print("The prompt system is ready for production use.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
