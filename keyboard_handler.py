#!/usr/bin/env python3
"""
Keyboard handler module for managing hotkeys
"""

import subprocess
import json
from pynput import keyboard
from pynput.keyboard import Key


class KeyboardHandler:
    def __init__(self, on_record_toggle=None, on_exit=None):
        self.on_record_toggle = on_record_toggle
        self.on_exit = on_exit
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
        # Check for Right Control key
        if key == Key.ctrl_r:
            # Unmute AT2020 microphone immediately when record key is pressed
            # This fixes the auto-mute issue with USB microphones
            self._unmute_usb_microphone()
            
            if self.on_record_toggle:
                self.on_record_toggle()
    
    def _unmute_usb_microphone(self):
        """Unmute USB microphone (like AT2020) when recording starts"""
        try:
            # Check if pactl is available
            which_result = subprocess.run(['which', 'pactl'], 
                                        capture_output=True, check=False)
            if which_result.returncode != 0:
                print("pactl not found - skipping microphone unmute")
                return
            
            # Use JSON output for reliable parsing
            result = subprocess.run(['pactl', '-f', 'json', 'list', 'sources'], 
                                  capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                sources = json.loads(result.stdout)
                
                # Find USB microphones, prioritizing AT2020
                usb_sources = []
                at2020_source = None
                
                for source in sources:
                    # Check if it's a USB device (not a monitor source)
                    properties = source.get('properties', {})
                    if properties.get('device.bus') == 'usb' and 'monitor' not in source.get('name', ''):
                        usb_sources.append(source)
                        
                        # Check if it's an AT2020 device
                        product_name = properties.get('device.product.name', '')
                        vendor_name = properties.get('device.vendor.name', '')
                        if 'AT2020' in product_name or 'Audio-Technica' in vendor_name:
                            at2020_source = source
                
                # Select the source to unmute (AT2020 first, then any USB mic)
                source_to_unmute = at2020_source if at2020_source else (usb_sources[0] if usb_sources else None)
                
                if source_to_unmute:
                    source_name = source_to_unmute['name']
                    current_mute = source_to_unmute.get('mute', False)
                    
                    print(f"Found USB microphone: {source_to_unmute.get('description', source_name)}")
                    print(f"Current mute status: {'muted' if current_mute else 'unmuted'}")
                    
                    # Try to unmute with verification (max 2 attempts)
                    max_attempts = 2
                    for attempt in range(max_attempts):
                        # Unmute and set good volume
                        unmute_result = subprocess.run(['pactl', 'set-source-mute', source_name, '0'], 
                                                     capture_output=True, text=True, check=False)
                        
                        if unmute_result.returncode != 0:
                            print(f"Warning: Failed to unmute {source_name}: {unmute_result.stderr}")
                            continue
                        
                        # Verify unmute succeeded
                        verify_result = subprocess.run(['pactl', '-f', 'json', 'get-source-mute', source_name],
                                                      capture_output=True, text=True, check=False)
                        
                        if verify_result.returncode == 0:
                            try:
                                mute_status = json.loads(verify_result.stdout)
                                if not mute_status:  # False means unmuted
                                    print(f"✅ Successfully unmuted {source_name} (verified)")
                                    
                                    # Set volume
                                    volume_result = subprocess.run(['pactl', 'set-source-volume', source_name, '70%'], 
                                                                  capture_output=True, text=True, check=False)
                                    
                                    if volume_result.returncode != 0:
                                        print(f"Warning: Failed to set volume for {source_name}: {volume_result.stderr}")
                                    else:
                                        # Verify volume was set
                                        verify_vol = subprocess.run(['pactl', '-f', 'json', 'get-source-volume', source_name],
                                                                   capture_output=True, text=True, check=False)
                                        if verify_vol.returncode == 0:
                                            print(f"✅ Successfully set volume to 70% for {source_name} (verified)")
                                        else:
                                            print(f"Successfully set volume to 70% for {source_name}")
                                    break
                                else:
                                    if attempt < max_attempts - 1:
                                        print(f"⚠️ Microphone still muted after attempt {attempt + 1}, retrying...")
                                    else:
                                        print(f"❌ Failed to unmute {source_name} after {max_attempts} attempts")
                            except json.JSONDecodeError:
                                # Fallback if JSON parsing fails
                                print(f"Successfully sent unmute command to {source_name}")
                                break
                        else:
                            # Can't verify, assume success
                            print(f"Successfully sent unmute command to {source_name}")
                            subprocess.run(['pactl', 'set-source-volume', source_name, '70%'], 
                                         capture_output=True, check=False)
                            break
                else:
                    print("No USB microphone found to unmute")
            else:
                print(f"Failed to list sources: {result.stderr}")
                
        except json.JSONDecodeError as e:
            print(f"Error parsing pactl JSON output: {e}")
            # Fallback to old method if JSON is not supported
            self._unmute_usb_microphone_fallback()
        except Exception as e:
            print(f"Error in unmute USB microphone: {e}")
    
    def _unmute_usb_microphone_fallback(self):
        """Fallback method using old parsing for systems without JSON support"""
        try:
            result = subprocess.run(['pactl', 'list', 'sources', 'short'], 
                                  capture_output=True, text=True, check=False)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'AT2020' in line or 'USB' in line:
                        # More robust parsing with spaces or tabs
                        parts = line.split()
                        if len(parts) >= 2:
                            source_name = parts[1]
                            print(f"Fallback: Found USB microphone {source_name}")
                            
                            # Unmute and set good volume
                            subprocess.run(['pactl', 'set-source-mute', source_name, '0'], 
                                         capture_output=True, check=False)
                            subprocess.run(['pactl', 'set-source-volume', source_name, '70%'], 
                                         capture_output=True, check=False)
                            print(f"Fallback: Attempted to unmute {source_name}")
                            break
        except Exception as e:
            print(f"Fallback unmute failed: {e}")
    
    def _on_release(self, key):
        """Handle key release events"""
        # No special handling needed for key release anymore
        pass