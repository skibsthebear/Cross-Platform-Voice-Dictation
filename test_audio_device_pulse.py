#!/usr/bin/env python3
"""
Test script for audio device detection using PulseAudio
"""

import subprocess
import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import time
import os
import sys
import json

def get_pulseaudio_sources():
    """Get audio sources from PulseAudio (Linux only)."""
    if sys.platform == "win32":
        print("PulseAudio is not available on Windows.")
        return []
    
    try:
        # Get list of sources (input devices) from pactl
        result = subprocess.run(
            ['pactl', '-f', 'json', 'list', 'sources'],
            capture_output=True,
            text=True,
            check=True
        )
        
        sources = json.loads(result.stdout)
        
        # Filter for actual hardware devices (not monitors)
        hardware_sources = []
        for source in sources:
            # Skip monitor devices
            if 'monitor' not in source.get('name', '').lower():
                device_info = {
                    'name': source.get('name', 'Unknown'),
                    'description': source.get('description', 'Unknown Device'),
                    'index': source.get('index', -1),
                    'state': source.get('state', 'UNKNOWN'),
                    'channels': source.get('channel_map', []),
                    'properties': source.get('properties', {})
                }
                
                # Get the actual device name from properties
                props = device_info['properties']
                if 'device.product.name' in props:
                    device_info['product_name'] = props['device.product.name']
                elif 'device.description' in props:
                    device_info['product_name'] = props['device.description']
                else:
                    device_info['product_name'] = device_info['description']
                
                hardware_sources.append(device_info)
        
        return hardware_sources
        
    except subprocess.CalledProcessError:
        print("⚠️  Could not get PulseAudio sources. Falling back to sounddevice listing.")
        return None
    except json.JSONDecodeError:
        print("⚠️  Could not parse PulseAudio output. Falling back to sounddevice listing.")
        return None
    except FileNotFoundError:
        print("⚠️  pactl not found. Make sure PulseAudio is installed.")
        return None

def list_devices_with_pulse():
    """List devices with PulseAudio names"""
    print("\n📋 Available Input Devices:")
    print("-" * 80)
    
    # Get PulseAudio sources
    pulse_sources = get_pulseaudio_sources()
    
    # Add Windows compatibility check
    if not pulse_sources and sys.platform == "win32":
        print("Using sounddevice for Windows...")
        # Use sounddevice enumeration instead
    
    if pulse_sources:
        print("Using PulseAudio device information:\n")
        
        devices = []
        for i, source in enumerate(pulse_sources, 1):
            devices.append(source)
            print(f"  [{i}] {source['product_name']}")
            print(f"      Description: {source['description']}")
            print(f"      State: {source['state']} | Channels: {len(source['channels'])}")
            if source['state'] == 'RUNNING':
                print("      ✅ Currently active")
            print()
        
        return devices, 'pulse'
    else:
        # Fallback to sounddevice
        print("Using sounddevice listing:\n")
        devices = sd.query_devices()
        input_devices = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append((i, device))
                default_marker = " [DEFAULT]" if i == sd.default.device[0] else ""
                print(f"  [{len(input_devices)}] {device['name']}")
                print(f"      Channels: {device['max_input_channels']} | Sample Rate: {int(device['default_samplerate'])} Hz{default_marker}")
                print()
        
        return input_devices, 'sounddevice'

def select_device(devices, mode):
    """Allow user to select a device"""
    while True:
        try:
            print("-" * 80)
            choice = input("Select device number (or press Enter for default): ").strip()
            
            if choice == "":
                if mode == 'pulse':
                    # For PulseAudio, we'll use the default sounddevice
                    print("\n✅ Using system default device")
                    return None, None
                else:
                    # Use default device
                    device_id = sd.default.device[0]
                    device_info = sd.query_devices(device_id)
                    print(f"\n✅ Using default device: {device_info['name']}")
                    return device_id, device_info
            
            choice = int(choice)
            if mode == 'pulse':
                if 1 <= choice <= len(devices):
                    selected = devices[choice - 1]
                    print(f"\n✅ Selected: {selected['product_name']}")
                    # Set this as the recording source in PulseAudio
                    try:
                        subprocess.run([
                            'pactl', 'set-default-source', 
                            selected['name']
                        ], check=True)
                        print("   Set as default PulseAudio source")
                    except:
                        print("   ⚠️  Could not set as default source")
                    return None, selected
                else:
                    print("❌ Invalid choice. Please try again.")
            else:
                if 1 <= choice <= len(devices):
                    device_id, device_info = devices[choice - 1]
                    print(f"\n✅ Selected: {device_info['name']}")
                    return device_id, device_info
                else:
                    print("❌ Invalid choice. Please try again.")
                    
        except ValueError:
            print("❌ Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\n👋 Test cancelled by user.")
            sys.exit(0)

def test_device(device_id=None, device_info=None):
    """Test the selected device"""
    if device_info and isinstance(device_info, dict) and 'product_name' in device_info:
        # PulseAudio device
        device_name = device_info['product_name']
        print("\n" + "=" * 80)
        print(f"Testing Device: {device_name}")
        print("=" * 80)
        print("\n📊 Using PulseAudio default device")
        print(f"   Device: {device_info['description']}")
        print(f"   State: {device_info['state']}")
        print(f"   Channels: {len(device_info.get('channels', []))}")
    else:
        # Sounddevice device
        if device_id is None:
            device_id = sd.default.device[0]
            device_info = sd.query_devices(device_id)
        
        device_name = device_info['name']
        print("\n" + "=" * 80)
        print(f"Testing Device: {device_name}")
        print("=" * 80)
        print(f"\n📊 Device Information:")
        print(f"   Device ID: {device_id}")
        print(f"   Max input channels: {device_info['max_input_channels']}")
        print(f"   Default sample rate: {int(device_info['default_samplerate'])} Hz")
    
    # Determine sample rate
    sample_rate = 44100  # Default
    
    # Test recording
    duration = 3  # seconds
    countdown = 3  # countdown seconds
    
    print(f"\n🎤 Testing {duration}-second recording...")
    print("   Preparing to record...")
    
    # Countdown
    for i in range(countdown, 0, -1):
        print(f"   Starting in {i}...", end='\r')
        time.sleep(1)
    
    print("\n   🔴 RECORDING! Speak now!")
    
    try:
        # Record audio (let sounddevice use the system default if device_id is None)
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='int16',
            device=device_id
        )
        
        # Show progress
        for i in range(duration):
            time.sleep(1)
            print(f"   Recording... {i+1}/{duration}s", end='\r')
        
        sd.wait()  # Wait for recording to complete
        print("\n   ⏹️  Recording stopped")
        
        # Analyze recording
        print("\n📈 Recording Analysis:")
        print(f"   Shape: {recording.shape}")
        print(f"   Duration: {len(recording) / sample_rate:.2f} seconds")
        print(f"   Sample rate: {sample_rate} Hz")
        
        # Calculate audio statistics
        peak_level = np.max(np.abs(recording))
        rms_level = np.sqrt(np.mean(recording.astype(float)**2))
        
        print(f"   Peak level: {peak_level} ({peak_level/32768*100:.1f}%)")
        print(f"   RMS level: {rms_level:.1f}")
        
        if peak_level < 100:
            print("   ⚠️  Very low audio level detected. Check microphone volume.")
        elif peak_level > 30000:
            print("   ⚠️  Audio might be clipping. Consider reducing microphone gain.")
        else:
            print("   ✅ Audio levels look good!")
        
        # Save the recording
        output_file = os.path.join(os.path.dirname(__file__), 'test_audio.wav')
        
        # Ensure the audio is in the right format
        if recording.ndim > 1 and recording.shape[1] == 1:
            recording = recording.flatten()
        
        # Save as WAV file
        scipy.io.wavfile.write(output_file, sample_rate, recording)
        
        file_size = os.path.getsize(output_file)
        print(f"\n💾 Audio saved to: {output_file}")
        print(f"   File size: {file_size:,} bytes")
        print(f"   Bit rate: {file_size * 8 / duration / 1000:.1f} kbps")
        
        # Verify the saved file
        try:
            read_rate, read_data = scipy.io.wavfile.read(output_file)
            print(f"\n🔍 File Verification:")
            print(f"   File readable: ✅")
            print(f"   Sample rate preserved: {'✅' if read_rate == sample_rate else '❌'}")
            print(f"   Data integrity: {'✅' if len(read_data) == len(recording) else '❌'}")
        except Exception as e:
            print(f"\n❌ File verification failed: {e}")
            
    except Exception as e:
        print(f"\n❌ Recording failed: {e}")
        return False
    
    return True

def main():
    print("=" * 80)
    print("🎙️  Audio Device Test Utility (PulseAudio Enhanced)")
    print("=" * 80)
    
    try:
        # List available devices
        devices, mode = list_devices_with_pulse()
        
        if not devices:
            print("❌ No input devices found!")
            return
        
        # Let user select device
        device_id, device_info = select_device(devices, mode)
        
        # Test the selected device
        success = test_device(device_id, device_info)
        
        if success:
            print("\n✅ Device test completed successfully!")
            print("   You can play test_audio.wav to hear the recording.")
            
            # Ask if user wants to test another device
            print("\n" + "-" * 80)
            again = input("Test another device? (y/N): ").strip().lower()
            if again == 'y':
                print()
                main()  # Recursive call to test another device
        else:
            print("\n❌ Device test failed!")
            
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()