@echo off
echo CUDA Error Fix for Windows
echo ==========================

:: Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

:: Find CUDA installation
set CUDA_PATH=
for /d %%i in ("C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v*") do set CUDA_PATH=%%i

if not defined CUDA_PATH (
    echo CUDA installation not found.
    echo Please install CUDA from: https://developer.nvidia.com/cuda-downloads
    pause
    exit /b 1
)

echo Found CUDA at: %CUDA_PATH%

:: Update system PATH
echo Updating system PATH...
setx /M PATH "%CUDA_PATH%\bin;%CUDA_PATH%\libnvvp;%PATH%"

:: Check NVIDIA driver
echo.
echo Checking NVIDIA driver...
nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo NVIDIA driver not found or not working properly.
    echo Please download and install the latest driver from:
    echo https://www.nvidia.com/drivers
) else (
    echo NVIDIA driver is working.
    nvidia-smi
)

:: Reinstall PyTorch with CUDA
echo.
echo Reinstalling PyTorch with CUDA support...
if exist "whisper_venv\Scripts\activate.bat" (
    call whisper_venv\Scripts\activate.bat
    pip uninstall -y torch torchvision torchaudio
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    
    :: Test CUDA
    echo.
    echo Testing CUDA...
    python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"
) else (
    echo Virtual environment not found. Please run startVoice_gpu.bat first.
)

echo.
echo CUDA fix completed.
pause