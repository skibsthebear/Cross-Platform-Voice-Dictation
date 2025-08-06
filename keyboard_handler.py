#!/usr/bin/env python3
"""
Keyboard handler module for managing hotkeys
"""

from pynput import keyboard
from pynput.keyboard import Key
import time


class KeyboardHandler:
    def __init__(self, on_record_toggle=None, on_exit=None):
        self.on_record_toggle = on_record_toggle
        self.on_exit = on_exit
        self.alt_pressed = False
        self.listener = None
        self.first_esc_time = None
        self.exit_confirmation_active = False
        self.exit_confirmation_timeout = 2.0  # 2 seconds
        
    def start(self):
        """Start listening for keyboard events"""
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        
    def stop(self):
        """Stop listening for keyboard events"""
        if self.listener:
            self.listener.stop()
            
    def wait(self):
        """Wait for the listener to finish"""
        if self.listener:
            self.listener.join()
    
    def _on_press(self, key):
        """Handle key press events"""
        # Track Alt key state
        if key in [Key.alt, Key.alt_l, Key.alt_r]:
            self.alt_pressed = True
        
        # Check for Alt+R
        if self.alt_pressed:
            try:
                if hasattr(key, 'char') and key.char == 'r':
                    if self.on_record_toggle:
                        self.on_record_toggle()
            except:
                pass
        
        # Check for Escape - double-press confirmation
        if key == Key.esc:
            current_time = time.time()
            
            if not self.exit_confirmation_active:
                # First ESC press - start confirmation countdown
                self.first_esc_time = current_time
                self.exit_confirmation_active = True
                print("\n⚠️  Press ESC again within 2 seconds to exit")
            else:
                # Check if second ESC press is within timeout window
                if current_time - self.first_esc_time <= self.exit_confirmation_timeout:
                    # Second ESC press within timeout - exit
                    print("\n👋 Exiting...")
                    if self.on_exit:
                        self.on_exit()
                    return False  # Stop listener
                else:
                    # Second ESC press too late - restart confirmation
                    self.first_esc_time = current_time
                    print("\n⚠️  Press ESC again within 2 seconds to exit")
    
    def _on_release(self, key):
        """Handle key release events"""
        # Track Alt key state
        if key in [Key.alt, Key.alt_l, Key.alt_r]:
            self.alt_pressed = False
        
        # Reset exit confirmation if timeout has passed
        if self.exit_confirmation_active and self.first_esc_time:
            current_time = time.time()
            if current_time - self.first_esc_time > self.exit_confirmation_timeout:
                self.exit_confirmation_active = False
                self.first_esc_time = None