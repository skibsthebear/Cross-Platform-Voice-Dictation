#!/usr/bin/env python3
"""
Text input module for typing transcribed text
"""

import time
import sys
import pyperclip
from pynput.keyboard import Key, Controller

# Platform-specific paste behavior
if sys.platform == "win32":
    # Windows typically uses Ctrl+V
    PASTE_KEYS = [Key.ctrl_l, 'v']
elif sys.platform == "darwin":
    # macOS uses Cmd+Shift+V for some terminals
    PASTE_KEYS = [Key.cmd, Key.shift, 'v']
else:
    # Linux default
    PASTE_KEYS = [Key.ctrl_l, Key.shift, 'v']


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
        
        # Paste using platform-specific keys
        if sys.platform == "win32":
            # Windows: Use Ctrl+V
            self.keyboard.press(Key.ctrl_l)
            self.keyboard.press('v')
            self.keyboard.release('v')
            self.keyboard.release(Key.ctrl_l)
        else:
            # Linux/Mac: Use Ctrl+Shift+V for terminal compatibility
            self.keyboard.press(Key.ctrl_l)
            self.keyboard.press(Key.shift)
            self.keyboard.press('v')
            self.keyboard.release('v')
            self.keyboard.release(Key.shift)
            self.keyboard.release(Key.ctrl_l)
        
        print("✅ Text pasted!")