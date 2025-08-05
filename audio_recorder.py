#!/usr/bin/env python3
"""
Audio recording module
"""

import os
import time
import numpy as np
import sounddevice as sd
import scipy.io.wavfile
from datetime import datetime
from config import OUTPUT_DIR, DTYPE, BLOCKSIZE
from audio_device import get_audio_device_info


class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.should_stop = False  # Separate flag for signaling stop
        self.audio_data = []
        self.sample_rate = None
        self.channels = None
        self.device = None
        
    def start_recording(self):
        """Start recording audio"""
        if self.is_recording:
            return
            
        print("🎤 Recording started...")
        
        # Get device info
        self.device, self.sample_rate, self.channels = get_audio_device_info()
        
        # Clear previous recording
        self.audio_data = []
        self.is_recording = True
        self.should_stop = False  # Reset stop flag
        
        try:
            # Track callback counts for debugging
            self.callback_count = 0
            
            # Define callback function for audio stream
            def audio_callback(indata, frames, time_info, status):
                if status:
                    print(f"⚠️  Audio callback status: {status}")
                if self.is_recording:
                    self.audio_data.append(indata.copy())
                    self.callback_count += 1
                    if self.callback_count % 50 == 0:  # Log every ~0.5 seconds
                        print(f"🎤 Audio callback #{self.callback_count}, chunks collected: {len(self.audio_data)}")
            
            # Start recording stream
            self.stream = sd.InputStream(
                device=self.device,
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype=DTYPE,
                callback=audio_callback,
                blocksize=BLOCKSIZE
            )
            self.stream.start()
            print(f"🎵 Audio stream started: device={self.device}, channels={self.channels}, rate={self.sample_rate}")
            
        except Exception as e:
            print(f"❌ Error during recording: {e}")
            self.is_recording = False
            raise
    
    def stop_recording(self):
        """Stop recording and return the audio file path"""
        if not self.is_recording and not self.audio_data:
            print("⚠️  stop_recording called but no recording data")
            return None
            
        self.is_recording = False
        self.should_stop = True
        print("🛑 Setting is_recording to False")
        
        # Stop and close the stream
        if hasattr(self, 'stream'):
            print("🔊 Stopping audio stream...")
            self.stream.stop()
            self.stream.close()
            print("✅ Audio stream stopped")
            
        print("⏹️  Recording stopped")
        print(f"📊 Collected {len(self.audio_data)} audio chunks")
        
        # Save audio if we have data
        if self.audio_data:
            print("💾 Saving audio data...")
            return self.save_audio()
        else:
            print("⚠️  No audio data collected!")
        return None
    
    def save_audio(self):
        """Save recorded audio to file"""
        if not self.audio_data:
            return None
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(OUTPUT_DIR, f"recording_{timestamp}.wav")
        
        # Concatenate all audio chunks
        audio_array = np.concatenate(self.audio_data, axis=0)
        
        # Convert float audio to int16 if needed
        if audio_array.dtype != np.int16:
            audio_array = (audio_array * 32767).astype(np.int16)
        
        # Save WAV file
        scipy.io.wavfile.write(output_file, self.sample_rate, audio_array)
        
        file_size = os.path.getsize(output_file)
        print(f"💾 Audio saved: {output_file} ({file_size:,} bytes)")
        
        return output_file
    
    def cleanup_file(self, file_path):
        """Remove audio file after use"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"⚠️  Could not remove file {file_path}: {e}")