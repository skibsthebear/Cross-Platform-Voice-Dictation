# Voice Typing - Cross-Platform Push-to-Talk Dictation Tool

A powerful, cross-platform voice typing application that uses push-to-talk functionality to transcribe speech in real-time. Supports both OpenAI's Whisper API and local GPU-accelerated transcription using distil-whisper models.

## 🌟 Features

- **Push-to-Talk Recording**: Press `Alt+R` to start/stop recording
- **Dual Transcription Modes**: 
  - **API Mode**: Uses OpenAI's Whisper API (requires API key)
  - **GPU Mode**: Uses local distil-whisper model for faster, offline transcription
- **Automatic Text Typing**: Transcribed text is automatically typed at your cursor position
- **Visual Recording Indicator**: Shows a floating indicator while recording
- **Smart Device Selection**: Choose your preferred microphone with actual device names
- **Long-Form Audio Support**: Handles recordings of any length
- **Cross-Platform**: Works on Linux, Windows, and macOS

## 📋 Requirements

### Common Requirements
- Python 3.8 or higher
- Virtual environment support
- Microphone/audio input device

### API Mode Requirements
- OpenAI API key
- Internet connection

### GPU Mode Requirements
- NVIDIA GPU with CUDA support (recommended) or CPU
- ~1.5GB disk space for model download
- PyTorch with CUDA support

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/voice_typing.git
cd voice_typing
```

### 2. Create Virtual Environment
```bash
python -m venv whisper_venv
source whisper_venv/bin/activate  # On Windows: whisper_venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up API Key (for API Mode)

#### Option 1: Copy the example file (recommended)
```bash
cp .example.env .env
# Then edit .env and replace 'your-api-key-here' with your actual API key
```

#### Option 2: Create manually
```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

Replace `your-api-key-here` with your actual OpenAI API key from https://platform.openai.com/api-keys

### 5. Run the Application

#### API Mode (uses OpenAI API):
```bash
./startVoice_api.sh
# Or directly: python voice_ptt.py
```

#### GPU Mode (local transcription):
```bash
./startVoice_gpu.sh
# Or directly: python voice_ptt.py --local
```

## 🎮 How to Use

1. **Start the application** using one of the methods above
2. **Select your microphone** from the device list (or press Enter for default)
3. **Press `Alt+R`** to start recording (you'll see a red recording indicator)
4. **Speak clearly** into your microphone
5. **Press `Alt+R` again** to stop recording
6. The transcribed text will be **automatically typed** at your cursor position
7. **Press `ESC`** to exit the application

### Recording Tips
- The application uses push-to-talk, so hold the recording as long as needed
- For best results, speak clearly and minimize background noise
- The recording indicator shows when audio is being captured
- Long recordings (>30 seconds) are automatically handled with chunking

## 🛠️ Installation Guide

### Detailed Setup for API Mode

1. **Get OpenAI API Key**:
   - Visit https://platform.openai.com/api-keys
   - Create a new API key
   - Copy the key (it starts with `sk-`)

2. **Configure Environment**:
   ```bash
   # Copy the example environment file
   cp .example.env .env
   
   # Edit .env and add your API key
   nano .env  # or use your preferred editor
   ```
   
   The `.example.env` file contains:
   ```env
   # OpenAI API Configuration
   OPENAI_API_KEY=your-api-key-here
   ```

3. **Test API Connection**:
   ```bash
   python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API key configured!' if os.getenv('OPENAI_API_KEY') else 'API key missing!')"
   ```

### Detailed Setup for GPU Mode

1. **Check CUDA Installation**:
   ```bash
   nvidia-smi  # Should show your GPU
   nvcc --version  # Should show CUDA version
   ```

2. **Install PyTorch with CUDA** (if needed):
   ```bash
   # For CUDA 12.x
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   
   # For CUDA 11.x
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

3. **First Run** (downloads model ~1.5GB):
   ```bash
   ./startVoice_gpu.sh
   # Model will be downloaded on first use
   ```

## 🔧 Troubleshooting

### CUDA Errors

#### "CUDA unknown error" Fix
This is a common issue after system suspend/resume. Try these solutions in order:

1. **Quick Fix** (no reboot required):
   ```bash
   sudo ./fix_cuda_error.sh
   # Or manually:
   sudo rmmod nvidia_uvm
   sudo modprobe nvidia_uvm
   ```

2. **Reboot System** (most reliable):
   ```bash
   sudo reboot
   ```

3. **Check nvidia-modprobe**:
   ```bash
   sudo apt install nvidia-modprobe  # Ubuntu/Debian
   ```

#### PyTorch Not Detecting GPU
If PyTorch can't see your GPU:

1. **Check CUDA environment**:
   ```bash
   echo $CUDA_HOME
   echo $LD_LIBRARY_PATH
   ```

2. **Set CUDA paths** (add to ~/.bashrc):
   ```bash
   export CUDA_HOME=/usr/local/cuda
   export PATH=$CUDA_HOME/bin:$PATH
   export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
   ```

3. **Reinstall PyTorch** for your CUDA version:
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

### Audio Device Issues

#### No Audio Devices Found
1. Check PulseAudio is running:
   ```bash
   pactl info
   ```

2. List all audio sources:
   ```bash
   pactl list sources short
   ```

3. Use fallback device selection:
   ```bash
   python voice_ptt.py --no-device-select
   ```

#### Wrong Device Selected
Use specific device by index:
```bash
python voice_ptt.py --device 2
```

List all devices:
```bash
python voice_ptt.py --list-devices
```

### Recording Issues

#### No Audio Recorded
- Check microphone permissions
- Ensure microphone is not muted
- Try a different audio device

#### Recording Stops Immediately
- Check console logs for errors
- Ensure no other application is using the microphone
- Try running with sudo if permission issues

## 🐧 Linux Setup: Global Command Access

Add a global command to run voice typing from anywhere:

1. **Create the launch script**:
   ```bash
   mkdir -p ~/bin
   cat > ~/bin/voice_ptt << 'EOF'
   #!/bin/bash
   VOICE_DIR="/path/to/voice_typing"
   cd "$VOICE_DIR"
   ./startVoice_gpu.sh --device 4  # Adjust device number as needed
   EOF
   ```

2. **Make it executable**:
   ```bash
   chmod +x ~/bin/voice_ptt
   ```

3. **Add to PATH** (in ~/.bashrc):
   ```bash
   export PATH="$HOME/bin:$PATH"
   ```

4. **Use from anywhere**:
   ```bash
   voice_ptt  # Launches voice typing from any directory
   ```

## ⚙️ Configuration

### Keyboard Shortcuts
Edit `config.py` to change default shortcuts:
```python
RECORD_KEY_COMBO = "Alt+R"  # Change to your preference
EXIT_KEY = "ESC"
```

### Audio Settings
```python
CHANNELS = 1  # Mono recording
DTYPE = 'int16'  # Audio format
DEFAULT_SAMPLE_RATE = 44100
```

### GPU Settings
```python
LOCAL_WHISPER_MODEL = "distil-whisper/distil-large-v3"
WHISPER_DEVICE = "cuda:0"  # or "cpu" or "mps" for Mac
```

### Command Line Options
```bash
--local              # Use local GPU model instead of API
--device <number>    # Use specific audio device
--no-device-select   # Skip device selection menu
--list-devices       # List available devices and exit
```

## 📁 Project Structure

```
voice_typing/
├── voice_ptt.py           # Main application entry point
├── config.py              # Configuration settings
├── audio_device.py        # Audio device management
├── audio_recorder.py      # Recording functionality
├── transcription.py       # Transcription engines (API/Local)
├── text_input.py          # Keyboard typing functionality
├── keyboard_handler.py    # Hotkey management
├── recording_indicator.py # Visual indicator management
├── recording_indicator_qt.py # Qt-based indicator UI
├── startVoice_api.sh      # API mode launcher
├── startVoice_gpu.sh      # GPU mode launcher
├── fix_cuda_error.sh      # CUDA troubleshooting script
├── requirements.txt       # Python dependencies
├── .example.env           # Example environment configuration
├── .env                   # API key configuration (create from .example.env)
└── outputs/              # Temporary audio storage
```

## 🔒 Privacy & Security

- **API Mode**: Audio is sent to OpenAI for transcription
- **GPU Mode**: All transcription happens locally on your machine
- Audio files are temporarily stored and immediately deleted after transcription
- Your API key is stored locally in `.env` and never shared
- No audio data is retained after transcription

## 📊 Performance

### API Mode
- Requires internet connection
- ~2-5 second latency depending on connection
- High accuracy
- Costs per API usage

### GPU Mode  
- Completely offline
- <1 second latency with GPU
- Good accuracy with distil-whisper
- Free after initial setup

### System Requirements
- **Minimum**: 4GB RAM, any modern CPU
- **Recommended**: 8GB RAM, NVIDIA GPU with 4GB+ VRAM
- **Disk Space**: ~2GB for models and dependencies

## 🐛 Known Issues

1. **Experimental Chunking Warning**: Expected for long recordings, doesn't affect functionality
2. **CUDA Initialization**: May fail after suspend/resume - use fix script
3. **First GPU Run**: Takes time to download model (~1.5GB)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/voice_typing.git
cd voice_typing

# Create development branch
git checkout -b feature/your-feature

# Install in development mode
pip install -e .
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI Whisper for transcription technology
- Hugging Face for distil-whisper models
- The open-source community for various dependencies

## 📞 Support

- **Issues**: Please report bugs via GitHub Issues
- **Feature Requests**: Open an issue with the `enhancement` label
- **Questions**: Use GitHub Discussions

---

**Note**: This tool is designed for productivity and accessibility. Please use responsibly and in accordance with all applicable laws and regulations.