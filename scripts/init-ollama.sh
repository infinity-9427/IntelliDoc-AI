#!/bin/bash

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if a model exists
model_exists() {
    ollama list | grep -q "$1"
}

# Function to pull model with retry
pull_model_with_retry() {
    local model=$1
    local max_retries=3
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        log "Attempting to pull $model (attempt $((retry + 1))/$max_retries)..."
        if ollama pull "$model"; then
            log "Successfully pulled $model"
            return 0
        else
            log "Failed to pull $model (attempt $((retry + 1))/$max_retries)"
            retry=$((retry + 1))
            if [ $retry -lt $max_retries ]; then
                log "Retrying in 10 seconds..."
                sleep 10
            fi
        fi
    done
    
    log "ERROR: Failed to pull $model after $max_retries attempts"
    return 1
}

log "=== Starting Ollama Initialization ==="

# Start Ollama server in the background
log "Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama service to be ready
log "Waiting for Ollama service to start..."
for i in {1..60}; do
    if ollama list > /dev/null 2>&1; then
        log "Ollama service is ready!"
        break
    fi
    log "Waiting for Ollama... ($i/60)"
    sleep 3
done

# Check if service started successfully
if ! ollama list > /dev/null 2>&1; then
    log "ERROR: Ollama service failed to start!"
    exit 1
fi

# Pull required models
MODELS=("llama3.2:3b" "nomic-embed-text")

for model in "${MODELS[@]}"; do
    if model_exists "$model"; then
        log "Model $model already exists, skipping download"
    else
        log "Model $model not found, downloading..."
        if ! pull_model_with_retry "$model"; then
            log "ERROR: Critical failure - could not download $model"
            # Continue anyway to allow basic functionality
        fi
    fi
done

# Verify models are available
log "Verifying downloaded models..."
ollama list

log "=== Ollama initialization completed ==="

# Keep the server running
wait $OLLAMA_PID
