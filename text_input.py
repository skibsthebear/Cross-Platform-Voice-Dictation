#!/usr/bin/env python3
"""
Text input module for typing transcribed text
"""

import time
import pyperclip
from pynput.keyboard import Key, Controller
from config import SETTINGS


class TextTyper:
    def __init__(self):
        self.keyboard = Controller()
        self.ai_formatter = None
        
        # Initialize AI formatter if pass-through is enabled
        if SETTINGS.get('ai_passthrough', False):
            try:
                from ai_formatter_shared import AIFormatter
                self.ai_formatter = AIFormatter(
                    api_url=SETTINGS.get('ai_api_url'),
                    model=SETTINGS.get('ai_model'),
                    temperature=SETTINGS.get('ai_temperature', 0.3),
                    max_tokens=SETTINGS.get('ai_max_tokens', -1)
                )
                print("🤖 AI Pass-through enabled")
            except ImportError:
                print("⚠️  AI Pass-through enabled but AIFormatter not available")
                self.ai_formatter = None
    
    def type_text(self, text):
        """Copy text to clipboard and paste at current cursor position"""
        if not text:
            return
        
        # Process through AI if pass-through is enabled
        if self.ai_formatter and SETTINGS.get('ai_passthrough', False):
            print("🤖 Processing transcription through AI...")
            processed_text = self.ai_formatter.format_text(text)
            if processed_text:
                text = processed_text
                print("✨ AI processing complete")
            else:
                print("⚠️  AI processing failed, using original text")
        
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