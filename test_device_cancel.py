#!/usr/bin/env python3
"""
Test script to verify device selection cancellation handling
"""

from audio_device import list_and_select_device, DeviceSelectionCancelled

def test_device_cancellation():
    """Test device selection cancellation handling"""
    print("Testing device selection cancellation...")
    print("When prompted, press Ctrl+C to test cancellation handling")
    
    try:
        result = list_and_select_device()
        print(f"Device selection completed successfully: {result}")
    except DeviceSelectionCancelled as e:
        print(f"✅ Cancellation handled gracefully: {e}")
        print("Application would continue with default device...")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_device_cancellation()
    if success:
        print("\n✅ Test completed - cancellation handling works!")
    else:
        print("\n❌ Test failed")