#!/bin/bash

# Start Voice Typing with Whisper Server
# This script starts both the Whisper.cpp server and the voice typing application

echo "🚀 Starting Voice Typing System..."
echo "=================================="

# Check if whisper server binary exists
if [ ! -f "./whisper.cpp/build/bin/whisper-server" ]; then
    echo "❌ Error: Whisper server binary not found at ./whisper.cpp/build/bin/whisper-server"
    echo "   Please build whisper.cpp first"
    exit 1
fi

# Check if model exists
if [ ! -f "./whisper.cpp/models/ggml-large-v3-turbo-q8_0.bin" ]; then
    echo "❌ Error: Model not found at ./whisper.cpp/models/ggml-large-v3-turbo-q8_0.bin"
    echo "   Please download the model first"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "./whisper_venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "   Please create it with: python -m venv whisper_venv"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    # Kill all child processes
    jobs -p | xargs -r kill 2>/dev/null
    wait
    echo "✅ All processes stopped"
    exit 0
}

# Set up trap for clean exit
trap cleanup SIGINT SIGTERM EXIT

# Start Whisper server in background
echo "📡 Starting Whisper server on port 50021..."
./whisper.cpp/build/bin/whisper-server \
    -m ./whisper.cpp/models/ggml-large-v3-turbo-q8_0.bin \
    --host 0.0.0.0 \
    --port 50021 \
    --convert &

WHISPER_PID=$!

# Wait a moment for server to start
sleep 3

# Check if server started successfully
if ! kill -0 $WHISPER_PID 2>/dev/null; then
    echo "❌ Failed to start Whisper server"
    exit 1
fi

echo "✅ Whisper server started (PID: $WHISPER_PID)"
echo ""

# Activate virtual environment and start voice typing
echo "🎤 Starting Voice Typing application..."
source ./whisper_venv/bin/activate
python voice_ptt.py &

VOICE_PID=$!

# Wait a moment to check if voice app started
sleep 1

if ! kill -0 $VOICE_PID 2>/dev/null; then
    echo "❌ Failed to start Voice Typing application"
    exit 1
fi

echo "✅ Voice Typing started (PID: $VOICE_PID)"
echo ""
echo "======================================"
echo "✨ System ready! Use Alt+R to record"
echo "   Press Ctrl+C to stop all services"
echo "======================================"

# Wait for both processes
wait