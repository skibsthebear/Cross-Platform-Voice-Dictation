@echo off
REM Start Voice Typing with OpenAI API
REM This script starts the voice typing application using OpenAI's API
REM Usage: startVoice_api.bat [options]

echo 🚀 Starting Voice Typing System...
echo 📡 Using OpenAI Whisper API
echo ==================================

REM Check if virtual environment exists
if not exist ".\whisper_venv" (
    echo ❌ Error: Virtual environment not found
    echo    Please create it with: python -m venv whisper_venv
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ❌ Error: .env file not found
    echo    Please create .env and add your OpenAI API key
    pause
    exit /b 1
)

REM Activate virtual environment
call .\whisper_venv\Scripts\activate.bat

REM Start AI Fix in background
echo 🤖 Starting AI Fix (Alt+G)...
start "AI Fix" /B cmd /c "call .\whisper_venv\Scripts\activate.bat && python ai-fix.py"

REM Give AI Fix a moment to start
timeout /t 2 /nobreak >nul

REM Start voice typing application
echo 🎤 Starting Voice Typing (Alt+R)...

REM Pass all arguments to voice_ptt.py (API mode is default)
python voice_ptt.py %*

REM When script ends, show completion message
echo Voice typing session ended.
echo Press any key to exit...
pause >nul