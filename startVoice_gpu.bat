@echo off
echo Starting Voice Typing and AI Fix (GPU Mode)...

:: Change to script directory
cd /d "%~dp0"

:: Check CUDA installation
set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.9
if not exist "%CUDA_PATH%" (
    echo CUDA not found at %CUDA_PATH%
    echo Checking other CUDA versions...
    for /d %%i in ("C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v*") do set CUDA_PATH=%%i
)

if exist "%CUDA_PATH%" (
    echo Found CUDA at: %CUDA_PATH%
    set PATH=%CUDA_PATH%\bin;%CUDA_PATH%\libnvvp;%PATH%
) else (
    echo WARNING: CUDA not found. GPU acceleration may not work.
)

:: Check if virtual environment exists
if not exist "whisper_venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating...
    python -m venv whisper_venv
)

:: Activate virtual environment
call whisper_venv\Scripts\activate.bat

:: Install dependencies
pip install -r requirements.txt >nul 2>&1

:: Check for PyTorch with CUDA
python -c "import torch; print(f'PyTorch CUDA available: {torch.cuda.is_available()}')"
if errorlevel 1 (
    echo Installing PyTorch with CUDA support...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
)

:: Install additional GPU dependencies
pip install transformers accelerate >nul 2>&1

:: Show GPU info
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"No GPU detected\"}')"

:: Function to clean up processes
:cleanup
echo Cleaning up...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Voice Typing*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq AI Fix*" >nul 2>&1
exit /b

:: Parse command line arguments
set ARGS=--local
:parse_args
if "%~1"=="" goto :done_parsing
set ARGS=%ARGS% %1
shift
goto :parse_args
:done_parsing

:: Start both processes
echo Starting Voice Typing (GPU Mode)...
start "Voice Typing GPU" /B python voice_ptt.py %ARGS%

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