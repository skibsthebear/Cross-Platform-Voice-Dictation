#!/usr/bin/env python3
"""
Test that pressing Right Ctrl unmutes the AT2020
"""

import subprocess
import time
from keyboard_handler import KeyboardHandler
from pynput.keyboard import Controller, Key

def check_mute_status():
    """Check if AT2020 is muted"""
    result = subprocess.run(['pactl', 'list', 'sources'], 
                          capture_output=True, text=True, check=False)
    
    in_at2020 = False
    for line in result.stdout.split('\n'):
        if 'AT2020' in line:
            in_at2020 = True
        elif in_at2020 and 'Mute:' in line:
            return line.strip()
    return "AT2020 not found"

print("🔍 Testing Right Ctrl unmute feature...")
print("-" * 50)

# First, manually mute the microphone to test
print("🔇 Manually muting AT2020 for test...")
subprocess.run(['pactl', 'set-source-mute', 
                'alsa_input.usb-AT_AT2020USB-X_202011110001-00.mono-fallback', '1'],
               capture_output=True, check=False)

time.sleep(0.5)
print(f"Status after muting: {check_mute_status()}")

# Set up keyboard handler
toggle_called = False
def on_toggle():
    global toggle_called
    toggle_called = True
    print("   Record toggle triggered!")

handler = KeyboardHandler(on_record_toggle=on_toggle)
handler.start()

# Simulate pressing Right Ctrl
print("\n🎮 Simulating Right Ctrl press...")
keyboard = Controller()
keyboard.press(Key.ctrl_r)
time.sleep(0.1)
keyboard.release(Key.ctrl_r)

# Wait for handler to process
time.sleep(0.5)

print(f"Status after Right Ctrl: {check_mute_status()}")
print(f"Toggle callback called: {toggle_called}")

handler.stop()

print("\n" + "=" * 50)
if "Mute: no" in check_mute_status():
    print("✅ Success! Right Ctrl unmutes the microphone!")
else:
    print("❌ Microphone is still muted")