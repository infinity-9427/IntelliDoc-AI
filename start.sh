#!/bin/bash

# IntelliDoc AI - Quick Start Script
echo "🚀 Starting IntelliDoc AI - PDF Converter & Document Intelligence Platform"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "Make sure you have both 'backend' and 'frontend' directories"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    jobs -p | xargs -r kill
    wait
    echo "✅ Cleanup complete"
    exit 0
}

# Trap signals to cleanup
trap cleanup SIGINT SIGTERM

echo "📦 Installing missing Python dependencies..."
cd backend
python -m pip install pdf2image opencv-python pytesseract > /dev/null 2>&1

echo "🔧 Starting FastAPI Backend Server (Port 8000)..."
python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

cd ../frontend
echo "🌐 Starting Next.js Frontend Server (Port 3001)..."
npm run dev &
FRONTEND_PID=$!

# Wait for servers to start
sleep 5

echo ""
echo "✅ Servers are running!"
echo ""
echo "📍 Backend API: http://localhost:8000"
echo "📍 Frontend UI: http://localhost:3001" 
echo "📍 Health Check: http://localhost:8000/health"
echo ""
echo "🎯 Ready to process documents!"
echo "   1. Open http://localhost:3001 in your browser"
echo "   2. Upload a PDF or image file"
echo "   3. Watch real-time processing"
echo "   4. Download your processed document"
echo ""
echo "💡 Press Ctrl+C to stop all servers"

# Wait for user to stop
wait
