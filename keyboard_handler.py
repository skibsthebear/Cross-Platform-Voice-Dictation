#!/usr/bin/env python3
"""
Keyboard handler module for managing hotkeys
"""

from pynput import keyboard
from pynput.keyboard import Key


class KeyboardHandler:
    def __init__(self, on_record_toggle=None, on_exit=None):
        self.on_record_toggle = on_record_toggle
        self.on_exit = on_exit
        self.alt_pressed = False
        self.listener = None
        
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
        
        # Check for Escape
        if key == Key.esc:
            print("\n👋 Exiting...")
            if self.on_exit:
                self.on_exit()
            return False  # Stop listener
    
    def _on_release(self, key):
        """Handle key release events"""
        # Track Alt key state
        if key in [Key.alt, Key.alt_l, Key.alt_r]:
            self.alt_pressed = False