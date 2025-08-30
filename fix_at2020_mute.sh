#!/bin/bash

# Fix AT2020USB-X microphone auto-mute issue
# This script ensures the microphone is properly configured

echo "🎤 Fixing AT2020USB-X microphone settings..."

# Find the AT2020 card number dynamically
CARD_NUM=$(arecord -l | grep -i "AT2020USB" | sed -n 's/card \([0-9]\).*/\1/p' | head -1)

if [ -z "$CARD_NUM" ]; then
    echo "❌ AT2020USB-X not found!"
    exit 1
fi

echo "✅ Found AT2020USB-X on card $CARD_NUM"

# Set ALSA capture volume to optimal level (70% of max)
echo "📊 Setting capture volume..."
amixer -c $CARD_NUM cset numid=3 80 > /dev/null 2>&1

# Find PulseAudio source name
PA_SOURCE=$(pactl list sources | grep -B 1 "AT2020USB" | grep "Name:" | awk '{print $2}' | head -1)

if [ -n "$PA_SOURCE" ]; then
    echo "🔊 Configuring PulseAudio..."
    
    # Unmute the source
    pactl set-source-mute "$PA_SOURCE" 0
    
    # Set volume to 70%
    pactl set-source-volume "$PA_SOURCE" 70%
    
    echo "✅ PulseAudio configured for: $PA_SOURCE"
else
    echo "⚠️  Could not find PulseAudio source for AT2020"
fi

# Optional: Save ALSA settings (requires sudo)
if [ "$EUID" -eq 0 ]; then
    alsactl store $CARD_NUM
    echo "💾 Settings saved permanently"
else
    echo "ℹ️  Run with sudo to save settings permanently"
fi

echo "✅ AT2020USB-X microphone configured successfully!"
echo ""
echo "📝 To make permanent, run:"
echo "   sudo $0"
echo ""
echo "🔧 To add to startup, add this line to ~/.bashrc:"
echo "   $0"