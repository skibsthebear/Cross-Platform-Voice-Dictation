#!/bin/bash

# Script to fix CUDA unknown error without rebooting
echo "🔧 CUDA Unknown Error Fix Script"
echo "================================="
echo ""
echo "This script fixes the 'CUDA unknown error' by reloading NVIDIA kernel modules"
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script needs sudo privileges to reload kernel modules"
    echo "   Please run: sudo ./fix_cuda_error.sh"
    exit 1
fi

echo "🔄 Reloading nvidia_uvm kernel module..."
rmmod nvidia_uvm 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Removed nvidia_uvm module"
else
    echo "   ⚠️  nvidia_uvm module was not loaded"
fi

modprobe nvidia_uvm
if [ $? -eq 0 ]; then
    echo "   ✅ Loaded nvidia_uvm module"
else
    echo "   ❌ Failed to load nvidia_uvm module"
    echo "   You may need to reboot your system"
    exit 1
fi

echo ""
echo "🔍 Checking nvidia-modprobe installation..."
if command -v nvidia-modprobe &> /dev/null; then
    echo "   ✅ nvidia-modprobe is installed"
else
    echo "   ⚠️  nvidia-modprobe not found. Installing..."
    apt update && apt install -y nvidia-modprobe
fi

echo ""
echo "🔍 Testing CUDA availability in Python..."
# Drop sudo privileges for Python test
sudo -u $SUDO_USER bash << 'EOF'
source whisper_venv/bin/activate 2>/dev/null
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print('✅ CUDA is working!')
else:
    print('❌ CUDA still not available')
    print('   Try rebooting your system')
" 2>/dev/null || echo "⚠️  Could not test PyTorch (virtual env may not be active)"
EOF

echo ""
echo "✅ Done! Try running ./startVoice_gpu.sh again"
echo ""
echo "If this didn't work, try:"
echo "1. Reboot your system (most reliable fix)"
echo "2. Check 'nvidia-smi' output"
echo "3. Update NVIDIA drivers"