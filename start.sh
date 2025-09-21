#!/bin/bash

# AI CLI Startup Script
# This script activates the virtual environment and starts the AI CLI

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Ollama is running
if ! ollama list >/dev/null 2>&1; then
    echo "🔄 Starting Ollama service..."
    ollama serve &
    sleep 3

    if ! ollama list >/dev/null 2>&1; then
        echo "❌ Failed to start Ollama. Please start it manually: ollama serve"
        exit 1
    fi
fi

# Start AI CLI with all arguments passed to this script
echo "🤖 Starting AI CLI..."
python main.py "$@"
