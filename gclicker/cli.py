"""CLI commands for GClicker."""

import argparse
import sys

from gclicker.dbus_service import check_gui_running, call_toggle, get_state


def main_cli():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='GClicker - Auto-clicker for Linux with Wayland support',
        prog='gclicker-cli'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='gclicker 1.0.0'
    )
    parser.add_argument(
        '--toggle',
        action='store_true',
        help='Toggle clicking (requires GUI to be running)'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current status'
    )

    args = parser.parse_args()

    # Check if GUI is running
    if not check_gui_running():
        print("Error: GClicker GUI is not running", file=sys.stderr)
        print("Please start the GUI first: gclicker", file=sys.stderr)
        sys.exit(1)

    # Handle toggle mode
    if args.toggle:
        success = call_toggle()
        if success:
            # Get the new state
            running, interval = get_state()
            if running:
                print(f"Started clicking (interval: {interval}s)")
            else:
                print("Stopped clicking")
        else:
            print("Error: Failed to toggle clicking", file=sys.stderr)
            sys.exit(1)
        return

    # Handle status mode
    if args.status:
        running, interval = get_state()
        if running:
            print(f"Status: Running (interval: {interval}s)")
        else:
            print(f"Status: Stopped (interval: {interval}s)")
        return

    # No action specified, show help
    parser.print_help()


if __name__ == '__main__':
    main_cli()
