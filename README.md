# Voice Typing & AI Fix - Cross-Platform Push-to-Talk Dictation and Text Formatting Tool

A powerful, cross-platform voice typing application with AI-powered text formatting. Features push-to-talk functionality to transcribe speech in real-time and intelligent text correction for highlighted text. Supports both OpenAI's Whisper API and local GPU-accelerated transcription using distil-whisper models.

## 🌟 Features

### Voice Typing (Alt+R)
- **Push-to-Talk Recording**: Press `Alt+R` to start/stop recording
- **Dual Transcription Modes**: 
  - **API Mode**: Uses OpenAI's Whisper API (requires API key)
  - **GPU Mode**: Uses local distil-whisper model for faster, offline transcription
- **Automatic Text Typing**: Transcribed text is automatically typed at your cursor position
- **Visual Recording Indicator**: Shows a floating indicator while recording
- **Smart Device Selection**: Choose your preferred microphone with actual device names
- **Long-Form Audio Support**: Handles recordings of any length

### AI Fix (Alt+G)
- **Intelligent Text Formatting**: Press `Alt+G` to format highlighted text
- **Context-Aware Processing**: Understands and maintains text structure
- **Smart Conversions**: Converts spoken formats like "dot com" → ".com"
- **Professional Formatting**: Fixes grammar, spelling, and punctuation
- **Email & List Formatting**: Adds appropriate line breaks for better structure
- **Real-Time Streaming**: Shows progress as AI processes your text

### General
- **Cross-Platform**: Works on Linux, Windows, and macOS
- **Dual Feature Access**: Both tools run simultaneously for seamless workflow

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

### AI Fix Requirements
- LM Studio running on `http://127.0.0.1:1234`
- Any LLM model loaded in LM Studio (default: liquid/lfm2-1.2b)

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

### 5. Start LM Studio (for AI Fix)

1. Download and install LM Studio from https://lmstudio.ai/
2. Download a model (e.g., liquid/lfm2-1.2b or any preferred model)
3. Start the local server on port 1234

### 6. Run the Application

Both startup scripts will launch Voice Typing AND AI Fix together:

#### API Mode (uses OpenAI API):

**Linux/macOS:**
```bash
./startVoice_api.sh
# Or directly: python voice_ptt.py
```

**Windows:**
```batch
startVoice_api.bat
REM Or with PowerShell: .\startVoice_api.ps1
```

#### GPU Mode (local transcription):

**Linux/macOS:**
```bash
./startVoice_gpu.sh
# Or directly: python voice_ptt.py --local
```

**Windows:**
```batch
startVoice_gpu.bat
REM Or with PowerShell: .\startVoice_gpu.ps1
```

To run AI Fix standalone:
```bash
python ai-fix.py  # All platforms
```

## 🎮 How to Use

### Voice Typing (Alt+R)
1. **Start the application** using one of the methods above
2. **Select your microphone** from the device list (or press Enter for default)
3. **Press `Alt+R`** to start recording (you'll see a red recording indicator)
4. **Speak clearly** into your microphone
5. **Press `Alt+R` again** to stop recording
6. The transcribed text will be **automatically typed** at your cursor position

### AI Fix (Alt+G)
1. **Highlight any text** you want to format or fix
2. **Press `Alt+G`** to trigger AI formatting
3. Watch the progress dots as AI processes your text
4. The highlighted text will be **automatically replaced** with the formatted version

### General
- **Press `ESC`** to exit the application
- Both features work simultaneously - use Alt+R for voice typing and Alt+G for text fixing

### Usage Tips
- **Voice Typing**: Push-to-talk design allows recordings of any length
- **AI Fix**: Works great for fixing voice-typed text, emails, or any text needing polish
- **Smart Formatting**: AI Fix understands context and formats appropriately:
  - Emails get proper paragraph breaks
  - Lists are formatted with line breaks
  - Spoken URLs/emails are converted (e.g., "john at gmail dot com" → "john@gmail.com")

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

### Windows-Specific Issues

#### Device Selection Automatically Skipped
This is normal behavior on Windows and WSL for compatibility:
- **Solution**: Use `python voice_ptt.py --device N` for manual device selection
- **Check devices**: Use `python voice_ptt.py --list-devices` to see available options

#### PowerShell Execution Policy Error
If you see "execution of scripts is disabled on this system":
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Batch Scripts Won't Run
- Make sure you're in the correct directory
- Try running from Command Prompt instead of PowerShell
- Use PowerShell scripts (.ps1) as an alternative

#### Virtual Environment Issues
- Windows: Use `whisper_venv\Scripts\activate.bat`
- PowerShell: Use `.\whisper_venv\Scripts\Activate.ps1`
- If activation fails, recreate the virtual environment

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
Default shortcuts (can be modified in code):
- `Alt+R` - Toggle voice recording
- `Alt+G` - Format highlighted text with AI
- `ESC` - Exit application

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

### AI Fix Settings
```python
# In ai-fix.py
api_url = "http://127.0.0.1:1234/v1/chat/completions"
model = "liquid/lfm2-1.2b"  # Change to your preferred model
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
├── ai-fix.py              # AI text formatting tool
├── config.py              # Configuration settings
├── audio_device.py        # Audio device management
├── audio_recorder.py      # Recording functionality
├── transcription.py       # Transcription engines (API/Local)
├── text_input.py          # Keyboard typing functionality
├── keyboard_handler.py    # Hotkey management
├── recording_indicator.py # Visual indicator management
├── recording_indicator_qt.py # Qt-based indicator UI
├── startVoice_api.sh      # API mode launcher (includes AI Fix)
├── startVoice_gpu.sh      # GPU mode launcher (includes AI Fix)
├── fix_cuda_error.sh      # CUDA troubleshooting script
├── requirements.txt       # Python dependencies
├── .example.env           # Example environment configuration
├── .env                   # API key configuration (create from .example.env)
└── outputs/              # Temporary audio storage
```

## 🔒 Privacy & Security

- **Voice Typing API Mode**: Audio is sent to OpenAI for transcription
- **Voice Typing GPU Mode**: All transcription happens locally on your machine
- **AI Fix**: Text is sent to your local LM Studio instance only
- Audio files are temporarily stored and immediately deleted after transcription
- Your API key is stored locally in `.env` and never shared
- No audio or text data is retained after processing
- AI Fix preserves clipboard content during operation

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

### AI Fix
- Local processing via LM Studio
- Real-time streaming responses
- Depends on loaded model size/speed
- No API costs

### System Requirements
- **Minimum**: 4GB RAM, any modern CPU
- **Recommended**: 8GB RAM, NVIDIA GPU with 4GB+ VRAM
- **Disk Space**: ~2GB for models and dependencies

## 🐛 Known Issues

1. **Experimental Chunking Warning**: Expected for long recordings, doesn't affect functionality
2. **CUDA Initialization**: May fail after suspend/resume - use fix script
3. **First GPU Run**: Takes time to download model (~1.5GB)
4. **AI Fix Clipboard**: Some applications may interfere with clipboard operations
5. **LM Studio Connection**: Ensure LM Studio server is running on port 1234

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
- LM Studio for local LLM hosting
- The open-source community for various dependencies

## 📞 Support

- **Issues**: Please report bugs via GitHub Issues
- **Feature Requests**: Open an issue with the `enhancement` label
- **Questions**: Use GitHub Discussions

---

**Note**: This tool is designed for productivity and accessibility. Please use responsibly and in accordance with all applicable laws and regulations.