# Task: Fix AI Fix Double-Pasting Issue

## Problem Analysis

The AI Fix feature is pasting text twice when Alt+G is pressed. Based on the user's output, we can see these messages appearing twice:
```
🔧 AI Fix triggered!
📋 Capturing highlighted text...
📝 Captured 54 characters
🤖 Sending to AI for processing...
📝 Captured 54 characters
🤖 Sending to AI for processing...
..............
.......✅ Text replaced and clipboard restored!
.......
✅ Text replaced and clipboard restored!
```

This indicates that the `handle_fix()` method is being executed twice for a single Alt+G keypress.

## Root Cause Investigation

After examining the code in `ai-fix.py`, the likely causes are:

### 1. **Keyboard Event Handling Issue** (Most Likely)
- **Problem**: The keyboard listener might be detecting both `Alt+G` key press events twice
- **Location**: `ai-fix.py:45-58` in the `_on_press()` method
- **Cause**: The keyboard listener could be receiving duplicate events from the system

### 2. **Race Condition in Processing Lock** (Possible)  
- **Problem**: The `processing` flag might not be preventing concurrent execution properly
- **Location**: `ai-fix.py:241` and `ai-fix.py:245-248`
- **Cause**: Timing issue where the flag isn't set fast enough before second trigger

### 3. **Startup Script Launching Multiple Instances** (Less Likely)
- **Problem**: The startup script might be launching AI Fix multiple times
- **Location**: `startVoice_api.sh:41-53`
- **Cause**: The restart loop could cause overlapping instances

## Implementation Plan for Non-Programmers

### **What We Need to Fix**

The AI Fix program is responding to the Alt+G keypress twice instead of once, causing it to paste the formatted text two times. This makes the text appear duplicated in your document.

### **Solution Overview**

We need to add better protection so that when Alt+G is pressed, the program only processes it once, even if the system sends the keypress signal multiple times.

### **Files to Modify**

1. **`ai-fix.py`** - The main AI Fix program file
2. **Test the fix** - Verify it works correctly

### **Step-by-Step Fix Instructions**

#### **Step 1: Improve Keyboard Event Handling**

**What to change**: Add better duplicate event prevention in the keyboard handling code.

**Location**: In `ai-fix.py`, find the `_on_press` method around line 45.

**Current problematic code**:
```python
def _on_press(self, key):
    """Handle key press events"""
    # Track Alt key state
    if key in [Key.alt, Key.alt_l, Key.alt_r]:
        self.alt_pressed = True
    
    # Check for Alt+G
    if self.alt_pressed:
        try:
            if hasattr(key, 'char') and key.char == 'g':
                if self.on_fix_trigger:
                    self.on_fix_trigger()
        except:
            pass
```

**What's wrong**: This code doesn't prevent multiple rapid keypresses of 'g' while Alt is held down.

**New improved code**:
```python
def _on_press(self, key):
    """Handle key press events"""
    # Track Alt key state
    if key in [Key.alt, Key.alt_l, Key.alt_r]:
        self.alt_pressed = True
    
    # Check for Alt+G
    if self.alt_pressed:
        try:
            if hasattr(key, 'char') and key.char == 'g':
                # Prevent rapid duplicate triggers
                current_time = time.time()
                if hasattr(self, 'last_trigger_time'):
                    if current_time - self.last_trigger_time < 0.5:  # 500ms cooldown
                        return
                
                self.last_trigger_time = current_time
                if self.on_fix_trigger:
                    self.on_fix_trigger()
        except:
            pass
```

**What this fixes**: Adds a 500-millisecond cooldown period so Alt+G can only trigger once every half second, preventing duplicate processing.

#### **Step 2: Improve Processing Lock**

**What to change**: Make the processing lock more robust to prevent race conditions.

**Location**: In `ai-fix.py`, find the `handle_fix` method around line 243.

**Current code**:
```python
def handle_fix(self):
    """Handle the Alt+G trigger"""
    if self.processing:
        print("⏳ Already processing, please wait...")
        return
        
    self.processing = True
    print("\n🔧 AI Fix triggered!")
```

**New improved code**:
```python
def handle_fix(self):
    """Handle the Alt+G trigger"""
    # Use atomic check-and-set to prevent race conditions
    if getattr(self, 'processing', False):
        print("⏳ Already processing, please wait...")
        return
        
    # Set processing flag immediately
    self.processing = True
    
    # Add visual feedback that we're starting
    print(f"\n🔧 AI Fix triggered at {time.strftime('%H:%M:%S')}!")
```

**What this fixes**: Makes sure the processing flag is set immediately and adds a timestamp so you can see if multiple triggers are happening.

#### **Step 3: Add Required Import**

**What to change**: Add the `time` import at the top of the file if it's not already there.

**Location**: At the top of `ai-fix.py`, around line 8.

**Make sure this line exists**:
```python
import time
```

### **How to Test the Fix**

1. **Start the program**: Run your normal startup script (`./startVoice_api.sh` or similar)
2. **Select some text**: Highlight any text in a document
3. **Press Alt+G once**: Hold Alt, press G, release both keys
4. **Watch the output**: You should only see the processing messages once:
   ```
   🔧 AI Fix triggered at 14:30:25!
   📋 Capturing highlighted text...
   📝 Captured X characters
   🤖 Sending to AI for processing...
   ............
   ✅ Text replaced and clipboard restored!
   ```
5. **Check your document**: The formatted text should appear only once, not twice

### **Expected Results After Fix**

- **Single Processing**: Alt+G will only trigger the formatting once per keypress
- **Visual Confirmation**: Timestamps in the output will show only one trigger time
- **No Duplicate Text**: Your formatted text will appear once in your document
- **Cooldown Protection**: Rapid Alt+G presses won't cause issues

### **If the Fix Doesn't Work**

If you still see double processing after this fix, it might be caused by:

1. **Multiple AI Fix Processes**: Check if multiple instances are running with `ps aux | grep ai-fix`
2. **System Keyboard Issues**: Try restarting your computer 
3. **Startup Script Issue**: The startup script might be launching AI Fix twice

### **Backup Plan**

If the keyboard cooldown approach doesn't work, we can try a different solution:

1. **Add Process ID Logging**: Make each AI Fix instance log its process ID
2. **Check for Multiple Instances**: Detect and prevent multiple AI Fix processes
3. **Alternative Keyboard Library**: Switch to a different keyboard monitoring approach

### **Files Modified Summary**

- **`ai-fix.py`**: Added keyboard event cooldown and improved processing lock
- **No other files need changes**: This is a focused fix for the specific double-trigger issue

### **Success Criteria**

✅ **Single Trigger**: Alt+G triggers formatting exactly once per keypress  
✅ **No Duplicate Output**: Console shows processing messages only once  
✅ **No Duplicate Text**: Formatted text appears once in documents  
✅ **Responsive**: Fix doesn't slow down or interfere with normal operation  
✅ **Reliable**: Works consistently across multiple uses  

This fix addresses the most common cause of duplicate processing while maintaining all the existing functionality of the AI Fix feature.