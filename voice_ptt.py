#!/usr/bin/env python3
"""
Push-to-Talk Voice Typing with Whisper.cpp
Press Alt+R to start/stop recording
Transcribed text is automatically typed at cursor position
"""

import pyaudio
import wave
import requests
import os
import sys
import threading
import time
import pyperclip
from datetime import datetime
from pynput import keyboard
from pynput.keyboard import Key, Controller

# Configuration
WHISPER_SERVER = "http://localhost:50021/inference"
OUTPUT_DIR = "outputs"
SAMPLE_RATE = 44100  # AT2020USB-X native rate
CHANNELS = 1
CHUNK_SIZE = 1024
DEVICE_INDEX = 4  # AT2020USB-X device

# Global state
is_recording = False
recording_thread = None
frames = []
keyboard_controller = Controller()

def record_audio():
    """Record audio from AT2020USB-X microphone"""
    global frames, is_recording
    
    p = pyaudio.PyAudio()
    
    print("🎤 Recording started...")
    
    # Open stream with AT2020USB-X
    stream_params = {
        'format': pyaudio.paInt16,
        'channels': CHANNELS,
        'rate': SAMPLE_RATE,
        'input': True,
        'frames_per_buffer': CHUNK_SIZE,
        'input_device_index': DEVICE_INDEX
    }
    
    try:
        stream = p.open(**stream_params)
    except Exception as e:
        print(f"❌ Error opening audio stream: {e}")
        is_recording = False
        p.terminate()
        return
    
    frames = []
    
    # Record while flag is set
    while is_recording:
        try:
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            frames.append(data)
        except Exception as e:
            print(f"❌ Error reading audio: {e}")
            break
    
    # Stop and close stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    print("⏹️  Recording stopped")
    
    # Save and transcribe if we have audio
    if frames:
        save_and_transcribe()

def save_and_transcribe():
    """Save recorded audio and send to whisper server"""
    global frames
    
    if not frames:
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"recording_{timestamp}.wav")
    
    # Save WAV file
    p = pyaudio.PyAudio()
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))
    p.terminate()
    
    file_size = os.path.getsize(output_file)
    print(f"💾 Audio saved: {output_file} ({file_size:,} bytes)")
    
    # Send to whisper server
    print("🔄 Transcribing...")
    
    try:
        with open(output_file, 'rb') as f:
            files = {'file': (os.path.basename(output_file), f, 'audio/wav')}
            data = {
                'temperature': '0.0',
                'response-format': 'json'
            }
            
            response = requests.post(WHISPER_SERVER, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('text', '').strip()
                
                # Remove line breaks and clean up spacing
                text = text.replace('\n', ' ').replace('\r', ' ')
                # Collapse multiple spaces into single space
                text = ' '.join(text.split())
                
                if text:
                    print(f"📝 Transcription: {text}")
                    type_text(text)
                else:
                    print("⚠️  No text transcribed")
            else:
                print(f"❌ Server error: {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to whisper server")
        print(f"   Make sure server is running at {WHISPER_SERVER}")
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
    
    # Clean up audio file
    try:
        os.remove(output_file)
    except:
        pass

def type_text(text):
    """Copy text to clipboard and paste at current cursor position"""
    if not text:
        return
    
    print("📋 Copying to clipboard and pasting...")
    
    # Copy text to clipboard
    pyperclip.copy(text)
    
    # Small delay to ensure window focus
    time.sleep(0.1)
    
    # Paste using Ctrl+Shift+V (or Cmd+Shift+V on macOS)
    keyboard_controller.press(Key.ctrl)
    keyboard_controller.press(Key.shift)
    keyboard_controller.press('v')
    keyboard_controller.release('v')
    keyboard_controller.release(Key.shift)
    keyboard_controller.release(Key.ctrl)
    
    print("✅ Text pasted!")

def toggle_recording():
    """Toggle recording on/off"""
    global is_recording, recording_thread
    
    if not is_recording:
        # Start recording
        is_recording = True
        recording_thread = threading.Thread(target=record_audio)
        recording_thread.start()
    else:
        # Stop recording
        is_recording = False
        if recording_thread:
            recording_thread.join(timeout=2)

def on_press(key):
    """Handle key press events"""
    try:
        # Check for Alt+R combination
        if hasattr(key, 'char') and key.char == 'r':
            # Check if Alt is pressed
            if keyboard.Controller().alt_pressed:
                toggle_recording()
                return
    except AttributeError:
        pass
    
    # Check for Escape to quit
    if key == Key.esc:
        print("\n👋 Exiting...")
        global is_recording
        if is_recording:
            is_recording = False
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🎙️  Push-to-Talk Voice Typing")
    print("=" * 60)
    print()
    print("📌 Using: AT2020USB-X microphone (Device 4)")
    print(f"📡 Whisper server: {WHISPER_SERVER}")
    print()
    print("🎮 Controls:")
    print("  • Alt+R: Start/Stop recording")
    print("  • ESC: Exit")
    print()
    print("✨ Ready! Press Alt+R to start recording...")
    print("-" * 60)
    
    # Check if whisper server is running
    try:
        response = requests.get(WHISPER_SERVER.replace('/inference', '/health'), timeout=2)
    except:
        print("⚠️  Warning: Cannot reach whisper server")
        print(f"   Make sure it's running at {WHISPER_SERVER}")
        print()
    
    # Create a custom listener that tracks Alt key state
    class CustomListener(keyboard.Listener):
        def __init__(self):
            super().__init__(on_press=self.on_press, on_release=self.on_release)
            self.alt_pressed = False
            
        def on_press(self, key):
            if key in [Key.alt, Key.alt_l, Key.alt_r]:
                self.alt_pressed = True
            
            # Check for Alt+R
            if self.alt_pressed:
                try:
                    if hasattr(key, 'char') and key.char == 'r':
                        toggle_recording()
                except:
                    pass
            
            # Check for Escape
            if key == Key.esc:
                print("\n👋 Exiting...")
                global is_recording
                if is_recording:
                    is_recording = False
                return False
        
        def on_release(self, key):
            if key in [Key.alt, Key.alt_l, Key.alt_r]:
                self.alt_pressed = False
    
    # Start keyboard listener
    with CustomListener() as listener:
        listener.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        if is_recording:
            is_recording = False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if is_recording:
            is_recording = False