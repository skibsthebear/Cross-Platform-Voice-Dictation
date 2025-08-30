@echo off
REM Start Voice Typing with Local GPU Model
REM This script starts the voice typing application using local Whisper model
REM Usage: startVoice_gpu.bat [options]

echo 🚀 Starting Voice Typing System...
echo 🖥️  Using Local Whisper Model (GPU)
echo ==================================

REM Check if virtual environment exists
if not exist ".\whisper_venv" (
    echo ❌ Error: Virtual environment not found
    echo    Please create it with: python -m venv whisper_venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .\whisper_venv\Scripts\activate.bat

REM Check if PyTorch is installed
python -c "import torch" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  PyTorch not detected. Installing required packages...
    echo    This may take a few minutes...
    pip install torch transformers accelerate
)

REM Check GPU availability
echo 🔍 Checking GPU availability...
python -c "import torch; import warnings; warnings.filterwarnings('ignore', category=UserWarning, message='CUDA initialization'); print('✅ CUDA GPU detected: ' + torch.cuda.get_device_name(0) + f' ({torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB)') if torch.cuda.is_available() else ('✅ CPU mode will be used' if not torch.backends.mps.is_available() else '✅ Apple Silicon GPU detected (MPS)')" 2>nul

echo.

REM Start AI Fix in background
echo 🤖 Starting AI Fix (Alt+G)...
start "AI Fix" /B cmd /c "call .\whisper_venv\Scripts\activate.bat && python ai-fix.py"

REM Give AI Fix a moment to start
timeout /t 2 /nobreak >nul

REM Start voice typing application
echo 🎤 Starting Voice Typing (Right Ctrl)...

REM Pass all arguments to voice_ptt.py with --local flag
python voice_ptt.py --local %*

REM When script ends, show completion message
echo Voice typing session ended.
echo Press any key to exit...
pause >nul