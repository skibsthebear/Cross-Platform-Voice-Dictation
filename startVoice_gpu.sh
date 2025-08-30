#!/bin/bash

# Start Voice Typing with Local GPU Model
# This script starts the voice typing application using local Whisper model
# Usage: ./startVoice_gpu.sh [options]

echo "🚀 Starting Voice Typing System..."
echo "🖥️  Using Local Whisper Model (GPU)"
echo "=================================="

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

# Set CUDA environment variables
export CUDA_HOME=/usr/local/cuda-12.9
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source ./whisper_venv/bin/activate

# Check if PyTorch is installed
if ! python -c "import torch" 2>/dev/null; then
    echo "⚠️  PyTorch not detected. Installing required packages..."
    echo "   This may take a few minutes..."
    pip install torch transformers accelerate
fi

# Check GPU availability
echo "🔍 Checking GPU availability..."
python -c "
import torch
import warnings
warnings.filterwarnings('ignore', category=UserWarning, message='CUDA initialization')

try:
    if torch.cuda.is_available():
        print(f'✅ CUDA GPU detected: {torch.cuda.get_device_name(0)}')
        print(f'   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
    elif torch.backends.mps.is_available():
        print('✅ Apple Silicon GPU detected (MPS)')
    else:
        print('⚠️  No GPU detected, will use CPU (slower)')
        print('')
        print('   Note: If you have a GPU but it\'s not detected, you may need to:')
        print('   1. Reinstall PyTorch with: pip install torch==2.4.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu129')
        print('   2. Or continue with CPU mode (still faster than API for local transcription)')
except Exception as e:
    print(f'⚠️  Error checking GPU: {e}')
    print('   Will continue with CPU mode')
"

echo ""

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

echo "🎤 Starting Voice Typing (Right Ctrl)..."

# Pass all arguments to voice_ptt.py with --local flag
python voice_ptt.py --local "$@"

# When voice_ptt.py exits, we should clean up
echo "Voice typing exited. Cleaning up..."
cleanup