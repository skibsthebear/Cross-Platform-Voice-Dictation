#!/bin/bash

# Start Voice Typing with OpenAI API
# This script starts the voice typing application using OpenAI's API
# Usage: ./startVoice_api.sh [options]

echo "🚀 Starting Voice Typing System..."
echo "📡 Using OpenAI Whisper API"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "./whisper_venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "   Please create it with: python -m venv whisper_venv"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "   Please create .env and add your OpenAI API key"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    echo "✅ Stopped"
    exit 0
}

# Set up trap for clean exit
trap cleanup SIGINT SIGTERM EXIT

# Activate virtual environment and start voice typing
echo "🎤 Starting Voice Typing application..."
source ./whisper_venv/bin/activate

# Pass all arguments to voice_ptt.py (API mode is default)
python voice_ptt.py "$@"