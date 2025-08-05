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
    # Kill all background processes
    kill $(jobs -p) 2>/dev/null
    echo "✅ Stopped"
    exit 0
}

# Set up trap for clean exit
trap cleanup SIGINT SIGTERM EXIT

# Activate virtual environment
source ./whisper_venv/bin/activate

# Start AI Fix in background
echo "🤖 Starting AI Fix (Alt+G)..."
python ai-fix.py &
AI_FIX_PID=$!

# Give AI Fix a moment to start
sleep 1

# Start voice typing application
echo "🎤 Starting Voice Typing (Alt+R)..."

# Pass all arguments to voice_ptt.py (API mode is default)
python voice_ptt.py "$@"

# Wait for all background processes
wait