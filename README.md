# Gclicker (goated clicker)

Gclicker is a wayland native linux auto clicker written with python3 and GTK4/libadwaita

## Installation

Clone the repo:
```bash
git clone https://github.com/firemonster612/gclicker.git
cd gclicker
```

Run the install.sh
```bash
./install.sh
```

Uninstall:
`pip uninstall gclicker`

## Usage

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -i, --interval INTERVAL   Click interval in seconds (default: 0.1)
  --toggle              Toggle: stop if running, start if not
  --stop                Stop all running instances
  --status              Show current status

By running `gclicker` in a terminal you can start the UI.
You can also use gclicker-cli to run a headless gclicker instance

The UI and CLI have shared state allowing the CLI to control the UI, for example running:
```
gclicker-cli --toggle
```
While the GUI is running will use the current click interval set in the GUI and will update It's state (e.g. Graying out the start button). Running it with no UI will run gclicker in the background in the terminal.

A quick tip is to set `gclicker --toggle` as a global shortcut in settings so you always have a toggle for gclicker ready.


