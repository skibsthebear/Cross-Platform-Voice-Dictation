#!/usr/bin/env python3
"""
Transcription module supporting both OpenAI API and local Whisper models
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from config import (
    WHISPER_MODEL, TRANSCRIPTION_LANGUAGE,
    LOCAL_WHISPER_MODEL, WHISPER_DEVICE, WHISPER_TORCH_DTYPE,
    WHISPER_CHUNK_LENGTH, WHISPER_STRIDE_LENGTH
)

# Load environment variables
load_dotenv()


class Transcriber:
    def __init__(self, use_local=False):
        self.use_local = use_local
        self.client = None
        self.pipe = None
        
        if use_local:
            self._initialize_local_model()
        else:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your-api-key-here':
            raise ValueError("OPENAI_API_KEY not set in .env file")
        
        self.client = OpenAI(api_key=api_key)
        print("📡 OpenAI client initialized")
    
    def _initialize_local_model(self):
        """Initialize local Whisper model using Hugging Face"""
        try:
            import torch
            from transformers import pipeline
            from transformers.utils import is_flash_attn_2_available
            import warnings
            
            # Suppress CUDA warnings
            warnings.filterwarnings('ignore', category=UserWarning, message='CUDA initialization')
            
            # Try to use configured device, fall back to CPU if needed
            device = WHISPER_DEVICE
            torch_dtype = torch.float16 if WHISPER_TORCH_DTYPE == "float16" else torch.float32
            
            # Check if we need to fall back to CPU
            try:
                if device.startswith("cuda") and not torch.cuda.is_available():
                    print("⚠️  CUDA requested but not available, falling back to CPU")
                    device = "cpu"
                    torch_dtype = torch.float32
            except Exception:
                device = "cpu"
                torch_dtype = torch.float32
            
            print(f"🔄 Loading local Whisper model: {LOCAL_WHISPER_MODEL}")
            print(f"   Device: {device}")
            
            # Determine attention implementation
            model_kwargs = {"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"}
            
            # Create pipeline
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=LOCAL_WHISPER_MODEL,
                torch_dtype=torch_dtype,
                device=device,
                model_kwargs=model_kwargs,
            )
            
            print("✅ Local Whisper model loaded successfully")
            if device == "cpu":
                print("   Note: Running on CPU - transcription will be slower than GPU")
            
        except ImportError as e:
            raise ImportError(f"Missing dependencies for local model: {e}\nPlease install: pip install torch transformers accelerate")
        except Exception as e:
            raise Exception(f"Failed to initialize local model: {e}")
    
    def transcribe_audio(self, audio_file_path):
        """Transcribe audio file using selected method"""
        if self.use_local:
            return self._transcribe_local(audio_file_path)
        else:
            return self._transcribe_api(audio_file_path)
    
    def _transcribe_api(self, audio_file_path):
        """Transcribe audio file using OpenAI Whisper API"""
        if not self.client:
            print("❌ OpenAI client not initialized")
            return None
        
        if not os.path.exists(audio_file_path):
            print(f"❌ Audio file not found: {audio_file_path}")
            return None
        
        try:
            print("🔄 Transcribing using OpenAI API...")
            
            with open(audio_file_path, 'rb') as audio:
                # Using the Whisper API
                response = self.client.audio.transcriptions.create(
                    model=WHISPER_MODEL,
                    file=audio,
                    response_format="text",
                    language=TRANSCRIPTION_LANGUAGE if TRANSCRIPTION_LANGUAGE else None
                )
                
                # Clean up the transcription
                text = response.strip() if isinstance(response, str) else response
                
                # Remove line breaks and clean up spacing
                text = text.replace('\n', ' ').replace('\r', ' ')
                # Collapse multiple spaces into single space
                text = ' '.join(text.split())
                
                print(f"📝 Transcription: {text}")
                return text
                
        except Exception as e:
            print(f"❌ Error during API transcription: {e}")
            return None
    
    def _transcribe_local(self, audio_file_path):
        """Transcribe audio file using local Whisper model"""
        if not self.pipe:
            print("❌ Local model not initialized")
            return None
        
        if not os.path.exists(audio_file_path):
            print(f"❌ Audio file not found: {audio_file_path}")
            return None
        
        try:
            print("🔄 Transcribing using local model...")
            print(f"   Audio file size: {os.path.getsize(audio_file_path):,} bytes")
            
            # Run the pipeline
            print("   Running pipeline...")
            # Enable proper long-form transcription for recordings > 30s
            outputs = self.pipe(
                audio_file_path,
                return_timestamps=True,  # Required for long-form audio > 30s
                chunk_length_s=WHISPER_CHUNK_LENGTH,  # Process in 30-second chunks
                stride_length_s=WHISPER_STRIDE_LENGTH,  # Overlap for better accuracy
            )
            
            print("   Pipeline completed")
            
            # Extract text from output - handle both timestamp and non-timestamp formats
            if isinstance(outputs, dict) and "text" in outputs:
                text = outputs["text"].strip()
            elif isinstance(outputs, dict) and "chunks" in outputs:
                # Handle chunked output with timestamps
                text = " ".join(chunk["text"] for chunk in outputs["chunks"]).strip()
            else:
                # Fallback
                text = str(outputs).strip()
            
            print(f"   Raw transcription: {text[:100]}..." if len(text) > 100 else f"   Raw transcription: {text}")
            
            # Remove line breaks and clean up spacing
            text = text.replace('\n', ' ').replace('\r', ' ')
            # Collapse multiple spaces into single space
            text = ' '.join(text.split())
            
            print(f"📝 Transcription: {text}")
            return text
            
        except Exception as e:
            print(f"❌ Error during local transcription: {e}")
            return None
    
    def is_available(self):
        """Check if transcription service is available"""
        if self.use_local:
            return self.pipe is not None
        else:
            return self.client is not None