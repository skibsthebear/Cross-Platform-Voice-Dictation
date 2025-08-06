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