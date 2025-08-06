@echo off
echo Starting Voice Typing and AI Fix (API Mode)...

:: Change to script directory
cd /d "%~dp0"

:: Check if virtual environment exists
if not exist "whisper_venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating...
    python -m venv whisper_venv
)

:: Activate virtual environment
call whisper_venv\Scripts\activate.bat

:: Install dependencies if needed
pip install -r requirements.txt >nul 2>&1

:: Function to clean up processes
:cleanup
echo Cleaning up...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Voice Typing*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq AI Fix*" >nul 2>&1
exit /b

:: Set up Ctrl+C handler
if "%1"=="TRAP" goto :cleanup

:: Parse command line arguments
set ARGS=
:parse_args
if "%~1"=="" goto :done_parsing
set ARGS=%ARGS% %1
shift
goto :parse_args
:done_parsing

:: Start both processes
echo Starting Voice Typing...
start "Voice Typing" /B python voice_ptt.py %ARGS%

echo Starting AI Fix...
start "AI Fix" /B python ai-fix.py

echo.
echo Both services are running. Press Ctrl+C to stop.
echo - Alt+R: Toggle voice recording
echo - Alt+G: Format highlighted text
echo - ESC: Exit application
echo.

:: Wait for user interrupt
pause >nul
call :cleanup