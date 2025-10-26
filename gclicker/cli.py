"""CLI commands for GClicker."""

import argparse
import os
import sys
import signal
from pathlib import Path

from gclicker.clicker import run_clicker_standalone


def get_pid_file():
    """Get the path to the PID file."""
    runtime_dir = os.environ.get('XDG_RUNTIME_DIR', '/tmp')
    return Path(runtime_dir) / 'gclicker.pid'


def get_running_pids():
    """Get list of running gclicker PIDs."""
    pids = []
    pid_file = get_pid_file()

    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                for line in f:
                    pid = int(line.strip())
                    # Check if process is still running
                    try:
                        os.kill(pid, 0)  # Signal 0 just checks if process exists
                        pids.append(pid)
                    except OSError:
                        # Process doesn't exist
                        pass
        except (ValueError, IOError):
            pass

    return pids


def save_pid(pid):
    """Save a PID to the PID file."""
    pid_file = get_pid_file()
    existing_pids = get_running_pids()

    with open(pid_file, 'w') as f:
        for existing_pid in existing_pids:
            f.write(f"{existing_pid}\n")
        f.write(f"{pid}\n")


def remove_pid(pid):
    """Remove a PID from the PID file."""
    pid_file = get_pid_file()
    pids = get_running_pids()

    if pid in pids:
        pids.remove(pid)

    if pids:
        with open(pid_file, 'w') as f:
            for p in pids:
                f.write(f"{p}\n")
    else:
        # No more PIDs, remove the file
        if pid_file.exists():
            pid_file.unlink()


def main_cli():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='GClicker - Auto-clicker for Linux with Wayland support',
        prog='gclicker'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='gclicker 1.0.0'
    )
    parser.add_argument(
        '-i', '--interval',
        type=float,
        default=0.1,
        help='Click interval in seconds (default: 0.1)'
    )
    parser.add_argument(
        '-d', '--daemon',
        action='store_true',
        help='Run in background as daemon'
    )
    parser.add_argument(
        '--toggle',
        action='store_true',
        help='Toggle: stop if running, start if not (implies --daemon)'
    )
    parser.add_argument(
        '--stop',
        action='store_true',
        help='Stop all running instances'
    )

    args = parser.parse_args()

    # Handle stop mode
    if args.stop:
        pids = get_running_pids()

        if not pids:
            print("No gclicker processes found")
            return

        print(f"Stopping {len(pids)} gclicker process(es)...")

        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"  Stopped PID {pid}")
            except OSError as e:
                print(f"  Failed to stop PID {pid}: {e}", file=sys.stderr)

        # Clean up PID file
        pid_file = get_pid_file()
        if pid_file.exists():
            pid_file.unlink()

        print("Done")
        return

    # Handle toggle mode
    if args.toggle:
        pids = get_running_pids()

        if pids:
            # Instances running - stop them
            print(f"Stopping {len(pids)} running instance(s)...")
            for pid in pids:
                try:
                    os.kill(pid, signal.SIGTERM)
                    print(f"  Stopped PID {pid}")
                except OSError as e:
                    print(f"  Failed to stop PID {pid}: {e}", file=sys.stderr)

            # Clean up PID file
            pid_file = get_pid_file()
            if pid_file.exists():
                pid_file.unlink()

            print("Stopped")
            sys.exit(0)
        else:
            # No instances running - start one
            print("No instances running, starting...")
            args.daemon = True  # Toggle implies daemon mode

    # Validate interval
    if args.interval < 0.001:
        print("Error: Interval must be at least 0.001 seconds", file=sys.stderr)
        sys.exit(1)

    # CLI mode - start clicking
    if args.daemon:
        # Fork to background
        pid = os.fork()
        if pid > 0:
            # Parent process
            save_pid(pid)
            print(f"Started gclicker with PID {pid}")
            print(f"Interval: {args.interval}s")
            print(f"Stop with: gclicker-cli --stop")
            sys.exit(0)

        # Child process - detach from terminal
        os.setsid()

        # Redirect stdin/stdout/stderr to /dev/null instead of closing
        # (Portal code needs to write to stderr)
        devnull = open(os.devnull, 'r+')
        os.dup2(devnull.fileno(), sys.stdin.fileno())
        os.dup2(devnull.fileno(), sys.stdout.fileno())
        os.dup2(devnull.fileno(), sys.stderr.fileno())
        devnull.close()

        # PID already saved by parent, just run
        try:
            run_clicker_standalone(args.interval)
        finally:
            remove_pid(os.getpid())
    else:
        # Run in foreground
        save_pid(os.getpid())
        try:
            run_clicker_standalone(args.interval)
        finally:
            remove_pid(os.getpid())


if __name__ == '__main__':
    main_cli()
