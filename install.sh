#!/bin/bash

# GClicker Installation Script

set -e

echo "=== GClicker Installation ==="
echo

# Detect distribution
if [ -f /etc/os-release ]; then
  . /etc/os-release
  DISTRO=$ID
else
  echo "Cannot detect Linux distribution"
  exit 1
fi

echo "Detected distribution: $DISTRO"
echo

# Install system dependencies
echo "Installing system dependencies..."

case $DISTRO in
fedora)
  sudo dnf install -y python3-gobject gtk4 libadwaita python3-pip
  ;;
ubuntu | debian)
  sudo apt update
  sudo apt install -y python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 python3-pip
  ;;
arch | manjaro)
  sudo pacman -S --noconfirm python-gobject gtk4 libadwaita python-pip
  ;;
*)
  echo "Unsupported distribution: $DISTRO"
  echo "Please install manually:"
  echo "  - python3-gobject"
  echo "  - gtk4"
  echo "  - libadwaita"
  exit 1
  ;;
esac

echo
echo "Installing GClicker..."
pip install -e .

echo
echo "HINT: make sure /home/$USER/.local/bin is in path"
echo "=== Installation Complete ==="
echo
echo "Usage:"
echo "  gclicker                   - Launch GUI"
echo "  gclicker-cli -i 0.1        - Start CLI with 0.1s interval"
echo "  gclicker-cli --toggle      - Toggle on/off (daemon mode)"
echo "  gclicker-cli --stop        - Stop all instances"
echo
echo "See README.md for more options and setting up global hotkeys."
echo
