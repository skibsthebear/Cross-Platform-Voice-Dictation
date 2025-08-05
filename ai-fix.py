#!/usr/bin/env python3
"""
AI-powered text fixing tool that monitors for Alt+G hotkey,
captures highlighted text, sends it to LM Studio for processing,
and replaces the selection with the AI-improved version.
"""

import time
import json
import sys
from typing import Optional
import requests
import pyperclip
from pynput import keyboard
from pynput.keyboard import Key, Controller


class KeyboardHandler:
    """Handles keyboard input and hotkey detection"""
    
    def __init__(self, on_fix_trigger=None, on_exit=None):
        self.on_fix_trigger = on_fix_trigger
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
        
        # Check for Alt+G
        if self.alt_pressed:
            try:
                if hasattr(key, 'char') and key.char == 'g':
                    if self.on_fix_trigger:
                        self.on_fix_trigger()
            except:
                pass
        
        # Check for Escape
        if key == Key.esc:
            print("\n👋 Exiting AI Fix...")
            if self.on_exit:
                self.on_exit()
            return False  # Stop listener
    
    def _on_release(self, key):
        """Handle key release events"""
        # Track Alt key state
        if key in [Key.alt, Key.alt_l, Key.alt_r]:
            self.alt_pressed = False


class TextCapture:
    """Captures highlighted text from the system"""
    
    def __init__(self):
        self.keyboard = Controller()
        
    def get_highlighted_text(self) -> Optional[str]:
        """Capture currently highlighted text"""
        # Save current clipboard content
        original_clipboard = pyperclip.paste()
        
        try:
            # Clear clipboard to ensure we get fresh content
            pyperclip.copy("")
            
            # Simulate Ctrl+C to copy highlighted text
            self.keyboard.press(Key.ctrl)
            self.keyboard.press('c')
            self.keyboard.release('c')
            self.keyboard.release(Key.ctrl)
            
            # Small delay to ensure copy operation completes
            time.sleep(0.1)
            
            # Get the copied text
            captured_text = pyperclip.paste()
            
            # Restore original clipboard content
            pyperclip.copy(original_clipboard)
            
            # Return captured text if it's not empty
            return captured_text if captured_text else None
            
        except Exception as e:
            print(f"❌ Error capturing text: {e}")
            # Restore original clipboard on error
            pyperclip.copy(original_clipboard)
            return None


class AIFormatter:
    """Handles communication with LM Studio API"""
    
    def __init__(self, api_url="http://127.0.0.1:1234/v1/chat/completions", model="liquid/lfm2-1.2b"):
        self.api_url = api_url
        self.model = model
        self.headers = {"Content-Type": "application/json"}
        
    def format_text(self, text: str, system_prompt: str = None) -> Optional[str]:
        """Send text to AI for formatting and return the result"""
        # Create a combined user message with explicit instructions
        user_message = (
            "You will always only reply with the formatted text. Your sole job is to format the text. "
            "Read the entire text carefully and understand the context before formatting. "
            "Add appropriate line breaks to separate paragraphs, sections, or logical units of text. "
            "Fix grammar, spelling, punctuation, and style issues. "
            "Convert spoken-out formats to their proper syntax (e.g., 'dot com' to '.com', 'readme dot md' to 'readme.md', "
            "'w w w dot' to 'www.', 'at symbol' to '@', 'hashtag' to '#'). "
            "For emails, add proper line breaks between greeting, body paragraphs, and signature. "
            "For lists, ensure each item is on a new line. "
            "Make the text clear, professional, and properly structured. "
            f"This is the text the user wants you to format: \"{text}\""
        )
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.3,
            "max_tokens": -1,
            "stream": True
        }
        
        try:
            print("🤖 Sending to AI for processing...")
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                stream=True
            )
            
            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return None
            
            # Accumulate the streamed response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]  # Remove "data: " prefix
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                full_response += content
                                # Print progress indicator
                                if content:
                                    print(".", end="", flush=True)
                        except json.JSONDecodeError:
                            continue
            
            print()  # New line after progress dots
            return full_response.strip()
            
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to LM Studio. Make sure it's running on port 1234.")
            return None
        except Exception as e:
            print(f"❌ Error during AI processing: {e}")
            return None


class TextReplacer:
    """Replaces selected text with new content"""
    
    def __init__(self):
        self.keyboard = Controller()
        
    def replace_selection(self, new_text: str):
        """Replace currently selected text with new text"""
        if not new_text:
            return
        
        # Copy new text to clipboard
        pyperclip.copy(new_text)
        
        # Small delay to ensure focus
        time.sleep(0.1)
        
        # Paste to replace selection (Ctrl+V)
        self.keyboard.press(Key.ctrl)
        self.keyboard.press('v')
        self.keyboard.release('v')
        self.keyboard.release(Key.ctrl)
        
        print("✅ Text replaced!")


class AIFix:
    """Main application class"""
    
    def __init__(self):
        self.text_capture = TextCapture()
        self.ai_formatter = AIFormatter()
        self.text_replacer = TextReplacer()
        self.keyboard_handler = KeyboardHandler(
            on_fix_trigger=self.handle_fix,
            on_exit=self.exit_app
        )
        self.processing = False
        
    def handle_fix(self):
        """Handle the Alt+G trigger"""
        if self.processing:
            print("⏳ Already processing, please wait...")
            return
            
        self.processing = True
        print("\n🔧 AI Fix triggered!")
        
        try:
            # Capture highlighted text
            print("📋 Capturing highlighted text...")
            highlighted_text = self.text_capture.get_highlighted_text()
            
            if not highlighted_text:
                print("❌ No text selected. Please highlight some text first.")
                return
            
            print(f"📝 Captured {len(highlighted_text)} characters")
            
            # Send to AI for formatting
            formatted_text = self.ai_formatter.format_text(highlighted_text)
            
            if formatted_text:
                # Replace the selection
                self.text_replacer.replace_selection(formatted_text)
            else:
                print("❌ Failed to get AI response")
                
        except Exception as e:
            print(f"❌ Error during processing: {e}")
        finally:
            self.processing = False
            
    def exit_app(self):
        """Clean exit"""
        self.keyboard_handler.stop()
        sys.exit(0)
        
    def run(self):
        """Start the application"""
        print("🚀 AI Fix is running!")
        print("📌 Press Alt+G to fix highlighted text")
        print("📌 Press ESC to exit")
        print("\n💡 Make sure LM Studio is running on http://127.0.0.1:1234")
        
        # Start keyboard listener
        self.keyboard_handler.start()
        
        try:
            # Keep the program running
            self.keyboard_handler.wait()
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user")
            self.exit_app()


def main():
    """Main entry point"""
    app = AIFix()
    app.run()


if __name__ == "__main__":
    main()