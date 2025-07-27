#!/bin/bash

# Start Ollama server in the background
echo "Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama service to be ready
echo "Waiting for Ollama service to start..."
for i in {1..30}; do
    if ollama list > /dev/null 2>&1; then
        echo "Ollama service is ready!"
        break
    fi
    sleep 2
done

# Pull required models
echo "Pulling llama3.2:3b model..."
ollama pull llama3.2:3b

echo "Pulling nomic-embed-text model..."
ollama pull nomic-embed-text

echo "All models downloaded successfully!"

# Wait for the background process to continue
wait $OLLAMA_PID
