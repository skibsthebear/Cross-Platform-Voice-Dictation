# Investigation: System Shutdown Issues

## Executive Summary

After thorough investigation of the codebase, I've identified multiple potential causes for the unexpected system shutdowns. The issue appears to be a combination of keyboard handling conflicts, process management issues, and exit signal propagation between different components.

## Root Causes Identified

### 1. **ESC Key Triggers Immediate Shutdown** (PRIMARY ISSUE)

**Location**: `keyboard_handler.py:50-55`

The ESC key is configured to immediately exit the entire application:

```python
# Check for Escape
if key == Key.esc:
    print("\n=K Exiting...")
    if self.on_exit:
        self.on_exit()
    return False  # Stop listener
```

**Problem**: 
- Pressing ESC at ANY time will immediately terminate the voice typing application
- This is likely being pressed accidentally during normal use
- The exit is immediate with no confirmation or grace period
- When the main app exits, the startup script's cleanup function triggers, killing all processes

### 2. **Device Selection Exit Points**

**Location**: `audio_device.py:109-110, 147-148`

During device selection, Ctrl+C or invalid inputs trigger `sys.exit(0)`:

```python
except KeyboardInterrupt:
    print("\n\n=K Cancelled by user.")
    sys.exit(0)
```

**Problem**:
- During startup, any keyboard interrupt exits the entire application
- No way to recover from accidental Ctrl+C during device selection

### 3. **AI Fix Restart Loop Can Cause Main App Exit**

**Location**: `startVoice_gpu.sh:78-85`

The AI Fix restart loop might be interfering with the main application:

```bash
start_ai_fix() {
    while true; do
        echo "> Starting AI Fix (Alt+G)..."
        python ai-fix.py
        echo "   AI Fix exited. Restarting in 2 seconds..."
        sleep 2
    done
}
```

**Problem**:
- If AI Fix fails to acquire lock (from our recent fix), it exits with `sys.exit(1)`
- The restart loop immediately tries again, potentially causing resource conflicts
- Multiple restart attempts could trigger the parent script's error handling

### 4. **Trap Handler Cascading Exits**

**Location**: `startVoice_gpu.sh:33` and `startVoice_api.sh:40`

```bash
trap cleanup SIGINT SIGTERM EXIT
```

**Problem**:
- The trap catches ALL exits, including normal ones
- When voice_ptt.py exits for ANY reason, the cleanup function runs
- Cleanup function kills ALL background processes including AI Fix
- This makes it impossible to restart just one component

### 5. **Recording Thread Management Issues**

**Location**: `voice_ptt.py:41-58`

The recording thread management has potential race conditions:

```python
self.recording_thread = threading.Thread(target=self._record_and_transcribe)
self.recording_thread.start()
# ...
self.recording_thread.join(timeout=5)
if self.recording_thread.is_alive():
    print("   Recording thread still alive after timeout!")
```

**Problem**:
- If the recording thread doesn't finish within 5 seconds, it's abandoned
- Abandoned threads can cause resource conflicts
- No cleanup for threads that timeout

## Specific Shutdown Scenarios

### Scenario 1: Accidental ESC Press
1. User presses ESC key (accidentally or intentionally)
2. `keyboard_handler.py` immediately triggers `on_exit()` callback
3. `voice_ptt.py` cleanup() is called
4. Main application exits
5. Startup script's trap handler activates
6. All processes are killed

### Scenario 2: Recording Completion Triggers Exit
From your log output:
```
 Recording thread finished
ù  Recording indicator stopped
=K Exiting...
Voice typing exited. Cleaning up...
```

This suggests the application is exiting immediately after a successful recording, which shouldn't happen. The likely cause:
- After transcription completes, something is triggering the exit condition
- Possibly a keyboard event is being misinterpreted
- Or the thread completion is somehow signaling an exit

### Scenario 3: AI Fix Lock Conflict
1. AI Fix tries to start but finds existing lock
2. Returns `sys.exit(1)`
3. Restart loop immediately tries again
4. Multiple failures might trigger parent script error handling

## Critical Code Issues

### Issue 1: No Exit Confirmation
The ESC key immediately exits without any confirmation or delay. This is too easy to trigger accidentally.

### Issue 2: Thread Lifecycle Management
Recording threads can be abandoned if they take too long, leading to resource leaks.

### Issue 3: Process Restart Logic
The AI Fix restart loop doesn't check why the process exited before restarting.

### Issue 4: Exit Signal Propagation
Exit signals cascade through all components, making targeted restarts impossible.

## Recommendations

### Immediate Fixes Needed

1. **Disable or Modify ESC Key Exit**
   - Remove ESC key as exit trigger
   - Or require double-press/confirmation
   - Or add a timeout (ESC must be held for 2 seconds)

2. **Fix Recording Thread Completion**
   - Investigate why app exits after successful recording
   - Check if keyboard state is being misread after Alt+R release

3. **Improve AI Fix Restart Logic**
   - Check exit code before restarting
   - Add exponential backoff for restart attempts
   - Don't restart if lock acquisition fails

4. **Better Process Management**
   - Use process groups for better control
   - Implement graceful shutdown sequences
   - Allow individual component restarts

### Long-term Improvements

1. **Implement State Machine**
   - Clear states: IDLE, RECORDING, PROCESSING, ERROR
   - State transitions should be explicit
   - Exit should only be possible from IDLE state

2. **Add Logging System**
   - Log all state changes
   - Log all keyboard events
   - Log all exit triggers with stack traces

3. **Separate Control Interface**
   - Move exit control to a different key combination
   - Add status display showing current state
   - Implement command interface for debugging

## Most Likely Culprit

Based on the evidence, the **ESC key handler** is the most likely cause of unexpected shutdowns. Users are probably pressing ESC accidentally during normal use, which immediately terminates the entire application stack.

The second most likely issue is something in the recording completion flow that's triggering an exit condition instead of returning to idle state.

## Testing Recommendations

1. **Disable ESC key exit** temporarily and see if shutdowns stop
2. **Add verbose logging** around all exit points
3. **Monitor keyboard events** to see what keys are pressed before shutdown
4. **Test recording multiple times** in succession to identify patterns
5. **Check system logs** for any OS-level signals or errors

## Conclusion

The system is too eager to shut down due to multiple hair-trigger exit conditions. The primary issue is likely the ESC key handler, but there are also structural issues with how processes are managed and restarted. A comprehensive fix would involve:

1. Making exit conditions more deliberate (not accidental)
2. Improving process lifecycle management
3. Adding proper state management
4. Implementing better error recovery

The immediate priority should be disabling or modifying the ESC key exit handler and investigating why the application exits after successful recording completion.