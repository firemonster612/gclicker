"""Settings management for gclicker."""

import json
import os
from pathlib import Path


class Settings:
    """Manage gclicker settings."""

    DEFAULT_HOTKEY = '<f8>'

    def __init__(self):
        """Initialize settings."""
        self.config_dir = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'gclicker'
        self.config_file = self.config_dir / 'settings.json'
        self._settings = self._load()

    def _load(self):
        """Load settings from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")

        return self._defaults()

    def _defaults(self):
        """Get default settings."""
        return {
            'hotkey': self.DEFAULT_HOTKEY,
        }

    def save(self):
        """Save settings to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    @property
    def hotkey(self):
        """Get the configured hotkey."""
        return self._settings.get('hotkey', self.DEFAULT_HOTKEY)

    @hotkey.setter
    def hotkey(self, value):
        """Set the hotkey."""
        self._settings['hotkey'] = value
        self.save()
