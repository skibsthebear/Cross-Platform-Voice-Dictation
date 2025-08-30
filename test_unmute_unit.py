#!/usr/bin/env python3
"""
Unit test for the USB microphone unmute functionality
"""

import unittest
import subprocess
import json
from unittest.mock import patch, MagicMock, call
from keyboard_handler import KeyboardHandler


class TestUnmuteUSBMicrophone(unittest.TestCase):
    """Test cases for USB microphone unmute feature"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.handler = KeyboardHandler()
        
    @patch('subprocess.run')
    def test_unmute_at2020_found(self, mock_run):
        """Test unmuting when AT2020 is found"""
        # Mock pactl check
        mock_run.side_effect = [
            # which pactl
            MagicMock(returncode=0),
            # pactl -f json list sources
            MagicMock(
                returncode=0, 
                stdout=json.dumps([{
                    'name': 'alsa_input.usb-AT_AT2020USB-X_202011110001-00.mono-fallback',
                    'description': 'AT2020USB-X Mono',
                    'mute': True,
                    'properties': {
                        'device.bus': 'usb',
                        'device.product.name': 'AT2020USB-X',
                        'device.vendor.name': 'Audio-Technica Corp.'
                    }
                }])
            ),
            # pactl set-source-mute
            MagicMock(returncode=0),
            # pactl -f json get-source-mute
            MagicMock(returncode=0, stdout='false'),
            # pactl set-source-volume
            MagicMock(returncode=0),
            # pactl -f json get-source-volume
            MagicMock(returncode=0)
        ]
        
        self.handler._unmute_usb_microphone()
        
        # Verify AT2020 was unmuted
        calls = mock_run.call_args_list
        unmute_call = [c for c in calls if 'set-source-mute' in c[0][0]]
        self.assertTrue(len(unmute_call) > 0)
        self.assertIn('AT2020', unmute_call[0][0][0][2])
        
    @patch('subprocess.run')
    def test_unmute_no_usb_microphone(self, mock_run):
        """Test when no USB microphone is found"""
        mock_run.side_effect = [
            # which pactl
            MagicMock(returncode=0),
            # pactl -f json list sources
            MagicMock(
                returncode=0,
                stdout=json.dumps([{
                    'name': 'alsa_input.pci-0000_00_1f.3.analog-stereo',
                    'description': 'Built-in Audio',
                    'mute': False,
                    'properties': {
                        'device.bus': 'pci'
                    }
                }])
            )
        ]
        
        with patch('builtins.print') as mock_print:
            self.handler._unmute_usb_microphone()
            mock_print.assert_any_call("No USB microphone found to unmute")
            
    @patch('subprocess.run')
    def test_unmute_pactl_not_found(self, mock_run):
        """Test when pactl is not available"""
        mock_run.return_value = MagicMock(returncode=1)
        
        with patch('builtins.print') as mock_print:
            self.handler._unmute_usb_microphone()
            mock_print.assert_called_with("pactl not found - skipping microphone unmute")
            
    @patch('subprocess.run')
    def test_unmute_fallback_on_json_error(self, mock_run):
        """Test fallback when JSON parsing fails"""
        mock_run.side_effect = [
            # which pactl
            MagicMock(returncode=0),
            # pactl -f json list sources (invalid JSON)
            MagicMock(returncode=0, stdout='not json'),
            # Fallback: pactl list sources short
            MagicMock(
                returncode=0,
                stdout='60\talsa_input.usb-AT_AT2020USB-X_202011110001-00.mono-fallback\tmodule-alsa-card.c\ts24le 1ch 48000Hz\tSUSPENDED'
            ),
            # Fallback unmute
            MagicMock(returncode=0),
            # Fallback volume
            MagicMock(returncode=0)
        ]
        
        with patch('builtins.print') as mock_print:
            self.handler._unmute_usb_microphone()
            # Should use fallback
            mock_print.assert_any_call("Fallback: Found USB microphone alsa_input.usb-AT_AT2020USB-X_202011110001-00.mono-fallback")
            
    @patch('subprocess.run')
    def test_unmute_retry_on_failure(self, mock_run):
        """Test retry logic when unmute fails first time"""
        mock_run.side_effect = [
            # which pactl
            MagicMock(returncode=0),
            # pactl -f json list sources
            MagicMock(
                returncode=0,
                stdout=json.dumps([{
                    'name': 'test_usb_mic',
                    'description': 'Test USB Mic',
                    'mute': True,
                    'properties': {
                        'device.bus': 'usb',
                        'device.product.name': 'Test Mic'
                    }
                }])
            ),
            # First unmute attempt
            MagicMock(returncode=0),
            # First verification - still muted
            MagicMock(returncode=0, stdout='true'),
            # Second unmute attempt
            MagicMock(returncode=0),
            # Second verification - now unmuted
            MagicMock(returncode=0, stdout='false'),
            # Set volume
            MagicMock(returncode=0),
            # Verify volume
            MagicMock(returncode=0)
        ]
        
        with patch('builtins.print') as mock_print:
            self.handler._unmute_usb_microphone()
            # Should show retry message
            mock_print.assert_any_call("⚠️ Microphone still muted after attempt 1, retrying...")
            
    @patch('subprocess.run')
    def test_prioritize_at2020_over_other_usb(self, mock_run):
        """Test that AT2020 is prioritized over other USB mics"""
        mock_run.side_effect = [
            # which pactl
            MagicMock(returncode=0),
            # pactl -f json list sources
            MagicMock(
                returncode=0,
                stdout=json.dumps([
                    {
                        'name': 'other_usb_mic',
                        'description': 'Other USB Mic',
                        'mute': True,
                        'properties': {
                            'device.bus': 'usb',
                            'device.product.name': 'Other Mic'
                        }
                    },
                    {
                        'name': 'at2020_mic',
                        'description': 'AT2020USB-X',
                        'mute': True,
                        'properties': {
                            'device.bus': 'usb',
                            'device.product.name': 'AT2020USB-X',
                            'device.vendor.name': 'Audio-Technica Corp.'
                        }
                    }
                ])
            ),
            # Unmute AT2020
            MagicMock(returncode=0),
            # Verify unmute
            MagicMock(returncode=0, stdout='false'),
            # Set volume
            MagicMock(returncode=0),
            # Verify volume
            MagicMock(returncode=0)
        ]
        
        self.handler._unmute_usb_microphone()
        
        # Verify AT2020 was selected
        calls = mock_run.call_args_list
        unmute_call = [c for c in calls if 'set-source-mute' in c[0][0]]
        self.assertIn('at2020_mic', unmute_call[0][0][0][2])


if __name__ == '__main__':
    unittest.main(verbosity=2)