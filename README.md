# GClicker

A Wayland-native Linux auto-clicker with GTK4/libadwaita GUI and CLI interface.

## Installation

```bash
git clone https://github.com/firemonster612/gclicker.git
cd gclicker
./install.sh
```

### Uninstall

```bash
pip uninstall gclicker
```

## Usage

### GUI

Launch the graphical interface:
```bash
gclicker
```

Set click interval using the spinboxes (minutes, seconds, milliseconds) and use Start/Stop buttons to control clicking.

### CLI

Control GClicker from the command line:

```bash
gclicker-cli --toggle          # Toggle clicking on/off
gclicker-cli --stop            # Stop clicking
gclicker-cli --status          # Show current status
gclicker-cli -i 0.5 --toggle   # Set interval and toggle
```

The CLI and GUI share state via D-Bus, so CLI commands control the GUI if it's running.

## Configuration

### Global Keyboard Shortcut

Configure a keyboard shortcut in GNOME Settings:

1. Open **Settings** → **Keyboard** → **Keyboard Shortcuts**
2. Scroll to **Custom Shortcuts** and click **+**
3. Name: `Toggle GClicker`
4. Command: `gclicker-cli --toggle`
5. Set your preferred shortcut (e.g., `F8`)

This allows you to toggle clicking from anywhere without opening the GUI.


