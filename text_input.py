#!/usr/bin/env python3
"""
Text input module for typing transcribed text
"""

import time
import pyperclip
from pynput.keyboard import Key, Controller


class TextTyper:
    def __init__(self):
        self.keyboard = Controller()
    
    def type_text(self, text):
        """Copy text to clipboard and paste at current cursor position"""
        if not text:
            return
        
        print("📋 Copying to clipboard and pasting...")
        
        # Copy text to clipboard
        pyperclip.copy(text)
        
        # Small delay to ensure window focus
        time.sleep(0.1)
        
        # Paste using Ctrl+Shift+V (or Cmd+Shift+V on macOS)
        self.keyboard.press(Key.ctrl)
        self.keyboard.press(Key.shift)
        self.keyboard.press('v')
        self.keyboard.release('v')
        self.keyboard.release(Key.shift)
        self.keyboard.release(Key.ctrl)
        
        print("✅ Text pasted!")