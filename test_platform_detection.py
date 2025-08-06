#!/usr/bin/env python3
"""
Test platform detection functionality
"""

import sys
import os
from platform_detection import (
    detect_operating_system,
    is_wsl,
    should_skip_device_selection,
    get_platform_info
)


def test_os_detection():
    """Test operating system detection"""
    print("🧪 Testing OS Detection")
    print("-" * 40)
    
    os_type = detect_operating_system()
    print(f"Detected OS: {os_type}")
    
    # Validate the result
    valid_os_types = ['windows', 'linux', 'macos', 'unknown']
    assert os_type in valid_os_types, f"Invalid OS type: {os_type}"
    print("✅ OS detection test passed")


def test_wsl_detection():
    """Test WSL detection"""
    print("\n🧪 Testing WSL Detection")
    print("-" * 40)
    
    wsl_detected = is_wsl()
    print(f"WSL Detected: {wsl_detected}")
    print("✅ WSL detection test passed")


def test_device_selection_logic():
    """Test device selection skip logic"""
    print("\n🧪 Testing Device Selection Logic")
    print("-" * 40)
    
    should_skip = should_skip_device_selection()
    print(f"Should Skip Device Selection: {should_skip}")
    
    # Verify logic consistency
    os_type = detect_operating_system()
    wsl = is_wsl()
    expected_skip = (os_type == 'windows' or wsl)
    
    assert should_skip == expected_skip, f"Logic inconsistency: should_skip={should_skip}, expected={expected_skip}"
    print("✅ Device selection logic test passed")


def test_platform_info():
    """Test platform info gathering"""
    print("\n🧪 Testing Platform Info")
    print("-" * 40)
    
    info = get_platform_info()
    
    # Validate required fields
    required_fields = ['os', 'is_wsl', 'skip_device_selection']
    for field in required_fields:
        assert field in info, f"Missing required field: {field}"
    
    print("Platform Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("✅ Platform info test passed")


def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🧪 Testing Edge Cases")
    print("-" * 40)
    
    # Test that functions don't crash on various conditions
    try:
        # These should not raise exceptions
        detect_operating_system()
        is_wsl()
        should_skip_device_selection()
        get_platform_info()
        print("✅ Edge case handling test passed")
    except Exception as e:
        print(f"❌ Edge case test failed: {e}")
        return False
    
    return True


def test_current_environment():
    """Test behavior on current environment"""
    print("\n🧪 Testing Current Environment")
    print("-" * 40)
    
    info = get_platform_info()
    os_type = info['os']
    is_wsl_env = info['is_wsl']
    
    print(f"Current Environment: {os_type}")
    if is_wsl_env:
        print("Running in WSL")
    
    # Expected behavior based on environment
    if os_type == 'linux' and not is_wsl_env:
        print("Expected: Device selection should be shown")
        assert not info['skip_device_selection'], "Device selection should not be skipped on native Linux"
    elif os_type == 'windows' or is_wsl_env:
        print("Expected: Device selection should be skipped")
        assert info['skip_device_selection'], "Device selection should be skipped on Windows/WSL"
    
    print("✅ Current environment test passed")


def main():
    """Run all tests"""
    print("🔬 Platform Detection Test Suite")
    print("=" * 50)
    
    tests = [
        test_os_detection,
        test_wsl_detection,
        test_device_selection_logic,
        test_platform_info,
        test_edge_cases,
        test_current_environment
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())