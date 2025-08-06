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
    
    # Kill AI Fix process if it's still running
    if [ ! -z "$AI_FIX_PID" ] && kill -0 "$AI_FIX_PID" 2>/dev/null; then
        echo "   Stopping AI Fix (PID $AI_FIX_PID)..."
        kill "$AI_FIX_PID" 2>/dev/null || true
        # Give it a moment to exit gracefully
        sleep 1
        # Force kill if still running
        kill -9 "$AI_FIX_PID" 2>/dev/null || true
    fi
    
    # Force cleanup any remaining AI Fix processes (fallback)
    pkill -f "python ai-fix.py" 2>/dev/null || true
    
    # Remove lock file if it exists
    rm -f /tmp/ai-fix.lock 2>/dev/null || true
    
    echo "✅ Stopped"
    exit 0
}

# Set up trap for clean exit (removed EXIT to prevent cascading shutdowns)
trap cleanup SIGINT SIGTERM

# Activate virtual environment
source ./whisper_venv/bin/activate

# Start AI Fix in background with restart capability
start_ai_fix() {
    local attempt=1
    local max_attempts=5
    local base_delay=2
    
    while [ $attempt -le $max_attempts ]; do
        echo "🤖 Starting AI Fix (Alt+G)... (attempt $attempt/$max_attempts)"
        python ai-fix.py
        local exit_code=$?
        
        # Check exit code
        case $exit_code in
            0)
                echo "✅ AI Fix exited normally"
                return 0
                ;;
            1)
                echo "❌ AI Fix could not acquire lock (another instance running)"
                echo "   Not restarting to avoid conflicts"
                return 1
                ;;
            *)
                echo "⚠️  AI Fix crashed with exit code $exit_code"
                if [ $attempt -lt $max_attempts ]; then
                    local delay=$((base_delay ** attempt))
                    echo "   Restarting in $delay seconds... (attempt $((attempt + 1))/$max_attempts)"
                    sleep $delay
                    attempt=$((attempt + 1))
                else
                    echo "   Maximum restart attempts reached. Giving up."
                    return $exit_code
                fi
                ;;
        esac
    done
}

# Initialize AI_FIX_PID variable
AI_FIX_PID=""

# Start AI Fix in background
start_ai_fix &
AI_FIX_PID=$!

# Give AI Fix a moment to start
sleep 1

# Start voice typing application
echo "🎤 Starting Voice Typing (Alt+R)..."

# Pass all arguments to voice_ptt.py (API mode is default)
python voice_ptt.py "$@"

# When voice_ptt.py exits, we should clean up
echo "Voice typing exited. Cleaning up..."
cleanup