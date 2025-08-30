#!/usr/bin/env python3
"""
Push-to-Talk Voice Typing with OpenAI API
Press Right Ctrl to start/stop recording
Transcribed text is automatically typed at cursor position
"""

import sys
import argparse
import threading
import time
import logging
from config import RECORD_KEY_COMBO, EXIT_KEY
from audio_device import list_and_select_device, list_all_devices, set_device, DeviceSelectionCancelled
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
        self._thread_lock = threading.Lock()  # Prevent concurrent thread creation
        self._recording_start_time = None
        
        # Setup logging for thread debugging
        logging.basicConfig(level=logging.DEBUG if '--debug' in sys.argv else logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
    def toggle_recording(self):
        """Toggle recording on/off with proper thread management"""
        print(f"\n🎛️  Toggle recording called. Current state: is_recording={self.recorder.is_recording}")
        
        with self._thread_lock:
            if not self.recorder.is_recording:
                # Check if there's an existing thread that needs cleanup
                if self.recording_thread and self.recording_thread.is_alive():
                    print("⚠️  Previous recording thread still running, cleaning up...")
                    self._force_cleanup_thread()
                
                print("▶️  Starting recording...")
                self._recording_start_time = time.time()
                
                # Start recording in a separate thread
                self.recording_thread = threading.Thread(
                    target=self._record_and_transcribe,
                    name="RecordingThread",
                    daemon=True  # Ensures thread dies with main process
                )
                self.recording_thread.start()
                print(f"🧵 Recording thread started: {self.recording_thread.is_alive()}")
                self.logger.info(f"Started recording thread: {self.recording_thread.name}")
                self.indicator.show()
            else:
                print("⏸️  Stopping recording...")
                self._stop_recording_thread()
                self.indicator.hide()
    
    def _stop_recording_thread(self):
        """Stop the recording thread with proper timeout and cleanup"""
        if self.recording_thread:
            # Calculate dynamic timeout based on recording duration
            recording_duration = time.time() - self._recording_start_time if self._recording_start_time else 0
            # Base timeout of 30s + 10s per minute of recording (for transcription time)
            dynamic_timeout = max(30, 30 + int(recording_duration / 60) * 10)
            
            # Signal the recording to stop
            self.recorder.should_stop = True
            print("🛑 Signaled recording to stop")
            print(f"⏳ Waiting for recording thread to finish (timeout: {dynamic_timeout}s)...")
            self.logger.info(f"Waiting for thread with {dynamic_timeout}s timeout")
            
            self.recording_thread.join(timeout=dynamic_timeout)
            
            if self.recording_thread.is_alive():
                print(f"⚠️  Recording thread still alive after {dynamic_timeout}s timeout!")
                self.logger.warning(f"Thread {self.recording_thread.name} timed out")
                self._force_cleanup_thread()
            else:
                print("✅ Recording thread finished normally")
                self.logger.info("Recording thread completed successfully")
                self.recording_thread = None
    
    def _force_cleanup_thread(self):
        """Force cleanup of abandoned recording thread"""
        if not self.recording_thread:
            return
            
        print("🧹 Force cleaning up abandoned recording thread...")
        self.logger.warning(f"Force cleaning up thread: {self.recording_thread.name}")
        
        # Force stop recording if it's still active
        if self.recorder.is_recording:
            self.recorder.is_recording = False
            self.recorder.should_stop = True
            print("🛑 Force stopped recording state")
            
            # Try to close audio stream if it exists
            try:
                if hasattr(self.recorder, 'stream') and self.recorder.stream:
                    self.recorder.stream.stop()
                    self.recorder.stream.close()
                    print("🔊 Force closed audio stream")
            except Exception as e:
                print(f"⚠️  Error force closing stream: {e}")
                self.logger.error(f"Error force closing stream: {e}")
        
        # Mark the thread as abandoned and create a new one if needed
        if self.recording_thread:
            self.logger.warning(f"Marking thread {self.recording_thread.name} as abandoned")
            # Note: We can't actually kill threads in Python, but we can mark them as abandoned
            # The daemon=True flag ensures they'll die with the main process
            self.recording_thread = None
        
        print("✅ Thread cleanup completed")
    
    def _record_and_transcribe(self):
        """Record audio and transcribe it with improved error handling"""
        thread_name = threading.current_thread().name
        print(f"🎙️  {thread_name} started")
        self.logger.info(f"Thread {thread_name} started recording and transcription")
        
        start_time = time.time()
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
            self.logger.error(f"Error in thread {thread_name}: {e}")
            import traceback
            traceback.print_exc()
            self.recorder.is_recording = False
        finally:
            # Ensure clean state regardless of how we exit
            self.recorder.is_recording = False
            self.recorder.should_stop = True
            duration = time.time() - start_time
            print(f"🏁 {thread_name} finished (duration: {duration:.1f}s)")
            self.logger.info(f"Thread {thread_name} completed in {duration:.1f}s")
    
    def cleanup(self):
        """Clean up resources with proper thread management"""
        print("🧹 Starting application cleanup...")
        self.logger.info("Starting application cleanup")
        
        # Stop recording if active
        if self.recorder.is_recording:
            print("🛑 Stopping active recording...")
            self.recorder.is_recording = False
            self.recorder.should_stop = True
        
        # Clean up recording thread
        if self.recording_thread and self.recording_thread.is_alive():
            print("⏳ Waiting for recording thread to finish...")
            self.recording_thread.join(timeout=10)  # Shorter timeout for cleanup
            if self.recording_thread.is_alive():
                print("⚠️  Recording thread didn't finish during cleanup")
                self.logger.warning("Recording thread abandoned during cleanup")
        
        # Hide indicator
        self.indicator.hide()
        print("✅ Cleanup completed")
        self.logger.info("Application cleanup completed")
        
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
        print("✨ Ready! Press Right Ctrl to start recording...")
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
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging for thread management')
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
        try:
            list_and_select_device()
        except DeviceSelectionCancelled:
            print("👋 Continuing with system default device...")
            print("   You can restart and use --device N for manual selection")
            print("   Or use --no-device-select to skip device selection")
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
    
    # Reload settings to pick up any changes
    from config import load_settings, SETTINGS
    SETTINGS.update(load_settings())
    
    # Show AI pass-through status
    if SETTINGS.get('ai_passthrough', False):
        print("🤖 AI Pass-through: ENABLED")
        print(f"   Model: {SETTINGS.get('ai_model', 'default')}")
    else:
        print("🤖 AI Pass-through: DISABLED")
    
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
