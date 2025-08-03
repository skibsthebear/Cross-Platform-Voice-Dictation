# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Push-to-Talk Voice Typing application that uses Whisper.cpp for speech-to-text transcription. The application records audio when Alt+R is pressed and automatically types the transcribed text at the cursor position.

## Architecture

### Core Components

1. **voice_ptt.py** - Main application script that:
   - Captures audio from AT2020USB-X microphone (device index 4) at 44100Hz
   - Uses pynput for keyboard shortcuts (Alt+R) and text typing
   - Sends audio to local Whisper.cpp server for transcription
   - Types transcribed text using pynput's keyboard Controller

### Dependencies & External Services

- **Whisper.cpp Server**: Must be running locally at `http://localhost:50021/inference`
  - The whisper.cpp directory contains the server but is gitignored
  - Server accepts WAV files and returns JSON with transcribed text
  
- **Audio Configuration**: 
  - Hardcoded to use AT2020USB-X microphone at device index 4
  - Sample rate: 44100 Hz, Mono channel

## Development Commands

### Running the Complete System

```bash
# Start both Whisper server and voice typing application
./start_voice.sh
```

This will:
1. Start the Whisper.cpp server on port 50021 with the large-v3-turbo model
2. Activate the virtual environment and start the voice typing application
3. Handle cleanup when you press Ctrl+C

### Running Components Individually

```bash
# Start Whisper server manually
./whisper.cpp/build/bin/whisper-server -m ./whisper.cpp/models/ggml-large-v3-turbo-q8_0.bin --host 0.0.0.0 --port 50021 --convert

# In another terminal, run the voice typing application
source whisper_venv/bin/activate
python voice_ptt.py
```

### Virtual Environment

```bash
# Create/recreate virtual environment
python -m venv whisper_venv

# Activate environment
source whisper_venv/bin/activate

# Install dependencies (if requirements.txt exists)
pip install pyaudio pynput requests pyperclip
```

## Key Implementation Details

- **Recording State**: Global `is_recording` flag controls audio capture thread
- **Audio Storage**: Temporarily saves WAV files in `outputs/` directory before sending to server
- **Text Input**: Uses `pyperclip` to copy text to clipboard and `pynput` to paste with Ctrl+Shift+V
- **Line Break Handling**: Automatically removes newlines from transcriptions for continuous text
- **Keyboard Detection**: Custom listener tracks Alt key state to detect Alt+R combination
- **Error Handling**: Graceful handling of server connection errors and audio device issues

## Important Notes

- The whisper.cpp and ydotool directories are gitignored (whisper.cpp contains the server, ydotool is unused)
- Audio device index (4) is hardcoded for AT2020USB-X microphone
- Server endpoint is hardcoded to localhost:50021
- Temporary audio files are cleaned up after transcription