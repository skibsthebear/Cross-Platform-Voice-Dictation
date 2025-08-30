#!/usr/bin/env python3
"""
Shared AI formatting functionality for both AI Fix and AI Pass-through
"""

import json
import requests
from typing import Optional


class AIFormatter:
    """Handles communication with LM Studio API"""
    
    def __init__(self, api_url="http://127.0.0.1:1234/v1/chat/completions", model="google/gemma-3n-e4b", temperature=0.3, max_tokens=-1):
        self.api_url = api_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.headers = {"Content-Type": "application/json"}
        
    def format_text(self, text: str, system_prompt: str = None) -> Optional[str]:
        """Send text to AI for formatting and return the result"""
        # Create a combined user message with explicit instructions
        user_message = (
            "You will always only reply with the formatted text. Your sole job is to format the text. "
            "Read the entire text carefully and understand the context before formatting. "
            "Fix grammar, spelling, punctuation, and style issues without altering meaning "
            "Convert spoken-out formats to their proper syntax (e.g., 'dot com' to '.com', 'readme dot md' to 'readme.md', "
            "'w w w dot' to 'www.', 'at symbol' to '@', 'hashtag' to '#'). "
            "Fix spelling issues of names and coding terms like Vercel, Netlify, GitHub, func, def and others."
            "For lists, ensure each item is on a new line. "
            f"This is the text the user wants you to format: \"{text}\""
        )
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
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