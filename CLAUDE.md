# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Push-to-Talk Voice Typing application that supports both OpenAI's Whisper API and local GPU-accelerated transcription using distil-whisper models.

The application records audio when Alt+R is pressed and automatically types the transcribed text at the cursor position.

## Architecture

### Core Components

1. **voice_ptt.py** - Main application orchestrator that:
   - Manages the overall application lifecycle
   - Handles command-line arguments for API vs local mode
   - Coordinates between different modules

2. **audio_device.py** - Audio device management:
   - Shows device selection menu with actual device names via PulseAudio
   - Handles device detection and configuration
   - Supports multiple sample rates with automatic fallback

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

There are two ways to run the voice typing system:

#### 1. OpenAI API Mode (requires API key)
```bash
# Start with device selection menu
./startVoice_api.sh

# Skip device selection and use system default
./startVoice_api.sh --no-device-select

# Use a specific device by index
./startVoice_api.sh --device 2

# List available devices
./startVoice_api.sh --list-devices
```

#### 2. Local GPU Mode (uses distil-whisper/distil-large-v3)
```bash
# Start with device selection menu
./startVoice_gpu.sh

# Skip device selection and use system default
./startVoice_gpu.sh --no-device-select

# Use a specific device by index
./startVoice_gpu.sh --device 2

# List available devices
./startVoice_gpu.sh --list-devices
```

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
pip install sounddevice numpy scipy pynput pyperclip python-dotenv openai PyQt6

# Additional dependencies for GPU mode
pip install torch transformers accelerate
```

## Key Implementation Details

- **Modular Architecture**: Application is split into focused modules for better maintainability
- **Recording State**: Managed by AudioRecorder class
- **Audio Device Selection**: 
  - `get_pulseaudio_sources()` retrieves device info from PulseAudio with actual hardware names
  - `list_and_select_device()` presents interactive menu at startup
  - Selected device becomes default PulseAudio source via `pactl set-default-source`
- **Audio Device Detection**: `get_audio_device_info()` validates device capabilities and selects optimal sample rate
- **Audio Storage**: Temporarily saves WAV files in `outputs/` directory before transcription
- **Transcription**: Transcriber class supports both API and local GPU transcription
- **Text Input**: Uses `pyperclip` to copy text to clipboard and `pynput` to paste with Ctrl+Shift+V
- **Line Break Handling**: Automatically removes newlines from transcriptions for continuous text
- **Keyboard Detection**: Custom listener tracks Alt key state to detect Alt+R combination
- **Error Handling**: Graceful handling of API errors and audio device issues with automatic fallback
- **Sample Rate Detection**: Tests multiple rates (8000-96000 Hz) and selects best supported option

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

## Recording Indicator

The application includes a visual recording indicator built with PyQt6:
- Shows a "🔴 Recording" text overlay near the mouse cursor
- Appears at the mouse position when recording starts (with 20px offset)
- Features a pulsing opacity animation
- White text on dark semi-transparent background with rounded corners
- Automatically closes when recording stops

The indicator is implemented in `recording_indicator_qt.py` and requires PyQt6 to be installed.

## Important Notes

- Audio device selection menu appears at startup showing actual device names (AT2020, HyperX, etc.)
- Temporary audio files are cleaned up after transcription
- `.env` file is gitignored and must contain `OPENAI_API_KEY`
- Command-line arguments:
  - `--api`: Accepted for backwards compatibility but not needed (API is default)
  - `--local`: Use local GPU model instead of OpenAI API
  - `--no-device-select`: Skip device selection menu and use system default
  - `--device <index>`: Use specific device by index number
  - `--list-devices`: List available devices and exit
- Requirements.txt includes all dependencies including PyQt6 for the recording indicator
- Recording indicator requires PyQt6 but the app will still work if PyQt6 is not installed
- Uses sounddevice instead of PyAudio for better Linux compatibility
- Uses PulseAudio to get actual hardware device names instead of generic ALSA names
- Configuration variables are centralized in config.py
- Supports both float16 (GPU) and float32 (CPU) precision automatically

## Testing Utilities

The repository includes several test scripts:

- **test_audio_device_pulse.py**: Interactive device selection and testing with PulseAudio support
- **test_audio_device.py**: Device testing with recording and analysis
- **list_audio_devices.py**: Shows devices from multiple sources (ALSA, PulseAudio, sounddevice)
- **test_qt_indicator.py**: Tests the PyQt6 recording indicator
- **test_pynput_mouse.py**: Tests mouse position detection for indicator placement