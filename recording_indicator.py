#!/usr/bin/env python3
"""
Recording indicator management module
"""

import os
import sys
import subprocess
import time
from pynput import mouse
from config import BASE_DIR, INDICATOR_OFFSET_X, INDICATOR_OFFSET_Y


class RecordingIndicatorManager:
    def __init__(self):
        self.process = None
        self.indicator_script = os.path.join(BASE_DIR, 'recording_indicator_qt.py')
        
    def show(self):
        """Show the recording indicator at mouse position"""
        try:
            # Get current mouse position
            mouse_x, mouse_y = self._get_mouse_position()
            
            # Start the PyQt indicator with mouse position
            if os.path.exists(self.indicator_script):
                self.process = subprocess.Popen(
                    [sys.executable, self.indicator_script, str(mouse_x), str(mouse_y)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # Check if process started successfully
                time.sleep(0.1)  # Brief pause to let it start
                if self.process.poll() is None:
                    print("🔴 Recording indicator started")
                else:
                    print("⚠️  Recording indicator failed to start")
                    self.process = None
            else:
                print(f"⚠️  Recording indicator script not found: {self.indicator_script}")
                
        except Exception as e:
            print(f"⚠️  Could not start recording indicator: {e}")
            self.process = None
    
    def hide(self):
        """Hide the recording indicator"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
                self.process = None
                print("⏹️  Recording indicator stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Recording indicator didn't stop, force killing...")
                try:
                    self.process.kill()
                    self.process.wait(timeout=1)
                except:
                    pass
                self.process = None
            except Exception as e:
                print(f"⚠️  Error stopping recording indicator: {e}")
                self.process = None
    
    def _get_mouse_position(self):
        """Get current mouse position"""
        try:
            mouse_controller = mouse.Controller()
            mouse_x, mouse_y = mouse_controller.position
            mouse_x = int(mouse_x) + INDICATOR_OFFSET_X
            mouse_y = int(mouse_y) + INDICATOR_OFFSET_Y
            print(f"🖱️  Mouse position: ({mouse_x}, {mouse_y})")
            return mouse_x, mouse_y
        except Exception as e:
            print(f"⚠️  Could not get mouse position: {e}")
            return 640, 360  # Default to center