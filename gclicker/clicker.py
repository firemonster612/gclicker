"""Core clicking functionality."""

import signal
import sys
import time

from gclicker.wayland_clicker import WaylandPortalClicker


def run_clicker_standalone(interval=0.1):
    """
    Run the clicker as a standalone process.

    Args:
        interval: Click interval in seconds
    """
    clicker = WaylandPortalClicker(interval)

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\nStopping clicker...")
        clicker.stop()
        clicker.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"Starting auto-clicker with {interval}s interval...")
    print("Press Ctrl+C to stop")

    success = clicker.start()

    if not success:
        sys.exit(1)

    # Keep the main thread alive
    try:
        while clicker.is_running():
            time.sleep(0.1)
    except KeyboardInterrupt:
        clicker.stop()
        clicker.cleanup()
