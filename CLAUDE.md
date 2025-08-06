# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Push-to-Talk Voice Typing and AI Text Formatting application that supports both OpenAI's Whisper API and local GPU-accelerated transcription using distil-whisper models.

The application provides two main features:
1. **Voice Typing**: Records audio when Alt+R is pressed and automatically types the transcribed text at the cursor position
2. **AI Fix**: Formats and corrects highlighted text when Alt+G is pressed using LM Studio's AI models

## Architecture

### Core Components

1. **voice_ptt.py** - Main application orchestrator that:
   - Manages the overall application lifecycle
   - Handles command-line arguments for API vs local mode
   - Coordinates between different modules
   - Implements platform-aware device selection logic
   - Provides informative startup messages with platform detection

2. **audio_device.py** - Audio device management:
   - Cross-platform device selection with platform-aware behavior
   - Linux: Shows device selection menu with actual device names via PulseAudio
   - Windows/WSL: Automatically skips device selection, uses system default
   - Handles device detection and configuration
   - Supports multiple sample rates with automatic fallback
   - Provides override options for manual device selection

3. **audio_recorder.py** - Audio recording functionality:
   - Manages recording start/stop
   - Handles audio data capture and storage
   - Saves temporary WAV files

4. **transcription.py** - Transcription engine:
   - Supports both OpenAI API and local GPU models
   - Auto-detects GPU availability (CUDA/MPS/CPU)
   - Uses distil-whisper/distil-large-v3 for local mode

5. **text_input.py** - Text typing functionality:
   - Copies transcribed text to clipboard
   - Types text at cursor position using pynput

6. **keyboard_handler.py** - Keyboard shortcut management:
   - Listens for Alt+R to toggle recording
   - Handles ESC key for exit

7. **recording_indicator.py** - Visual feedback:
   - Manages the recording indicator subprocess
   - Shows/hides indicator based on recording state

8. **config.py** - Centralized configuration:
   - Audio settings
   - Model configurations
   - Keyboard shortcuts

9. **ai-fix.py** - AI-powered text formatting:
   - Monitors for Alt+G hotkey
   - Captures highlighted text via clipboard
   - Sends text to LM Studio API for processing
   - Replaces selection with formatted text
   - Supports streaming responses
   - Intelligent formatting with context understanding

10. **platform_detection.py** - Cross-platform compatibility:
    - Detects operating system (Windows, Linux, macOS)
    - Identifies Windows Subsystem for Linux (WSL)
    - Determines whether to skip audio device selection
    - Provides platform-aware behavior logic
    - Uses multiple detection methods for reliability

### Dependencies & External Services

- **Transcription Options**:
  1. **OpenAI API Mode**:
     - Requires OpenAI API key in `.env` file
     - Uses OpenAI's Whisper API endpoint
     - No local server required
  
  2. **Local GPU Mode**:
     - Uses distil-whisper/distil-large-v3 model
     - Automatically detects CUDA GPU, Apple Silicon (MPS), or falls back to CPU
     - Requires PyTorch, transformers, and accelerate packages
     - No API key needed

- **AI Text Formatting**:
  - Requires LM Studio running on `http://127.0.0.1:1234`
  - Uses LM Studio's OpenAI-compatible API endpoint
  - Default model: liquid/lfm2-1.2b (configurable)
  - Supports streaming responses for real-time feedback
  
- **Audio Configuration**: 
  - Device selection menu at startup shows actual hardware names (e.g., AT2020, HyperX, Anker)
  - Uses PulseAudio (`pactl`) to get real device names instead of generic ALSA identifiers
  - Selected device is set as the default PulseAudio source for the session
  - Supports multiple sample rates with automatic detection (44100, 48000, 16000, 22050, 8000 Hz)
  - Defaults to mono recording with fallback to stereo if needed
  - Falls back to sounddevice listing if PulseAudio is not available

- **Environment Variables**:
  - `.env` file contains `OPENAI_API_KEY` for API mode
  - File is gitignored for security

## Development Commands

### Running the Complete System

The startup scripts now launch both Voice Typing and AI Fix features together.

There are two ways to run the complete system:

#### 1. OpenAI API Mode (requires API key)

**Linux/macOS:**
```bash
# Start with device selection menu (launches both Voice Typing and AI Fix)
./startVoice_api.sh

# Skip device selection and use system default
./startVoice_api.sh --no-device-select

# Use a specific device by index
./startVoice_api.sh --device 2

# List available devices
./startVoice_api.sh --list-devices
```

**Windows:**
```batch
REM Batch script version
startVoice_api.bat
startVoice_api.bat --no-device-select
startVoice_api.bat --device 2
startVoice_api.bat --list-devices

REM PowerShell version (enhanced error handling)
.\startVoice_api.ps1
.\startVoice_api.ps1 --no-device-select
```

#### 2. Local GPU Mode (uses distil-whisper/distil-large-v3)

**Linux/macOS:**
```bash
# Start with device selection menu (launches both Voice Typing and AI Fix)
./startVoice_gpu.sh

# Skip device selection and use system default
./startVoice_gpu.sh --no-device-select

# Use a specific device by index
./startVoice_gpu.sh --device 2

# List available devices
./startVoice_gpu.sh --list-devices
```

**Windows:**
```batch
REM Batch script version
startVoice_gpu.bat
startVoice_gpu.bat --no-device-select
startVoice_gpu.bat --device 2

REM PowerShell version (with GPU detection and error handling)
.\startVoice_gpu.ps1
.\startVoice_gpu.ps1 --no-device-select
```

Both scripts will start:
- Voice Typing (Alt+R) - For speech-to-text transcription
- AI Fix (Alt+G) - For formatting and correcting highlighted text

The GPU mode will:
- Automatically detect CUDA GPU, Apple Silicon (MPS), or fall back to CPU
- Install PyTorch dependencies if not already installed
- Use the distil-whisper/distil-large-v3 model for faster local transcription
- Show GPU information before starting

### Running Components Individually

```bash
# Activate virtual environment
source whisper_venv/bin/activate

# API Mode (default)
python voice_ptt.py

# Local GPU Mode
python voice_ptt.py --local

# Skip device selection
python voice_ptt.py --no-device-select

# Use specific device
python voice_ptt.py --device 2

# List all available devices
python voice_ptt.py --list-devices

# The --api flag is accepted for backwards compatibility
python voice_ptt.py --api

# Run AI Fix standalone
python ai-fix.py
```

### Virtual Environment

```bash
# Create/recreate virtual environment
python -m venv whisper_venv

# Activate environment
source whisper_venv/bin/activate

# Install dependencies for API mode
pip install -r requirements.txt
# or manually:
pip install sounddevice numpy scipy pynput pyperclip python-dotenv openai PyQt6 requests

# Additional dependencies for GPU mode
pip install torch transformers accelerate
```

## Key Implementation Details

- **Modular Architecture**: Application is split into focused modules for better maintainability
- **Cross-Platform Architecture**: Intelligent platform detection with adaptive behavior
- **Platform Detection**: Multiple detection methods for Windows, Linux, macOS, and WSL environments
- **Recording State**: Managed by AudioRecorder class
- **Audio Device Selection**: 
  - **Cross-Platform Logic**: `list_and_select_device()` automatically detects platform and adjusts behavior
  - **Linux**: `get_pulseaudio_sources()` retrieves device info from PulseAudio with actual hardware names
  - **Linux**: Interactive menu presented at startup with real device names (AT2020, HyperX, etc.)
  - **Linux**: Selected device becomes default PulseAudio source via `pactl set-default-source`
  - **Windows/WSL**: Automatically skips device selection, uses system default with informative messages
  - **Override Options**: Manual device selection available via `--device N` on all platforms
- **Audio Device Detection**: `get_audio_device_info()` validates device capabilities and selects optimal sample rate
- **Audio Storage**: Temporarily saves WAV files in `outputs/` directory before transcription
- **Transcription**: Transcriber class supports both API and local GPU transcription
- **Text Input**: Uses `pyperclip` to copy text to clipboard and `pynput` to paste with Ctrl+Shift+V
  - **Clipboard Restoration**: Automatically restores previous clipboard content after pasting transcribed text
- **Line Break Handling**: Automatically removes newlines from transcriptions for continuous text
- **Keyboard Detection**: Custom listener tracks Alt key state to detect Alt+R and Alt+G combinations
- **Error Handling**: Graceful handling of API errors and audio device issues with automatic fallback
- **Sample Rate Detection**: Tests multiple rates (8000-96000 Hz) and selects best supported option
- **AI Text Processing**: 
  - Captures highlighted text preserving clipboard state
  - Streams AI responses for real-time feedback
  - Intelligent formatting with context understanding
  - Converts spoken formats (e.g., "dot com" → ".com")
  - Adds appropriate line breaks for emails, lists, and paragraphs
  - **Clipboard Restoration**: Automatically restores previous clipboard content after text replacement

## Device Selection Workflow

When starting the application:

1. **PulseAudio Detection**: The app first tries to get device info from PulseAudio using `pactl -f json list sources`
2. **Device Listing**: Shows actual hardware names (e.g., "AT2020USB+", "HyperX QuadCast S") extracted from device properties
3. **User Selection**: User can:
   - Select a device by number (1, 2, 3, etc.)
   - Press Enter or select 0 for system default
   - Use Ctrl+C to cancel
4. **Device Configuration**: Selected device is set as PulseAudio default source
5. **Fallback**: If PulseAudio is unavailable, falls back to sounddevice's generic listing

## Cross-Platform Compatibility

The application now includes intelligent cross-platform detection and behavior:

### Platform Detection
- **platform_detection.py**: Automatically detects Windows, Linux, macOS, and WSL environments
- **WSL Detection**: Uses multiple methods to identify Windows Subsystem for Linux:
  - Checks `/proc/version` for Microsoft/WSL signatures
  - Looks for `WSL_DISTRO_NAME` environment variable
  - Detects `WSLENV` environment variable (WSL2)

### Platform-Specific Behavior
- **Linux (non-WSL)**: Full device selection menu with PulseAudio integration
- **Windows/WSL**: Automatically skips device selection and uses system default
  - Shows informative message explaining auto-skip behavior
  - Provides override instructions for manual device selection
  - Warns about potential compatibility issues when using manual selection

### Windows-Specific Scripts
- **startVoice_api.bat**: Windows batch script for OpenAI API mode
- **startVoice_gpu.bat**: Windows batch script for local GPU mode
- **startVoice_api.ps1**: PowerShell alternative with enhanced error handling
- **startVoice_gpu.ps1**: PowerShell GPU script with execution policy warnings

## Recording Indicator

The application includes a visual recording indicator built with PyQt6:
- Shows a "🔴 Recording" text overlay near the mouse cursor
- Appears at the mouse position when recording starts (with 20px offset)
- Features a pulsing opacity animation
- White text on dark semi-transparent background with rounded corners
- Automatically closes when recording stops

The indicator is implemented in `recording_indicator_qt.py` and requires PyQt6 to be installed.

## Important Notes

### Cross-Platform Behavior
- **Linux (non-WSL)**: Audio device selection menu appears at startup showing actual device names (AT2020, HyperX, etc.)
- **Windows/WSL**: Device selection is automatically skipped for compatibility, uses system default
- **All Platforms**: Manual device selection available via `--device N` and `--list-devices` flags
- Platform detection is automatic and provides informative startup messages

### General Notes
- Temporary audio files are cleaned up after transcription
- `.env` file is gitignored and must contain `OPENAI_API_KEY` for API mode
- AI Fix requires LM Studio running on `http://127.0.0.1:1234`
- Command-line arguments:
  - `--api`: Accepted for backwards compatibility but not needed (API is default)
  - `--local`: Use local GPU model instead of OpenAI API
  - `--no-device-select`: Skip device selection menu and use system default
  - `--device <index>`: Use specific device by index number
  - `--list-devices`: List available devices and exit
- Keyboard shortcuts:
  - `Alt+R`: Toggle voice recording and transcription
  - `Alt+G`: Format and fix highlighted text with AI
  - `ESC`: Exit the application
- Requirements.txt includes all dependencies including PyQt6 for the recording indicator and requests for AI Fix
- Recording indicator requires PyQt6 but the app will still work if PyQt6 is not installed
- Uses sounddevice instead of PyAudio for better Linux compatibility
- Uses PulseAudio to get actual hardware device names instead of generic ALSA names
- Configuration variables are centralized in config.py
- Supports both float16 (GPU) and float32 (CPU) precision automatically

## Troubleshooting

### Windows/WSL Specific Issues

**Device Selection Skipped**: This is normal behavior on Windows/WSL for compatibility reasons
- **Solution**: Use `--device N` for manual device selection if needed
- **Check devices**: Use `--list-devices` to see available options

**PowerShell Execution Policy Error**: 
- **Error**: "execution of scripts is disabled on this system"
- **Solution**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Virtual Environment Issues**:
- **Windows**: Use `whisper_venv\Scripts\activate.bat` instead of the Linux path
- **PowerShell**: Use `.\whisper_venv\Scripts\Activate.ps1`

**PyTorch Installation on Windows**:
- For CUDA: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
- For CPU only: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu`

### General Troubleshooting

**Audio Recording Issues**:
- Verify microphone permissions in system settings
- Check if other applications are using the microphone
- Try `--list-devices` to confirm device availability

**API Errors**:
- Verify `.env` file contains valid `OPENAI_API_KEY`
- Check internet connection for API mode

## Testing Utilities

The repository includes several test scripts:

### Platform and Compatibility Testing
- **test_platform_detection.py**: Comprehensive platform detection testing suite
  - Tests OS detection (Windows, Linux, macOS)
  - Validates WSL detection methods
  - Verifies device selection skip logic
  - Tests edge cases and error handling

### Audio Device Testing
- **test_audio_device_pulse.py**: Interactive device selection and testing with PulseAudio support
- **test_audio_device.py**: Device testing with recording and analysis
- **list_audio_devices.py**: Shows devices from multiple sources (ALSA, PulseAudio, sounddevice)

### UI Component Testing
- **test_qt_indicator.py**: Tests the PyQt6 recording indicator
- **test_pynput_mouse.py**: Tests mouse position detection for indicator placement

## Recent Changes: Windows/WSL Compatibility Implementation

### New Files Added
- **platform_detection.py**: Core platform detection module with OS and WSL identification
- **startVoice_api.bat**: Windows batch script for API mode
- **startVoice_gpu.bat**: Windows batch script for GPU mode  
- **startVoice_api.ps1**: PowerShell script with enhanced error handling
- **startVoice_gpu.ps1**: PowerShell script with GPU detection
- **test_platform_detection.py**: Comprehensive platform detection test suite

### Modified Files
- **voice_ptt.py**: Added platform-aware device selection logic and startup messages
- **audio_device.py**: Implemented cross-platform device selection with auto-skip for Windows/WSL
- **CLAUDE.md**: Updated with cross-platform documentation and troubleshooting
- **README.md**: Added Windows-specific instructions and troubleshooting sections

### Key Features Implemented
- **Automatic Platform Detection**: Detects Windows, Linux, macOS, and WSL environments
- **Smart Device Selection**: Auto-skips device selection on Windows/WSL, full menu on Linux
- **Informative User Messages**: Clear explanations of platform-specific behavior
- **Manual Override Options**: Advanced users can still use `--device N` on any platform
- **Complete Windows Support**: Native batch and PowerShell scripts with error handling
- **Comprehensive Testing**: Full test suite validates platform detection across environments
- **Documentation**: Updated technical and user documentation with Windows-specific guidance

### Backwards Compatibility
- **Linux Behavior**: Completely unchanged - all existing functionality preserved
- **Command-Line Arguments**: All existing flags work identically on all platforms  
- **API Compatibility**: No breaking changes to any existing interfaces
- **Script Compatibility**: Original Linux scripts continue to work normally

This implementation ensures seamless cross-platform operation while maintaining full backwards compatibility and providing clear, helpful user feedback.