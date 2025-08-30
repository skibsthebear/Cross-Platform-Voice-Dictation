#!/usr/bin/env python3
"""
Test script to verify the AT2020 unmute fixes
"""

import time
import subprocess
from audio_recorder import AudioRecorder

def check_mute_status():
    """Check if AT2020 is muted"""
    result = subprocess.run(['pactl', 'list', 'sources'], 
                          capture_output=True, text=True, check=False)
    
    in_at2020 = False
    for line in result.stdout.split('\n'):
        if 'AT2020' in line:
            in_at2020 = True
        elif in_at2020 and 'Mute:' in line:
            mute_status = line.strip()
            return mute_status
    return "Not found"

print("🔍 Testing AT2020 unmute fixes...")
print("-" * 50)

# Check initial status
print(f"Initial mute status: {check_mute_status()}")

# Start recording (this should trigger the unmute fixes)
print("\n🎤 Starting recording...")
recorder = AudioRecorder()
recorder.start_recording()

# Wait a bit for the unmute to take effect
time.sleep(0.5)

# Check status after starting
print(f"After starting: {check_mute_status()}")

print("\n📊 Recording for 2 seconds...")
time.sleep(2)

# Stop recording
audio_file = recorder.stop_recording()
print(f"✅ Recording saved to: {audio_file}")

# Final status check
print(f"Final status: {check_mute_status()}")

print("\n" + "=" * 50)
print("✅ Test complete!")
print("\nIf the microphone shows 'Mute: no' after starting,")
print("the fix is working correctly!")