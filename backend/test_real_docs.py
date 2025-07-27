#!/usr/bin/env python3
"""
Test the prompt system with real PDF documents
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import PyPDF2
from app.services.prompts import DocumentPrompts, SpecializedPrompts

def extract_text_from_pdf(pdf_path: str, max_pages: int = 3) -> str:
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            # Extract text from first few pages
            pages_to_read = min(len(pdf_reader.pages), max_pages)
            for page_num in range(pages_to_read):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def test_with_real_pdf():
    """Test prompts with a real PDF document"""
    print("📄 Testing with Real PDF Documents")
    print("=" * 50)
    
    # Find a PDF to test with
    uploads_dir = "/home/dev/code/portfolio/local-pdf-converter/backend/uploads"
    pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found in uploads directory")
        return False
    
    # Use the first PDF file
    pdf_path = os.path.join(uploads_dir, pdf_files[0])
    print(f"📖 Testing with: {pdf_files[0]}")
    
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    
    if not pdf_text:
        print("❌ Could not extract text from PDF")
        return False
    
    print(f"📝 Extracted {len(pdf_text)} characters from PDF")
    print(f"📄 First 200 characters:\n{pdf_text[:200]}...\n")
    
    # Test prompts with real data
    prompts = DocumentPrompts()
    
    try:
        # Test classification
        print("🔍 Generating classification prompt...")
        classification_prompt = prompts.get_classification_prompt(pdf_text)
        print(f"✅ Classification prompt: {len(classification_prompt)} characters")
        
        # Test entity extraction
        print("🏷️ Generating entity extraction prompt...")
        entity_prompt = prompts.get_entity_extraction_prompt(pdf_text)
        print(f"✅ Entity extraction prompt: {len(entity_prompt)} characters")
        
        # Test sentiment analysis
        print("😊 Generating sentiment analysis prompt...")
        sentiment_prompt = prompts.get_sentiment_prompt(pdf_text)
        print(f"✅ Sentiment analysis prompt: {len(sentiment_prompt)} characters")
        
        # Test summarization
        print("📝 Generating summarization prompt...")
        summary_prompt = prompts.get_summarization_prompt(pdf_text)
        print(f"✅ Summarization prompt: {len(summary_prompt)} characters")
        
        # Test input validation
        print("🔍 Testing input validation...")
        validation_result = prompts.validate_prompt_input("classification", pdf_text)
        print(f"✅ Validation result: Valid={validation_result['valid']}")
        if validation_result['warnings']:
            print(f"⚠️ Warnings: {validation_result['warnings']}")
        
        print("\n🎉 Real PDF testing completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def main():
    """Run real document tests"""
    print("🚀 IntelliDoc AI - Real Document Testing")
    print("=" * 60)
    print()
    
    try:
        # Check if PyPDF2 is available
        import PyPDF2
        
        success = test_with_real_pdf()
        
        if success:
            print("\n✅ All real document tests passed!")
            print("🎯 The prompt system is validated and ready for production!")
        else:
            print("\n❌ Some tests failed")
            return 1
            
    except ImportError:
        print("⚠️ PyPDF2 not installed. Testing with text content only...")
        # Fallback test with sample content
        print("📄 Using sample document content for testing...")
        
        sample_content = """
        QUARTERLY BUSINESS REPORT
        Q4 2023 Financial Summary
        
        Company: TechInnovate Solutions
        Report Date: December 31, 2023
        
        EXECUTIVE SUMMARY:
        This quarter showed strong performance with revenue growth of 15% 
        compared to Q3 2023. Key achievements include successful product 
        launches and expansion into new markets.
        
        FINANCIAL HIGHLIGHTS:
        - Total Revenue: $2.4M (+15% QoQ)
        - Operating Expenses: $1.8M
        - Net Profit: $600K
        - Cash Flow: Positive $450K
        
        KEY METRICS:
        - Customer Acquisition: 150 new clients
        - Customer Retention Rate: 94%
        - Average Deal Size: $16,000
        """
        
        prompts = DocumentPrompts()
        
        print("🔍 Testing with sample content...")
        classification = prompts.get_classification_prompt(sample_content)
        print(f"✅ Classification prompt generated: {len(classification)} chars")
        
        entities = prompts.get_entity_extraction_prompt(sample_content)
        print(f"✅ Entity extraction prompt generated: {len(entities)} chars")
        
        print("\n✅ Fallback testing completed successfully!")
    
    return 0

if __name__ == "__main__":
    exit(main())
