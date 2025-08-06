#!/usr/bin/env python3
"""
Platform detection module for cross-platform compatibility
Detects operating system and Windows Subsystem for Linux (WSL)
"""

import platform
import os


def detect_operating_system():
    """
    Detect the operating system
    
    Returns:
        str: 'windows', 'linux', 'macos', or 'unknown'
    """
    try:
        system = platform.system().lower()
        
        if system == 'windows':
            return 'windows'
        elif system == 'linux':
            return 'linux'
        elif system == 'darwin':
            return 'macos'
        else:
            print(f"⚠️  Unknown platform detected: {system}")
            return 'unknown'
            
    except Exception as e:
        print(f"❌ Error detecting operating system: {e}")
        return 'unknown'


def is_wsl():
    """
    Detect if running under Windows Subsystem for Linux (WSL)
    
    Returns:
        bool: True if running under WSL, False otherwise
    """
    try:
        # Method 1: Check /proc/version for Microsoft/WSL signatures
        try:
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                if 'microsoft' in version_info or 'wsl' in version_info:
                    return True
        except (FileNotFoundError, IOError):
            pass
        
        # Method 2: Check for WSL_DISTRO_NAME environment variable
        if os.environ.get('WSL_DISTRO_NAME'):
            return True
            
        # Method 3: Check for WSLENV environment variable (WSL2)
        if os.environ.get('WSLENV'):
            return True
            
        return False
        
    except Exception as e:
        print(f"❌ Error detecting WSL: {e}")
        return False


def should_skip_device_selection():
    """
    Determine if audio device selection should be skipped
    
    Returns:
        bool: True if device selection should be skipped (Windows/WSL), False otherwise
    """
    try:
        os_type = detect_operating_system()
        wsl_detected = is_wsl()
        
        # Skip device selection for Windows or WSL
        if os_type == 'windows' or wsl_detected:
            print(f"🖥️  Platform: {os_type.title()}{' (WSL)' if wsl_detected else ''}")
            return True
        
        print(f"🖥️  Platform: {os_type.title()}")
        return False
        
    except Exception as e:
        print(f"❌ Error in platform detection: {e}")
        # Default to not skipping for safety
        return False


def get_platform_info():
    """
    Get detailed platform information for debugging
    
    Returns:
        dict: Platform information dictionary
    """
    try:
        os_type = detect_operating_system()
        wsl_detected = is_wsl()
        
        return {
            'os': os_type,
            'is_wsl': wsl_detected,
            'platform_system': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'skip_device_selection': should_skip_device_selection()
        }
        
    except Exception as e:
        print(f"❌ Error getting platform info: {e}")
        return {
            'os': 'unknown',
            'is_wsl': False,
            'error': str(e),
            'skip_device_selection': False
        }


def test_platform_detection():
    """
    Test function to validate platform detection on current system
    """
    print("🧪 Testing Platform Detection")
    print("=" * 50)
    
    # Test OS detection
    os_type = detect_operating_system()
    print(f"Detected OS: {os_type}")
    
    # Test WSL detection
    wsl_detected = is_wsl()
    print(f"WSL Detected: {wsl_detected}")
    
    # Test skip logic
    should_skip = should_skip_device_selection()
    print(f"Should Skip Device Selection: {should_skip}")
    
    # Show detailed info
    print("\n📊 Detailed Platform Information:")
    info = get_platform_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Platform detection test completed")


if __name__ == "__main__":
    test_platform_detection()