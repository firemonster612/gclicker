# GClicker

A simple auto-clicker for Linux with Wayland support, featuring both GUI and CLI interfaces.

## Features

- **Native Wayland Support**: Uses Wayland RemoteDesktop portal - no root access or special permissions needed!
- **Session Persistence**: Grant permission once, never see the dialog again!
- **Toggle Mode**: Single command to start/stop - perfect for keyboard shortcuts
- **GTK4 GUI**: Beautiful native GNOME interface with interval control
- **CLI Support**: Command-line interface for scripting and global hotkeys
- **Configurable Interval**: Set click interval from 0.001 to 10 seconds
- **Background Mode**: Run as daemon for hotkey integration

## Requirements

- Python 3.8+
- GTK4 and libadwaita (for GUI)
- PyGObject (Python GTK bindings)
- A Wayland compositor with RemoteDesktop portal support (GNOME, KDE Plasma, etc.)

## Installation

### 1. Install System Dependencies

**Fedora:**
```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

**Ubuntu/Debian:**
```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1
```

**Arch:**
```bash
sudo pacman -S python-gobject gtk4 libadwaita
```

### 2. Install GClicker

From the project directory:

```bash
pip install -e .
```

Or for system-wide installation:
```bash
sudo pip install .
```

Or use the install script:
```bash
chmod +x install.sh
./install.sh
```

## Usage

### GUI Mode

Launch the graphical interface:

```bash
gclicker
```

**First time:**
1. Click "Start"
2. A system permission dialog will appear asking for RemoteDesktop access
3. Grant permission
4. Clicking begins!

**Every time after:**
- No permission dialog! Session is automatically restored.
- Just click "Start" and it works instantly.

Features:
- Set click interval with spin button or preset buttons
- Start/Stop clicking with buttons
- Visual status indicator

### CLI Mode

```bash
# Start clicking in foreground (default 0.1s interval)
gclicker-cli

# Start with custom interval (0.5 seconds)
gclicker-cli -i 0.5

# Start in background (daemon mode)
gclicker-cli -d

# Background with custom interval
gclicker-cli -i 0.2 -d

# Toggle mode - start if stopped, stop if running (daemon mode)
gclicker-cli --toggle

# Toggle with custom interval
gclicker-cli --toggle -i 0.5

# Stop all running instances
gclicker-cli --stop
```

**Note:** The first time you run this, a permission dialog will appear. Grant access to RemoteDesktop control. After that, the session is saved and no permission dialog will appear again!

### Setting Up Global Hotkeys in GNOME

You can bind commands to keyboard shortcuts in GNOME Settings:

1. Open **Settings** → **Keyboard** → **Keyboard Shortcuts**
2. Scroll down and click **Custom Shortcuts**
3. Click **+** to add a new shortcut

**Recommended: Toggle Mode (one key for start/stop):**

- **Toggle clicking:**
  - Name: `Toggle GClicker`
  - Command: `gclicker-cli --toggle -i 0.1`
  - Shortcut: `Ctrl+Alt+C`

Press once to start, press again to stop!

**Alternative: Separate Keys:**

- **Start clicking:**
  - Name: `Start GClicker`
  - Command: `gclicker-cli -d -i 0.1`
  - Shortcut: `Ctrl+Alt+C`

- **Stop clicking:**
  - Name: `Stop GClicker`
  - Command: `gclicker-cli --stop`
  - Shortcut: `Ctrl+Alt+S`

## Command-Line Options

**GUI:**
```
gclicker    # Launch GUI
```

**CLI:**
```
usage: gclicker-cli [-h] [--version] [-i INTERVAL] [-d] [--toggle] [--stop]

GClicker - Auto-clicker for Linux with Wayland support

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -i INTERVAL, --interval INTERVAL
                        Click interval in seconds (default: 0.1)
  -d, --daemon          Run in background as daemon
  --toggle              Toggle: stop if running, start if not (implies --daemon)
  --stop                Stop all running instances
```

## Troubleshooting

### Permission dialog doesn't appear

Make sure you're running on a Wayland session with portal support:

```bash
echo $XDG_SESSION_TYPE  # Should show "wayland"
```

If you're on X11, Wayland portals are not supported.

### "Failed to start (permission denied?)" error

You may have denied the permission request. To grant it:

1. Open GNOME Settings → Privacy → Screen Sharing
2. Enable screen sharing for GClicker
3. Try starting again

Or on KDE: Settings → Workspace Behavior → Screen Locking

### Nothing happens when clicking starts

Check if your Wayland compositor supports the RemoteDesktop portal. Most modern compositors (GNOME 3.38+, KDE Plasma 5.23+) support it.

## How It Works

- **Wayland RemoteDesktop Portal**: Uses the official D-Bus portal API for secure, permission-based input control
- **Session Persistence**: Saves restore tokens to `~/.cache/gclicker/` so you only grant permission once
- **No Root Required**: The portal handles permissions through the desktop environment
- **Threading**: Clicks run in a separate thread to keep the UI responsive
- **PID Management**: CLI mode tracks process IDs to allow clean stopping and toggle functionality
- **GTK4**: Modern GNOME interface with libadwaita styling

## Revoking Portal Permissions

To revoke the RemoteDesktop permission:

```bash
# Delete the saved session token
rm ~/.cache/gclicker/portal_restore_token

# Or revoke in system settings:
# GNOME: Settings → Privacy → Screen Sharing → Remove GClicker
# KDE: Settings → Workspace Behavior → Screen Locking
```

## Uninstallation

```bash
pip uninstall gclicker
```

## License

MIT License - feel free to use and modify as needed.
