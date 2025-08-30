# Start Voice Typing with Local GPU Model
# This script starts the voice typing application using local Whisper model
# Usage: .\startVoice_gpu.ps1 [options]

Write-Host "🚀 Starting Voice Typing System..." -ForegroundColor Green
Write-Host "🖥️  Using Local Whisper Model (GPU)" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Gray

# Check execution policy
$policy = Get-ExecutionPolicy -Scope CurrentUser
if ($policy -eq "Restricted") {
    Write-Host "⚠️  PowerShell execution policy is restricted." -ForegroundColor Yellow
    Write-Host "   Run this command to allow local scripts: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "Press Enter to continue anyway"
}

# Check if virtual environment exists
if (-not (Test-Path ".\whisper_venv")) {
    Write-Host "❌ Error: Virtual environment not found" -ForegroundColor Red
    Write-Host "   Please create it with: python -m venv whisper_venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

try {
    # Activate virtual environment
    Write-Host "🔄 Activating virtual environment..." -ForegroundColor Blue
    & ".\whisper_venv\Scripts\Activate.ps1"
    
    # Check if PyTorch is installed
    $torchInstalled = python -c "import torch" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  PyTorch not detected. Installing required packages..." -ForegroundColor Yellow
        Write-Host "   This may take a few minutes..." -ForegroundColor Yellow
        pip install torch transformers accelerate
    }
    
    # Check GPU availability
    Write-Host "🔍 Checking GPU availability..." -ForegroundColor Blue
    python -c @"
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
        print('   1. Reinstall PyTorch with CUDA support')
        print('   2. Or continue with CPU mode (still faster than API for local transcription)')
except Exception as e:
    print(f'⚠️  Error checking GPU: {e}')
    print('   Will continue with CPU mode')
"@
    
    Write-Host ""
    
    # Start AI Fix in background
    Write-Host "🤖 Starting AI Fix (Alt+G)..." -ForegroundColor Magenta
    $aiFix = Start-Process -FilePath "python" -ArgumentList "ai-fix.py" -NoNewWindow -PassThru
    
    # Give AI Fix a moment to start
    Start-Sleep -Seconds 2
    
    # Start voice typing application
    Write-Host "🎤 Starting Voice Typing (Right Ctrl)..." -ForegroundColor Green
    
    # Pass all arguments to voice_ptt.py with --local flag
    $arguments = $args -join " "
    if ($arguments) {
        $allArgs = "--local " + $arguments
        python voice_ptt.py $allArgs.Split(" ")
    } else {
        python voice_ptt.py --local
    }
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
} finally {
    # Cleanup
    Write-Host "🛑 Cleaning up..." -ForegroundColor Yellow
    try {
        if ($aiFix -and -not $aiFix.HasExited) {
            $aiFix.Kill()
        }
    } catch {
        # Ignore cleanup errors
    }
    Write-Host "✅ Session ended." -ForegroundColor Green
    Read-Host "Press Enter to exit"
}