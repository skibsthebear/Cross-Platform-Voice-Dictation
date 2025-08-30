# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Push-to-Talk Voice Typing and AI Text Formatting application with dual transcription support:
- **Voice Typing**: Real-time speech-to-text with Right Ctrl push-to-talk
- **AI Fix**: Intelligent text formatting with Alt+G hotkey
- Supports OpenAI Whisper API and local GPU (distil-whisper/distil-large-v3)

## Commands

### Setup and Installation
```bash
# Create virtual environment
python -m venv whisper_venv
source whisper_venv/bin/activate  # Linux/macOS
# or: whisper_venv\Scripts\activate.bat  # Windows

# Install dependencies
pip install -r requirements.txt

# Additional for GPU mode
pip install torch transformers accelerate

# For OpenAI API mode
cp .example.env .env
# Edit .env to add OPENAI_API_KEY
```

### Running the Application

#### Complete System (Voice + AI Fix)
```bash
# API Mode
./startVoice_api.sh [options]        # Linux/macOS
startVoice_api.bat [options]         # Windows

# GPU Mode  
./startVoice_gpu.sh [options]        # Linux/macOS
startVoice_gpu.bat [options]         # Windows

# Options:
#   --no-device-select    Skip device selection menu
#   --device <N>          Use specific device by index
#   --list-devices        List available devices and exit
```

#### Individual Components
```bash
# Voice Typing
python voice_ptt.py          # API mode (default)
python voice_ptt.py --local  # GPU mode

# AI Fix standalone
python ai-fix.py
```

### Testing and Debugging
```bash
# Test platform detection
python test_platform_detection.py

# Test audio device selection
python test_audio_device_pulse.py

# List all audio devices
python list_audio_devices.py

# Fix CUDA errors (Linux)
sudo ./fix_cuda_error.sh
```

## Architecture

### Core Module Structure

```
voice_typing/
├── Core Components
│   ├── voice_ptt.py              # Main orchestrator, CLI argument handling
│   ├── audio_device.py           # Cross-platform device selection with PulseAudio
│   ├── audio_recorder.py         # Recording state management, WAV file handling
│   ├── transcription.py          # Dual-mode transcriber (API/Local GPU)
│   ├── text_input.py             # Clipboard management, keyboard typing
│   ├── keyboard_handler.py       # Hotkey detection (Right Ctrl, Alt+G, ESC)
│   └── recording_indicator.py    # PyQt6 visual feedback management
│
├── AI Processing
│   ├── ai-fix.py                 # Alt+G text formatting handler
│   └── ai_formatter_shared.py    # Shared LM Studio API client
│
├── Platform Support
│   └── platform_detection.py     # OS/WSL detection, device skip logic
│
├── Configuration
│   ├── config.py                 # Centralized settings, device auto-detection
│   └── settings.json             # User preferences (AI model, passthrough mode)
│
└── Startup Scripts
    ├── startVoice_*.sh           # Linux/macOS launchers with cleanup traps
    └── startVoice_*.bat/ps1      # Windows launchers with error handling
```

### Key Design Patterns

1. **Modular Architecture**: Each module has single responsibility
2. **Cross-Platform Abstraction**: Platform detection determines behavior
3. **Dual Transcription Pipeline**: 
   - API: OpenAI Whisper endpoint
   - Local: distil-whisper with auto GPU/CPU detection
4. **Process Management**: Startup scripts handle both Voice and AI Fix with cleanup
5. **State Management**: 
   - Recording state in AudioRecorder class
   - Lock files prevent duplicate AI Fix instances
6. **Error Recovery**: Automatic restart for AI Fix crashes with exponential backoff

### Audio Device Flow

1. **Platform Detection** (`platform_detection.py`):
   - Linux (non-WSL): Full device selection
   - Windows/WSL: Auto-skip for compatibility
   
2. **Device Selection** (`audio_device.py`):
   - PulseAudio integration: `pactl -f json list sources`
   - Shows actual hardware names (e.g., "AT2020USB+")
   - Sets default source: `pactl set-default-source`
   - Fallback to sounddevice if PulseAudio unavailable

3. **Sample Rate Detection** (`get_audio_device_info()`):
   - Tests rates: 44100, 48000, 16000, 22050, 8000 Hz
   - Auto-selects best supported rate
   - Fallback chain for compatibility

### Clipboard Preservation

Both `text_input.py` and `ai-fix.py` implement clipboard restoration:
```python
# Save original clipboard
original_clipboard = pyperclip.paste()
# ... perform operations ...
# Restore clipboard
pyperclip.copy(original_clipboard)
```

### Long-Form Audio Handling

For recordings >30 seconds (`config.py`):
- Chunking: 30-second segments
- Overlap: 5-second stride for context
- Automatic in both API and local modes

## Important Implementation Details

### Settings Configuration (`settings.json`)
- `ai_passthrough`: Enable/disable AI formatting for transcribed text
- `ai_model`: LM Studio model selection
- `ai_temperature`: Response creativity (0.0-1.0)
- `ai_api_url`: LM Studio endpoint (default: http://127.0.0.1:1234)

### GPU Detection (`config.py`)
```python
# Auto-detection order:
1. CUDA GPU (NVIDIA)
2. MPS (Apple Silicon)  
3. CPU fallback with float32
```

### Process Cleanup (`startVoice_*.sh`)
- Trap handlers for SIGINT/SIGTERM
- AI Fix PID tracking and cleanup
- Lock file removal (`/tmp/ai-fix.lock`)
- Force cleanup with pkill fallback

### ESC Key Handling (`keyboard_handler.py`)
- Double-press confirmation to prevent accidental exits
- Single press during device selection cancels selection
- Configurable in `config.py`

### USB Microphone Unmute (`keyboard_handler.py`)
- Automatically unmutes USB microphones when Right Ctrl is pressed
- Uses JSON parsing with `pactl -f json list sources` for reliability
- Prioritizes AT2020 devices when multiple USB mics present
- Verifies unmute success with retry logic (max 2 attempts)
- Sets volume to 70% after successful unmute
- Fallback to legacy parsing for older pactl versions
- Clear logging for debugging unmute issues

### Error Codes (`ai-fix.py`)
- 0: Normal exit
- 1: Lock acquisition failed (duplicate instance)
- Other: Crash requiring restart

## Development Guidelines

### Adding New Features
1. Create modular component in separate file
2. Import and integrate in `voice_ptt.py` or relevant module
3. Update startup scripts if new process needed
4. Add configuration to `config.py` or `settings.json`

### Debugging Audio Issues
1. Check device with `--list-devices`
2. Test specific device with `--device N`
3. Verify PulseAudio: `pactl info`
4. Check sample rates in `test_audio_device_pulse.py`

### Platform-Specific Testing
1. Use `test_platform_detection.py` to verify OS detection
2. Test device selection behavior matches platform
3. Verify startup scripts work on target platform

### AI Model Configuration
1. Ensure LM Studio running on port 1234
2. Load desired model in LM Studio
3. Update `settings.json` with model name
4. Test with highlighted text + Alt+G

## Critical Files

- **voice_ptt.py**: Entry point, argument parsing, module coordination
- **audio_device.py**: Platform-aware device selection logic
- **config.py**: All configuration constants, auto-detection
- **platform_detection.py**: WSL/OS detection for behavior switching
- **ai_formatter_shared.py**: Shared AI formatting client
- **startVoice_*.sh**: Process management, cleanup handlers