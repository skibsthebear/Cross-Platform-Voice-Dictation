#!/usr/bin/env python3
"""
Configuration settings for Voice Typing application
"""

import os

# Audio settings
OUTPUT_DIR = "outputs"
CHANNELS = 1
DTYPE = 'int16'  # 16-bit audio for WAV compatibility
DEFAULT_SAMPLE_RATE = 44100
PREFERRED_SAMPLE_RATES = [44100, 48000, 16000, 22050, 8000]

# Recording settings
BLOCKSIZE = 1024

# OpenAI settings
WHISPER_MODEL = "whisper-1"
TRANSCRIPTION_LANGUAGE = "en"  # Set to None for auto-detection

# Local Whisper settings
LOCAL_WHISPER_MODEL = "distil-whisper/distil-large-v3"
WHISPER_DEVICE = "cuda:0"  # or "cpu" or "mps" for Mac
WHISPER_TORCH_DTYPE = "float16"  # or "float32" for CPU

# Long-form transcription settings (for recordings > 30 seconds)
# These are used automatically when audio exceeds 30 seconds
WHISPER_CHUNK_LENGTH = 30  # Process in 30-second chunks
WHISPER_STRIDE_LENGTH = (5, 5)  # 5-second overlap between chunks for accuracy

# Auto-detect device if needed
try:
    import torch
    import warnings
    # Suppress CUDA initialization warnings
    warnings.filterwarnings('ignore', category=UserWarning, message='CUDA initialization')
    
    try:
        if torch.cuda.is_available():
            WHISPER_DEVICE = "cuda:0"
        elif torch.backends.mps.is_available():
            WHISPER_DEVICE = "mps"
        else:
            WHISPER_DEVICE = "cpu"
            WHISPER_TORCH_DTYPE = "float32"  # CPU requires float32
    except Exception:
        # If CUDA check fails, fall back to CPU
        WHISPER_DEVICE = "cpu"
        WHISPER_TORCH_DTYPE = "float32"
except ImportError:
    # If torch is not installed, default to CPU
    WHISPER_DEVICE = "cpu"
    WHISPER_TORCH_DTYPE = "float32"

# Keyboard shortcuts
RECORD_KEY_COMBO = "Alt+R"
EXIT_KEY = "ESC"

# UI settings
INDICATOR_OFFSET_X = 20
INDICATOR_OFFSET_Y = 20

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))