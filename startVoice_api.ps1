# Start Voice Typing with OpenAI API
# This script starts the voice typing application using OpenAI's API
# Usage: .\startVoice_api.ps1 [options]

Write-Host "🚀 Starting Voice Typing System..." -ForegroundColor Green
Write-Host "📡 Using OpenAI Whisper API" -ForegroundColor Cyan
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

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found" -ForegroundColor Red
    Write-Host "   Please create .env and add your OpenAI API key" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

try {
    # Activate virtual environment
    Write-Host "🔄 Activating virtual environment..." -ForegroundColor Blue
    & ".\whisper_venv\Scripts\Activate.ps1"
    
    # Start AI Fix in background
    Write-Host "🤖 Starting AI Fix (Alt+G)..." -ForegroundColor Magenta
    $aiFix = Start-Process -FilePath "python" -ArgumentList "ai-fix.py" -NoNewWindow -PassThru
    
    # Give AI Fix a moment to start
    Start-Sleep -Seconds 2
    
    # Start voice typing application
    Write-Host "🎤 Starting Voice Typing (Alt+R)..." -ForegroundColor Green
    
    # Pass all arguments to voice_ptt.py (API mode is default)
    $arguments = $args -join " "
    if ($arguments) {
        python voice_ptt.py $arguments.Split(" ")
    } else {
        python voice_ptt.py
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