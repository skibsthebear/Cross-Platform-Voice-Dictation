#!/usr/bin/env python3
"""
Audio device detection and selection module
"""

import sys
import subprocess
import json
import sounddevice as sd
from config import CHANNELS, DTYPE, PREFERRED_SAMPLE_RATES


def get_pulseaudio_sources():
    """Get list of audio sources from PulseAudio"""
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
        return None
    except json.JSONDecodeError:
        return None
    except FileNotFoundError:
        return None


def list_and_select_device():
    """List devices and let user select one"""
    print("\n📋 Available Input Devices:")
    print("-" * 60)
    
    # Get PulseAudio sources
    pulse_sources = get_pulseaudio_sources()
    
    if pulse_sources:
        devices = []
        for i, source in enumerate(pulse_sources, 1):
            devices.append(source)
            print(f"  [{i}] {source['product_name']}")
            if source['state'] == 'RUNNING':
                print("      ✅ Currently active")
            
        print(f"  [0] Use system default")
        print("-" * 60)
        
        while True:
            try:
                choice = input("Select device number (or press Enter for default): ").strip()
                
                if choice == "" or choice == "0":
                    print("\n✅ Using system default device")
                    return None
                
                choice = int(choice)
                if 1 <= choice <= len(devices):
                    selected = devices[choice - 1]
                    print(f"\n✅ Selected: {selected['product_name']}")
                    # Set this as the recording source in PulseAudio
                    try:
                        subprocess.run([
                            'pactl', 'set-default-source', 
                            selected['name']
                        ], check=True, capture_output=True)
                        print("   Set as default PulseAudio source")
                    except:
                        print("   ⚠️  Could not set as default source")
                    return selected
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except ValueError:
                print("❌ Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\n👋 Cancelled by user.")
                sys.exit(0)
    else:
        # Fallback to sounddevice listing
        print("Using sounddevice listing:\n")
        devices = sd.query_devices()
        input_devices = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append(i)
                default_marker = " [DEFAULT]" if i == sd.default.device[0] else ""
                print(f"  [{len(input_devices)}] {device['name']}{default_marker}")
        
        print(f"  [0] Use system default")
        print("-" * 60)
        
        while True:
            try:
                choice = input("Select device number (or press Enter for default): ").strip()
                
                if choice == "" or choice == "0":
                    print("\n✅ Using system default device")
                    return None
                
                choice = int(choice)
                if 1 <= choice <= len(input_devices):
                    device_id = input_devices[choice - 1]
                    device_info = sd.query_devices(device_id)
                    sd.default.device[0] = device_id
                    print(f"\n✅ Selected: {device_info['name']}")
                    return device_id
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except ValueError:
                print("❌ Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\n👋 Cancelled by user.")
                sys.exit(0)


def get_audio_device_info():
    """Get information about available audio devices and select the best configuration"""
    channels = CHANNELS
    
    try:
        # Query all devices
        devices = sd.query_devices()
        
        # Get default input device
        default_input = sd.default.device[0]
        
        print("🎤 Available audio devices:")
        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                marker = "→" if idx == default_input else " "
                print(f"  {marker} [{idx}] {device['name']} ({device['max_input_channels']} channels)")
        
        # Get info about default device
        device_info = sd.query_devices(default_input)
        
        # Determine best sample rate
        device_sample_rate = int(device_info['default_samplerate'])
        
        # Use device's default sample rate if it's in our preferred list
        if device_sample_rate in PREFERRED_SAMPLE_RATES:
            selected_rate = device_sample_rate
        else:
            # Otherwise use 44100 as fallback
            selected_rate = 44100
            
        # Validate the configuration
        try:
            sd.check_input_settings(
                device=default_input,
                channels=channels,
                samplerate=selected_rate,
                dtype=DTYPE
            )
            print(f"\n✅ Using default input device: {device_info['name']}")
            print(f"   Sample rate: {selected_rate} Hz")
            return default_input, selected_rate, channels
            
        except sd.PortAudioError:
            # Try fallback configurations
            for rate in PREFERRED_SAMPLE_RATES:
                if rate != selected_rate:
                    try:
                        sd.check_input_settings(
                            device=default_input,
                            channels=channels,
                            samplerate=rate,
                            dtype=DTYPE
                        )
                        print(f"\n✅ Using default input device: {device_info['name']}")
                        print(f"   Sample rate: {rate} Hz (fallback)")
                        return default_input, rate, channels
                    except:
                        continue
            
            # If still failing, try with 2 channels
            try:
                sd.check_input_settings(
                    device=default_input,
                    channels=2,
                    samplerate=device_sample_rate,
                    dtype=DTYPE
                )
                print(f"\n⚠️  Using stereo mode for: {device_info['name']}")
                print("   Note: Recording will use 2 channels")
                channels = 2
                return default_input, device_sample_rate, channels
            except:
                raise Exception("Could not find compatible audio configuration")
                
    except Exception as e:
        print(f"❌ Error detecting audio devices: {e}")
        print("   Falling back to system defaults")
        return None, 44100, channels


def list_all_devices():
    """List all available audio devices"""
    print("Available audio input devices:")
    print("-" * 60)
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            default = " [DEFAULT]" if i == sd.default.device[0] else ""
            print(f"[{i}] {device['name']} ({device['max_input_channels']} ch){default}")


def set_device(device_index):
    """Set a specific audio device by index"""
    try:
        device_info = sd.query_devices(device_index)
        if device_info['max_input_channels'] > 0:
            sd.default.device[0] = device_index
            print(f"✅ Using device [{device_index}]: {device_info['name']}")
            return True
        else:
            print(f"❌ Device {device_index} is not an input device")
            return False
    except Exception as e:
        print(f"❌ Invalid device index {device_index}: {e}")
        return False