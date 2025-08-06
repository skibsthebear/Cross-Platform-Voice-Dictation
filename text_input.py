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
        
        # Save current clipboard content
        original_clipboard = pyperclip.paste()
        
        try:
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
            
            # Small delay to ensure paste completes
            time.sleep(0.1)
            
            # Restore original clipboard content
            pyperclip.copy(original_clipboard)
            
            print("✅ Text pasted and clipboard restored!")
            
        except Exception as e:
            print(f"❌ Error during text pasting: {e}")
            # Restore original clipboard on error
            pyperclip.copy(original_clipboard)