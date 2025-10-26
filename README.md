# GClicker

A simple auto-clicker for Linux with Wayland support, featuring both GUI and CLI interfaces.

## Features

- **Native Wayland Support**: Uses Wayland RemoteDesktop portal - no root access or special permissions needed!
- **Global Hotkey Support**: Built-in global hotkey (default F8) to toggle clicking from anywhere
- **Unified GUI/CLI Control**: Control clicking via GUI buttons, global hotkey, or CLI commands
- **Session Persistence**: Grant permission once, never see the dialog again!
- **GTK4 GUI**: Beautiful native GNOME interface with interval control and preferences
- **CLI Integration**: Command-line interface that communicates with the GUI
- **Configurable Interval**: Set click interval from 0.001 seconds to minutes
- **Real-time Sync**: UI updates automatically whether you use GUI, hotkey, or CLI

## Requirements

- Python 3.8+
- GTK4 and libadwaita (for GUI)
- PyGObject (Python GTK bindings)
- pynput (for global hotkey support)
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
1. Click "Start" or press the hotkey (default: F8)
2. A system permission dialog will appear asking for RemoteDesktop access
3. Grant permission
4. Clicking begins!

**Every time after:**
- No permission dialog! Session is automatically restored.
- Use any control method instantly: GUI buttons, hotkey, or CLI

Features:
- **Global Hotkey**: Press F8 (configurable) to toggle clicking from anywhere
- **Preferences**: Configure global hotkey in the menu
- **Interval Control**: Set precise intervals (minutes, seconds, milliseconds)
- **Start/Stop**: Use GUI buttons, hotkey, or CLI - all stay in sync
- **Status Indicator**: UI updates automatically from any control method

### CLI Mode

**Important:** The CLI requires the GUI to be running. It communicates with the GUI via D-Bus to control clicking.

```bash
# Toggle clicking (start if stopped, stop if running)
gclicker-cli --toggle

# Check current status
gclicker-cli --status

# Show help
gclicker-cli --help
```

**Workflow:**
1. Start the GUI: `gclicker`
2. Configure your interval in the GUI
3. Use CLI to toggle: `gclicker-cli --toggle`
4. The GUI updates automatically to reflect the state

**Note:** All control methods (GUI buttons, global hotkey, CLI commands) work together seamlessly and keep the UI synchronized.

### Global Hotkey

GClicker has built-in global hotkey support! By default, pressing **F8** will toggle clicking on/off.

**Configuring the Hotkey:**

1. Open GClicker
2. Click the menu button (☰) → **Preferences**
3. Change the hotkey to your preference (e.g., `<ctrl>+<alt>+c`, `<f9>`, etc.)
4. Changes apply immediately!

**Hotkey Format:**
- Function keys: `<f8>`, `<f9>`, etc.
- With modifiers: `<ctrl>+<alt>+c`, `<shift>+<f5>`, etc.
- Any combination supported by your system

**Optional: Additional CLI Hotkeys**

You can also create GNOME keyboard shortcuts that call CLI commands:

1. Open **Settings** → **Keyboard** → **Keyboard Shortcuts**
2. Scroll down and click **Custom Shortcuts**
3. Click **+** to add:
   - Name: `Toggle GClicker`
   - Command: `gclicker-cli --toggle`
   - Shortcut: Your choice (e.g., `Ctrl+Alt+C`)

## Command-Line Options

**GUI:**
```
gclicker    # Launch GUI with built-in hotkey support
```

**CLI:**
```
usage: gclicker-cli [-h] [--version] [--toggle] [--status]

GClicker - Auto-clicker for Linux with Wayland support

options:
  -h, --help     show this help message and exit
  --version      show program's version number and exit
  --toggle       Toggle clicking (requires GUI to be running)
  --status       Show current status
```

**Note:** The CLI requires the GUI to be running. It communicates with the GUI process to control clicking.

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

### Global hotkey doesn't work

On pure Wayland sessions, global hotkey support may be limited due to Wayland's security model. If the built-in hotkey doesn't work:

1. **Recommended**: Use GNOME keyboard shortcuts (see "Optional: Additional CLI Hotkeys" section above)
2. **Alternative**: Run under XWayland (most systems have this by default)

The built-in hotkey works best on X11 or XWayland-compatible setups.

### Nothing happens when clicking starts

Check if your Wayland compositor supports the RemoteDesktop portal. Most modern compositors (GNOME 3.38+, KDE Plasma 5.23+) support it.

## How It Works

- **Wayland RemoteDesktop Portal**: Uses the official D-Bus portal API for secure, permission-based input control
- **Session Persistence**: Saves restore tokens to `~/.cache/gclicker/` so you only grant permission once
- **No Root Required**: The portal handles permissions through the desktop environment
- **D-Bus IPC**: GUI exposes a D-Bus service that CLI and hotkeys use to control clicking
- **Global Hotkeys**: Uses pynput to listen for system-wide keyboard events
- **Threading**: Clicks run in a separate thread to keep the UI responsive
- **Real-time Sync**: All control methods update the GUI state immediately
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
