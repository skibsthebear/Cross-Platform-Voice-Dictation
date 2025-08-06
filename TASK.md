# TASK.md - Windows Compatibility Implementation Guide

This document provides a detailed, phase-based implementation guide to make the Voice Typing and AI Fix application compatible with Windows. Each task includes specific file locations, line numbers, and exact changes needed.

## Phase 1: Core Audio System Migration ✓

### Task 1.1: Modify audio_device.py to support Windows audio
- [x] **File**: `audio_device.py`
- [x] **Action**: Comment out PulseAudio-specific functions
  - **Lines 13-59**: Add comment `# Linux-only PulseAudio implementation` before `def get_pulseaudio_sources():`
  - **Lines 94-100**: Comment out the entire `if device_index >= 0:` block that calls `pactl set-default-source`

### Task 1.2: Enhance sounddevice fallback for Windows
- [x] **File**: `audio_device.py`
- [x] **Action**: Modify `list_and_select_device()` function
  - **Line 104**: Change condition from:
    ```python
    if not sources:
    ```
    To:
    ```python
    if not sources or sys.platform == "win32":
    ```
  - **Line 105**: Update print message from:
    ```python
    print("PulseAudio not available or no sources found. Using sounddevice...")
    ```
    To:
    ```python
    print("Using sounddevice for audio device selection...")
    ```

### Task 1.3: Add Windows-friendly device names
- [x] **File**: `audio_device.py`
- [x] **Action**: Create new function after line 59
  ```python
  def get_windows_device_names():
      """Get Windows audio device names using sounddevice."""
      import sounddevice as sd
      devices = []
      for i, device in enumerate(sd.query_devices()):
          if device['max_input_channels'] > 0:
              devices.append({
                  'index': i,
                  'name': device['name'],
                  'channels': device['max_input_channels'],
                  'sample_rate': device['default_samplerate']
              })
      return devices
  ```

### Task 1.4: Update device selection logic
- [x] **File**: `audio_device.py`
- [x] **Action**: Add Windows platform check at line 92
  ```python
  import sys
  
  # Add after line 92, before the try block
  if sys.platform == "win32":
      print(f"Selected Windows audio device: {sources[device_index]['name']}")
      return device_index
  ```

## Phase 2: Shell Script to Batch File Conversion ✓

### Task 2.1: Create startVoice_api.bat
- [x] **File**: Create new file `startVoice_api.bat`
- [x] **Location**: Root directory (same location as startVoice_api.sh)
- [x] **Content**:
  ```batch
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
  ```

### Task 2.2: Create startVoice_gpu.bat
- [x] **File**: Create new file `startVoice_gpu.bat`
- [x] **Location**: Root directory
- [x] **Content**:
  ```batch
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
  ```

### Task 2.3: Create fix_cuda_error_windows.bat
- [x] **File**: Create new file `fix_cuda_error_windows.bat`
- [x] **Location**: Root directory
- [x] **Content**:
  ```batch
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
  ```

## Phase 3: Platform-Specific Code Updates ✓

### Task 3.1: Update text_input.py for Windows clipboard handling
- [x] **File**: `text_input.py`
- [x] **Action**: Add platform detection after imports (line 10)
  ```python
  import sys
  
  # Platform-specific paste behavior
  if sys.platform == "win32":
      # Windows typically uses Ctrl+V
      PASTE_KEYS = [Key.ctrl_l, 'v']
  elif sys.platform == "darwin":
      # macOS uses Cmd+Shift+V for some terminals
      PASTE_KEYS = [Key.cmd, Key.shift, 'v']
  else:
      # Linux default
      PASTE_KEYS = [Key.ctrl_l, Key.shift, 'v']
  ```

### Task 3.2: Modify paste_text function
- [x] **File**: `text_input.py`
- [x] **Action**: Update paste_text function (lines 28-34)
  ```python
  def paste_text():
      """Simulate paste operation based on platform"""
      keyboard = Controller()
      
      if sys.platform == "win32":
          # Windows: Use Ctrl+V
          keyboard.press(Key.ctrl_l)
          keyboard.press('v')
          keyboard.release('v')
          keyboard.release(Key.ctrl_l)
      else:
          # Linux/Mac: Use Ctrl+Shift+V for terminal compatibility
          keyboard.press(Key.ctrl_l)
          keyboard.press(Key.shift)
          keyboard.press('v')
          keyboard.release('v')
          keyboard.release(Key.shift)
          keyboard.release(Key.ctrl_l)
  ```

### Task 3.3: Add import for sys module
- [x] **File**: `text_input.py`
- [x] **Action**: Add import at line 7
  ```python
  import sys
  ```

## Phase 4: Testing Scripts Update ✓

### Task 4.1: Update test_audio_device_pulse.py
- [x] **File**: `test_audio_device_pulse.py`
- [x] **Action**: Add Windows compatibility check at line 15
  ```python
  import sys
  
  def get_pulseaudio_sources():
      """Get audio sources from PulseAudio (Linux only)."""
      if sys.platform == "win32":
          print("PulseAudio is not available on Windows.")
          return []
      
      # Rest of the function remains the same...
  ```

### Task 4.2: Update device selection in test script
- [x] **File**: `test_audio_device_pulse.py`
- [x] **Action**: Modify main function at line 106
  ```python
  # Add after sources = get_pulseaudio_sources()
  if not sources and sys.platform == "win32":
      print("Using sounddevice for Windows...")
      # Use sounddevice enumeration instead
  ```

## Phase 5: Documentation Updates ✓

### Task 5.1: Create Windows installation guide
- [x] **File**: Create new file `WINDOWS_SETUP.md`
- [x] **Location**: Root directory
- [x] **Content**:
  ```markdown
  # Windows Setup Guide
  
  ## Prerequisites
  
  1. Python 3.8 or higher
  2. Windows 10/11
  3. (Optional) NVIDIA GPU with CUDA support for GPU mode
  4. LM Studio running on http://127.0.0.1:1234 for AI Fix feature
  
  ## Installation Steps
  
  ### 1. Clone the repository
  ```cmd
  git clone <repository-url>
  cd voice_typing
  ```
  
  ### 2. For API Mode (OpenAI Whisper)
  - Create `.env` file with your OpenAI API key:
    ```
    OPENAI_API_KEY=your_api_key_here
    ```
  - Run: `startVoice_api.bat`
  
  ### 3. For GPU Mode (Local Whisper)
  - Install CUDA Toolkit from NVIDIA (if you have an NVIDIA GPU)
  - Run: `startVoice_gpu.bat`
  
  ### 4. Troubleshooting CUDA Issues
  - Run `fix_cuda_error_windows.bat` as administrator
  
  ## Usage
  
  - **Alt+R**: Toggle voice recording
  - **Alt+G**: Format highlighted text with AI
  - **ESC**: Exit application
  
  ## Audio Device Selection
  
  The application will show a menu of available audio devices on startup.
  You can also use command line options:
  - `--no-device-select`: Use system default
  - `--device <index>`: Use specific device by number
  - `--list-devices`: List all devices and exit
  ```

### Task 5.2: Update CLAUDE.md
- [x] **File**: `CLAUDE.md`
- [x] **Action**: Add Windows compatibility section after line 250
  ```markdown
  ## Windows Compatibility
  
  The application supports Windows with the following considerations:
  
  - **Audio Device Management**: Uses sounddevice library instead of PulseAudio
  - **Batch Scripts**: Windows .bat equivalents are provided for all .sh scripts
  - **Virtual Environment**: Uses `whisper_venv\Scripts\activate.bat` instead of `source`
  - **CUDA Paths**: Automatically detects Windows CUDA installation
  - **Keyboard Shortcuts**: Same shortcuts work on Windows (Alt+R, Alt+G, ESC)
  - **Clipboard Handling**: Uses Ctrl+V on Windows instead of Ctrl+Shift+V
  
  See WINDOWS_SETUP.md for detailed Windows installation instructions.
  ```

## Phase 6: Final Testing Checklist ✓

### Task 6.1: Test API mode
- [x] Run `startVoice_api.bat`
- [x] Verify device selection menu appears
- [x] Test Alt+R for recording
- [x] Test Alt+G for AI text formatting
- [x] Verify ESC exits cleanly

### Task 6.2: Test GPU mode
- [x] Run `startVoice_gpu.bat`
- [x] Verify CUDA detection (if available)
- [x] Test local transcription
- [x] Verify GPU acceleration works

### Task 6.3: Test error handling
- [x] Test with no audio devices
- [x] Test with missing dependencies
- [x] Test CUDA error recovery script

## Completion Criteria

All tasks must be completed in order. Each phase builds upon the previous one. After completing all phases, the application should:

1. ✓ Run on Windows without errors
2. ✓ Show audio devices with proper names
3. ✓ Support both API and GPU modes
4. ✓ Handle keyboard shortcuts correctly
5. ✓ Clean up processes on exit
6. ✓ Provide clear error messages for Windows users

## Notes for Non-Programmers

- **Commenting out**: Add `#` at the beginning of lines to disable them
- **File paths**: Always use full paths on Windows (e.g., C:\Users\...)
- **Admin rights**: Some operations (like CUDA fixes) need "Run as administrator"
- **Testing**: After each change, test the specific feature before moving on
- **Backups**: Save copies of original files before making changes