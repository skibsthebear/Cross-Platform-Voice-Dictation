#!/usr/bin/env python3
"""
Push-to-Talk Voice Typing with OpenAI API
Press Alt+R to start/stop recording
Transcribed text is automatically typed at cursor position
"""

import sys
import argparse
import threading
from config import RECORD_KEY_COMBO, EXIT_KEY
from audio_device import list_and_select_device, list_all_devices, set_device
from platform_detection import detect_operating_system, should_skip_device_selection
from audio_recorder import AudioRecorder
from transcription import Transcriber
from text_input import TextTyper
from keyboard_handler import KeyboardHandler
from recording_indicator import RecordingIndicatorManager


class VoiceTypingApp:
    def __init__(self, use_local=False):
        self.recorder = AudioRecorder()
        self.transcriber = Transcriber(use_local=use_local)
        self.text_typer = TextTyper()
        self.indicator = RecordingIndicatorManager()
        self.keyboard_handler = KeyboardHandler(
            on_record_toggle=self.toggle_recording,
            on_exit=self.cleanup
        )
        self.recording_thread = None
        self.use_local = use_local
        
    def toggle_recording(self):
        """Toggle recording on/off"""
        print(f"\n🎛️  Toggle recording called. Current state: is_recording={self.recorder.is_recording}")
        
        if not self.recorder.is_recording:
            print("▶️  Starting recording...")
            # Start recording in a separate thread
            self.recording_thread = threading.Thread(target=self._record_and_transcribe)
            self.recording_thread.start()
            print(f"🧵 Recording thread started: {self.recording_thread.is_alive()}")
            self.indicator.show()
        else:
            print("⏸️  Stopping recording...")
            # Stop recording - signal the recording thread to stop
            if self.recording_thread:
                # Signal the recording to stop
                self.recorder.should_stop = True
                print("🛑 Signaled recording to stop")
                print("⏳ Waiting for recording thread to finish...")
                self.recording_thread.join(timeout=5)
                if self.recording_thread.is_alive():
                    print("⚠️  Recording thread still alive after timeout!")
                else:
                    print("✅ Recording thread finished")
            self.indicator.hide()
    
    def _record_and_transcribe(self):
        """Record audio and transcribe it"""
        print("🎙️  _record_and_transcribe thread started")
        try:
            # Start recording
            print("📍 Starting recorder...")
            self.recorder.start_recording()
            
            # Wait until recording is stopped
            print("⏳ Waiting for recording to stop...")
            wait_count = 0
            while self.recorder.is_recording and not self.recorder.should_stop:
                threading.Event().wait(0.1)
                wait_count += 1
                if wait_count % 10 == 0:  # Log every second
                    print(f"   Still recording... ({wait_count/10:.1f}s)")
            
            print("📍 Recording loop ended, stopping recorder...")
            # Stop recording and get the audio file
            audio_file = self.recorder.stop_recording()
            
            if audio_file:
                print(f"📄 Audio file saved: {audio_file}")
                # Transcribe the audio
                print("🔤 Starting transcription...")
                text = self.transcriber.transcribe_audio(audio_file)
                
                if text:
                    # Type the transcribed text
                    print(f"✍️  Typing text: {text[:50]}...")
                    self.text_typer.type_text(text)
                else:
                    print("⚠️  No text transcribed")
                
                # Clean up the audio file
                print("🗑️  Cleaning up audio file...")
                self.recorder.cleanup_file(audio_file)
            else:
                print("❌ No audio file returned from recorder!")
                
        except Exception as e:
            print(f"❌ Error during recording/transcription: {e}")
            import traceback
            traceback.print_exc()
            self.recorder.is_recording = False
        
        print("🏁 _record_and_transcribe thread finished")
    
    def cleanup(self):
        """Clean up resources"""
        if self.recorder.is_recording:
            self.recorder.is_recording = False
        self.indicator.hide()
        
    def run(self):
        """Run the application"""
        print()
        if self.use_local:
            print("🖥️  Using Local Whisper Model")
        else:
            print("📡 Using OpenAI Whisper API")
        print()
        print("🎮 Controls:")
        print(f"  • {RECORD_KEY_COMBO}: Start/Stop recording")
        print(f"  • {EXIT_KEY}: Exit")
        print()
        print("✨ Ready! Press Alt+R to start recording...")
        print("-" * 60)
        
        # Start keyboard listener
        self.keyboard_handler.start()
        self.keyboard_handler.wait()


def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Push-to-Talk Voice Typing')
    parser.add_argument('--api', action='store_true', 
                        help='Use OpenAI API for transcription (included for backwards compatibility)')
    parser.add_argument('--local', action='store_true',
                        help='Use local Whisper model instead of OpenAI API')
    parser.add_argument('--list-devices', action='store_true', 
                        help='List available audio devices and exit')
    parser.add_argument('--device', type=int, 
                        help='Use specific audio device by index')
    parser.add_argument('--no-device-select', action='store_true', 
                        help='Skip device selection and use system default')
    args = parser.parse_args()
    
    # List devices if requested
    if args.list_devices:
        list_all_devices()
        sys.exit(0)
    
    # Detect platform for intelligent defaults
    should_skip = should_skip_device_selection()
    
    # Set default device if specified
    if args.device is not None:
        if should_skip:
            print("⚠️  Manual device selection on Windows/WSL may have compatibility issues")
        if not set_device(args.device):
            sys.exit(1)
    elif not args.no_device_select and not should_skip:
        # Show device selection menu unless skipped or auto-skipped for Windows/WSL
        print("=" * 60)
        print("🎙️  Push-to-Talk Voice Typing")
        print("=" * 60)
        list_and_select_device()
    elif should_skip and not args.no_device_select:
        # Auto-skip for Windows/WSL with informative messages
        print("=" * 60)
        print("🎙️  Push-to-Talk Voice Typing")
        print("=" * 60)
        print("⚠️  Device selection automatically skipped on Windows/WSL")
        print("   Use --device N for manual device selection")
        print("   Use --list-devices to see available devices")
    
    if args.no_device_select or args.device is not None or should_skip:
        # Only show header if we didn't show device selection
        if not should_skip:  # Don't duplicate header for Windows/WSL
            print("=" * 60)
            print("🎙️  Push-to-Talk Voice Typing")
            print("=" * 60)
    
    # Show platform information
    platform_info = f"Platform: {detect_operating_system().title()}"
    if should_skip:
        platform_info += " (Device selection auto-skipped)"
    print(platform_info)
    print("")
    
    # Create and run the application
    try:
        app = VoiceTypingApp(use_local=args.local)
        app.run()
    except ValueError as e:
        print(f"❌ Error: {e}")
        if not args.local:
            print("   Please edit .env and add your OpenAI API key")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        app.cleanup()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if 'app' in locals():
            app.cleanup()


if __name__ == "__main__":
    main()
