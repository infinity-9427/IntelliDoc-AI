#!/bin/bash

# Cross-platform OCR setup script for IntelliDoc AI
# This script ensures Tesseract and language packs are available across different environments

set -e

echo "🔧 Setting up cross-platform OCR dependencies..."

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            echo "ubuntu"
        elif command -v dnf &> /dev/null; then
            echo "fedora"
        elif command -v yum &> /dev/null; then
            echo "rhel"
        elif command -v pacman &> /dev/null; then
            echo "arch"
        else
            echo "linux-other"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to install Tesseract based on OS
install_tesseract() {
    local os_type=$(detect_os)
    
    echo "📦 Installing Tesseract OCR for: $os_type"
    
    case $os_type in
        "ubuntu")
            sudo apt-get update
            sudo apt-get install -y \
                tesseract-ocr \
                tesseract-ocr-eng \
                tesseract-ocr-fra \
                tesseract-ocr-deu \
                tesseract-ocr-spa \
                tesseract-ocr-ita \
                libtesseract-dev \
                poppler-utils \
                libgl1-mesa-glx \
                libglib2.0-0
            ;;
        "fedora")
            sudo dnf install -y \
                tesseract \
                tesseract-langpack-eng \
                tesseract-langpack-fra \
                tesseract-langpack-deu \
                tesseract-langpack-spa \
                tesseract-langpack-ita \
                tesseract-devel \
                poppler-utils \
                mesa-libGL
            ;;
        "rhel")
            sudo yum install -y epel-release
            sudo yum install -y \
                tesseract \
                tesseract-langpack-eng \
                tesseract-langpack-fra \
                tesseract-langpack-deu \
                tesseract-langpack-spa \
                tesseract-langpack-ita \
                tesseract-devel \
                poppler-utils
            ;;
        "arch")
            sudo pacman -S --noconfirm \
                tesseract \
                tesseract-data-eng \
                tesseract-data-fra \
                tesseract-data-deu \
                tesseract-data-spa \
                tesseract-data-ita \
                poppler
            ;;
        "macos")
            if command -v brew &> /dev/null; then
                brew install tesseract
                brew install tesseract-lang
                brew install poppler
            else
                echo "❌ Homebrew not found. Please install Homebrew first: https://brew.sh"
                exit 1
            fi
            ;;
        "windows")
            echo "🪟 Windows detected. Please install:"
            echo "   1. Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki"
            echo "   2. Poppler: https://blog.alivate.com.au/poppler-windows/"
            echo "   3. Add both to your system PATH"
            echo ""
            echo "   Or use Docker for a consistent environment."
            ;;
        *)
            echo "❓ Unknown OS: $os_type"
            echo "   Please install Tesseract OCR manually or use Docker."
            ;;
    esac
}

# Function to verify Tesseract installation
verify_tesseract() {
    echo "🔍 Verifying Tesseract installation..."
    
    if command -v tesseract &> /dev/null; then
        echo "✅ Tesseract found: $(tesseract --version | head -1)"
        
        # Check available languages
        echo "📚 Available languages:"
        tesseract --list-langs 2>/dev/null | head -10
        
        # Test basic OCR
        echo "🧪 Testing OCR functionality..."
        echo "Hello World" | tesseract stdin stdout 2>/dev/null
        
        if [ $? -eq 0 ]; then
            echo "✅ Tesseract OCR is working correctly"
        else
            echo "⚠️  Tesseract OCR test failed"
        fi
    else
        echo "❌ Tesseract not found in PATH"
        return 1
    fi
}

# Function to set up Docker alternative
setup_docker_alternative() {
    echo "🐳 Setting up Docker-based OCR solution..."
    
    # Create a lightweight Dockerfile for OCR
    cat > Dockerfile.ocr << 'EOF'
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    tesseract-ocr-deu \
    tesseract-ocr-spa \
    tesseract-ocr-ita \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Tesseract data path
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

# Install Python OCR packages
RUN pip install \
    pytesseract \
    easyocr \
    opencv-python-headless \
    Pillow \
    pdf2image

WORKDIR /app
CMD ["python"]
EOF

    echo "✅ Docker OCR setup complete. Use: docker build -f Dockerfile.ocr -t ocr-engine ."
}

# Function to create environment detection script
create_env_detection() {
    cat > check_ocr_env.py << 'EOF'
#!/usr/bin/env python3
"""
OCR Environment Check Script
Validates that all OCR dependencies are properly installed.
"""

import sys
import subprocess
import importlib.util

def check_python_package(package_name):
    """Check if a Python package is installed."""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def check_system_command(command):
    """Check if a system command is available."""
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, None

def main():
    print("🔍 OCR Environment Check")
    print("=" * 50)
    
    all_good = True
    
    # Check system dependencies
    print("\n📦 System Dependencies:")
    
    # Tesseract
    tesseract_ok, tesseract_info = check_system_command('tesseract')
    if tesseract_ok:
        print(f"✅ Tesseract: {tesseract_info.split()[1] if tesseract_info else 'Found'}")
    else:
        print("❌ Tesseract: Not found")
        all_good = False
    
    # Poppler (pdftoppm)
    poppler_ok, _ = check_system_command('pdftoppm')
    if poppler_ok:
        print("✅ Poppler (PDF processing): Found")
    else:
        print("❌ Poppler (PDF processing): Not found")
        all_good = False
    
    # Check Python packages
    print("\n🐍 Python Packages:")
    
    packages = [
        'pytesseract',
        'easyocr', 
        'cv2',
        'PIL',
        'pdf2image',
        'numpy'
    ]
    
    for package in packages:
        if check_python_package(package):
            print(f"✅ {package}: Installed")
        else:
            print(f"❌ {package}: Missing")
            all_good = False
    
    # Test OCR functionality
    print("\n🧪 OCR Functionality Test:")
    try:
        import pytesseract
        from PIL import Image
        import numpy as np
        
        # Create a simple test image
        test_image = Image.new('RGB', (200, 50), color='white')
        import ImageDraw, ImageFont
        
        # Simple text test (fallback if no fonts available)
        test_text = pytesseract.image_to_string(test_image)
        print("✅ Basic OCR test: Passed")
        
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All OCR dependencies are properly configured!")
        return 0
    else:
        print("⚠️  Some dependencies are missing. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

    chmod +x check_ocr_env.py
    echo "✅ Environment check script created: check_ocr_env.py"
}

# Main execution
main() {
    echo "🚀 IntelliDoc AI - OCR Dependencies Setup"
    echo "========================================"
    
    # Check if running in Docker
    if [ -f /.dockerenv ]; then
        echo "🐳 Running in Docker - dependencies should be handled by Dockerfile"
        verify_tesseract
        return $?
    fi
    
    # Detect if user wants Docker setup
    if [ "$1" = "--docker" ]; then
        setup_docker_alternative
        return 0
    fi
    
    # Create environment check script
    create_env_detection
    
    # Ask user preference
    echo ""
    echo "Choose installation method:"
    echo "1) Install system dependencies (requires admin/sudo)"
    echo "2) Use Docker-based solution (recommended for production)"
    echo "3) Skip installation (dependencies already installed)"
    echo "4) Check current environment only"
    echo ""
    read -p "Enter choice (1-4): " choice
    
    case $choice in
        1)
            install_tesseract
            verify_tesseract
            ;;
        2)
            setup_docker_alternative
            ;;
        3)
            echo "⏭️  Skipping installation..."
            verify_tesseract
            ;;
        4)
            echo "🔍 Checking current environment..."
            if command -v python3 &> /dev/null; then
                python3 check_ocr_env.py
            else
                verify_tesseract
            fi
            ;;
        *)
            echo "❌ Invalid choice"
            exit 1
            ;;
    esac
    
    echo ""
    echo "💡 Tips for production deployment:"
    echo "   • Use Docker for consistent environments across platforms"
    echo "   • Consider using cloud-based OCR APIs for better scalability"
    echo "   • Test with your specific document types before deployment"
    echo ""
    echo "🔧 To run the environment check later: python3 check_ocr_env.py"
}

# Run main function
main "$@"
