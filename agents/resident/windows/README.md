# Heystive Windows Resident Wake-Word Service

This directory contains the Windows-specific implementation of the Heystive resident wake-word service that keeps the assistant listening in the background.

## Files

- `watcher_win.py` - Main wake-word detection service
- `run_resident.bat` - Batch launcher script
- `install_task.ps1` - PowerShell script to install as Windows scheduled task
- `uninstall_task.ps1` - PowerShell script to remove the scheduled task

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the unified server:**
   ```bash
   python server/main.py
   ```

3. **Test the watcher manually:**
   ```bash
   python agents\resident\windows\watcher_win.py
   ```

4. **Install as auto-start service:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File agents\resident\windows\install_task.ps1
   ```

5. **Uninstall the service:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File agents\resident\windows\uninstall_task.ps1
   ```

## Configuration

The service reads configuration from the Heystive settings API at `http://127.0.0.1:8765/api/settings`:

- `wakeword_enabled` (bool) - Enable/disable wake-word detection
- `wakeword_keyword` (str) - Wake-word phrase (default: "hey steve")
- `wakeword_sensitivity` (float) - Detection sensitivity 0.1-0.9 (default: 0.5)
- `wakeword_device_index` (int|null) - Audio device index (null for system default)

## Features

- **Local processing** - No cloud calls, all processing happens locally
- **Voice Activity Detection** - Uses WebRTC VAD to filter out non-speech audio
- **Debouncing** - Prevents multiple triggers within 5 seconds
- **Dynamic configuration** - Settings changes apply without restart
- **Low CPU usage** - Optimized for background operation
- **Auto-start** - Installs as Windows scheduled task for automatic startup

## Privacy & Security

- All audio processing is local
- No data is sent to external services
- Only communicates with local Heystive server
- Can be completely disabled via settings or uninstalled