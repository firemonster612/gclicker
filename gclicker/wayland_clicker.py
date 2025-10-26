"""Wayland portal-based clicking functionality."""

import threading
import time
import random
import string
import os
from pathlib import Path

try:
    from gi.repository import GLib, Gio
    PORTAL_AVAILABLE = True
except ImportError:
    PORTAL_AVAILABLE = False


class WaylandPortalClicker:
    """Auto-clicker using Wayland RemoteDesktop portal."""

    def __init__(self, interval=0.1):
        """
        Initialize the Wayland portal-based auto-clicker.

        Args:
            interval: Time between clicks in seconds (default 0.1s = 100ms)
        """
        if not PORTAL_AVAILABLE:
            raise RuntimeError("GLib and Gio are required for Wayland portal support")

        self.interval = interval
        self.running = False
        self._thread = None
        self._stop_event = threading.Event()

        # Portal state
        self._portal = None
        self._session_handle = None
        self._ready = False
        self._setup_error = None
        self._main_loop = None
        self._restore_token = None

        # Load saved restore token
        self._load_restore_token()

    def set_interval(self, interval):
        """Set the click interval in seconds."""
        self.interval = max(0.001, interval)

    def _generate_token(self):
        """Generate a random token for portal requests."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    def _get_token_file(self):
        """Get the path to the restore token file."""
        cache_dir = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache'))
        gclicker_cache = cache_dir / 'gclicker'
        gclicker_cache.mkdir(parents=True, exist_ok=True)
        return gclicker_cache / 'portal_restore_token'

    def _load_restore_token(self):
        """Load the saved restore token."""
        token_file = self._get_token_file()
        if token_file.exists():
            try:
                self._restore_token = token_file.read_text().strip()
            except:
                pass

    def _save_restore_token(self, token):
        """Save the restore token for next time."""
        if token:
            try:
                token_file = self._get_token_file()
                token_file.write_text(token)
            except Exception as e:
                print(f"Warning: Could not save restore token: {e}")

    def _setup_portal_session(self):
        """Set up the RemoteDesktop portal session."""
        try:
            # Connect to the RemoteDesktop portal
            self._portal = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                Gio.DBusProxyFlags.NONE,
                None,
                'org.freedesktop.portal.Desktop',
                '/org/freedesktop/portal/desktop',
                'org.freedesktop.portal.RemoteDesktop',
                None
            )

            # Create a session
            session_token = self._generate_token()
            sender_name = self._portal.get_connection().get_unique_name()[1:].replace('.', '_')
            session_path = f"/org/freedesktop/portal/desktop/session/{sender_name}/{session_token}"

            handle_token = self._generate_token()
            request_path = f"/org/freedesktop/portal/desktop/request/{sender_name}/{handle_token}"

            options = {
                'session_handle_token': GLib.Variant('s', session_token),
                'handle_token': GLib.Variant('s', handle_token)
            }

            # Subscribe to CreateSession response on the specific request path
            def on_create_session_response(connection, sender_name, object_path, interface_name,
                                          signal_name, parameters, user_data):
                response_code = parameters[0]
                results = parameters[1]

                if response_code == 0:  # Success
                    self._session_handle = results.get('session_handle', session_path)
                    # Now select devices (pointer)
                    GLib.idle_add(self._select_devices)
                else:
                    self._setup_error = f"Session creation failed with code {response_code}"
                    if self._main_loop:
                        self._main_loop.quit()

            self._portal.get_connection().signal_subscribe(
                'org.freedesktop.portal.Desktop',
                'org.freedesktop.portal.Request',
                'Response',
                request_path,  # Subscribe to this specific request path
                None,
                Gio.DBusSignalFlags.NONE,
                on_create_session_response,
                None
            )

            # Call CreateSession
            self._portal.call_sync(
                'CreateSession',
                GLib.Variant('(a{sv})', (options,)),
                Gio.DBusCallFlags.NONE,
                -1,
                None
            )

        except Exception as e:
            self._setup_error = f"Portal setup error: {e}"
            if self._main_loop:
                self._main_loop.quit()

    def _select_devices(self):
        """Select input devices (pointer)."""
        try:
            handle_token = self._generate_token()
            sender_name = self._portal.get_connection().get_unique_name()[1:].replace('.', '_')
            request_path = f"/org/freedesktop/portal/desktop/request/{sender_name}/{handle_token}"

            # Device types: KEYBOARD = 1, POINTER = 2, TOUCHSCREEN = 4
            options = {
                'types': GLib.Variant('u', 2),  # 2 = POINTER
                'handle_token': GLib.Variant('s', handle_token),
                'persist_mode': GLib.Variant('u', 2)  # 2 = persist until explicitly revoked
            }

            # Add restore token if we have one
            if self._restore_token:
                options['restore_token'] = GLib.Variant('s', self._restore_token)

            # Subscribe to SelectDevices response
            def on_select_devices_response(connection, sender_name, object_path, interface_name,
                                          signal_name, parameters, user_data):
                response_code = parameters[0]
                results = parameters[1]

                if response_code == 0:  # Success
                    # Check for restore token here too
                    if 'restore_token' in results:
                        new_token = results['restore_token']
                        self._save_restore_token(new_token)
                        self._restore_token = new_token

                    # Start the session (shows permission dialog)
                    GLib.idle_add(self._start_session)
                else:
                    self._setup_error = f"Device selection failed with code {response_code}"
                    if self._main_loop:
                        self._main_loop.quit()

            self._portal.get_connection().signal_subscribe(
                'org.freedesktop.portal.Desktop',
                'org.freedesktop.portal.Request',
                'Response',
                request_path,  # Subscribe to this specific request path
                None,
                Gio.DBusSignalFlags.NONE,
                on_select_devices_response,
                None
            )

            # Call SelectDevices
            self._portal.call_sync(
                'SelectDevices',
                GLib.Variant('(oa{sv})', (self._session_handle, options)),
                Gio.DBusCallFlags.NONE,
                -1,
                None
            )

        except Exception as e:
            self._setup_error = f"Device selection error: {e}"
            if self._main_loop:
                self._main_loop.quit()

        return False  # Don't repeat

    def _start_session(self):
        """Start the portal session (shows permission dialog)."""
        try:
            handle_token = self._generate_token()
            sender_name = self._portal.get_connection().get_unique_name()[1:].replace('.', '_')
            request_path = f"/org/freedesktop/portal/desktop/request/{sender_name}/{handle_token}"

            options = {
                'handle_token': GLib.Variant('s', handle_token)
            }

            # Subscribe to Start response
            def on_start_response(connection, sender_name, object_path, interface_name,
                                 signal_name, parameters, user_data):
                response_code = parameters[0]
                results = parameters[1]

                if response_code == 0:  # Success - permission granted
                    self._ready = True

                    # Save restore token if provided
                    if 'restore_token' in results:
                        new_token = results['restore_token']
                        self._save_restore_token(new_token)
                        self._restore_token = new_token

                    if self._restore_token:
                        print("Session restored - ready to click!")
                    else:
                        print("Permission granted - session ready!")
                else:
                    self._setup_error = f"Session start failed with code {response_code} (permission denied?)"

                # Either way, we're done with setup
                if self._main_loop:
                    self._main_loop.quit()

            self._portal.get_connection().signal_subscribe(
                'org.freedesktop.portal.Desktop',
                'org.freedesktop.portal.Request',
                'Response',
                request_path,  # Subscribe to this specific request path
                None,
                Gio.DBusSignalFlags.NONE,
                on_start_response,
                None
            )

            # Call Start - this shows the permission dialog
            self._portal.call_sync(
                'Start',
                GLib.Variant('(osa{sv})', (self._session_handle, '', options)),
                Gio.DBusCallFlags.NONE,
                -1,
                None
            )

        except Exception as e:
            self._setup_error = f"Session start error: {e}"
            if self._main_loop:
                self._main_loop.quit()

        return False  # Don't repeat

    def _click(self):
        """Perform a single mouse click using the portal."""
        if not self._ready or not self._portal:
            return

        try:
            # Button code: 0x110 = BTN_LEFT (272 in decimal)
            # State: 1 = pressed, 0 = released
            # The signature is (oa{sv}iu): object path, options dict, button, state

            options = {}  # Empty options dict

            # Press button
            self._portal.call_sync(
                'NotifyPointerButton',
                GLib.Variant('(oa{sv}iu)', (self._session_handle, options, 0x110, 1)),
                Gio.DBusCallFlags.NONE,
                -1,
                None
            )

            # Small delay
            time.sleep(0.001)

            # Release button
            self._portal.call_sync(
                'NotifyPointerButton',
                GLib.Variant('(oa{sv}iu)', (self._session_handle, options, 0x110, 0)),
                Gio.DBusCallFlags.NONE,
                -1,
                None
            )

        except Exception as e:
            print(f"Error clicking: {e}", flush=True)

    def _click_loop(self):
        """Main clicking loop."""
        while not self._stop_event.is_set():
            self._click()
            time.sleep(self.interval)

    def start(self):
        """Start auto-clicking."""
        if self.running:
            return True

        # Set up portal session if not ready
        if not self._ready:
            if self._restore_token:
                print("Restoring portal session...")
            else:
                print("Setting up Wayland portal session...")
                print("A permission dialog will appear - please grant access")

            # Create and run the main loop in this thread
            self._main_loop = GLib.MainLoop()

            # Start the setup process
            GLib.idle_add(self._setup_portal_session)

            # Set a timeout to prevent hanging forever
            def timeout_handler():
                if not self._ready and not self._setup_error:
                    self._setup_error = "Timeout waiting for portal setup"
                if self._main_loop:
                    self._main_loop.quit()
                return False

            GLib.timeout_add_seconds(30, timeout_handler)

            # Run the main loop (this blocks until setup completes or timeout)
            self._main_loop.run()
            self._main_loop = None

            if self._setup_error:
                print(f"Portal setup failed: {self._setup_error}")
                return False

            if not self._ready:
                print("Portal setup failed: Unknown error")
                return False

        # Start clicking
        self.running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._click_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        """Stop auto-clicking."""
        if not self.running:
            return

        self.running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        self._thread = None

    def is_running(self):
        """Check if auto-clicker is running."""
        return self.running

    def cleanup(self):
        """Clean up portal resources."""
        self.stop()

        if self._session_handle and self._portal:
            try:
                # Close the session
                self._portal.call_sync(
                    'Close',
                    GLib.Variant('(o)', (self._session_handle,)),
                    Gio.DBusCallFlags.NONE,
                    -1,
                    None
                )
            except:
                pass

        self._portal = None
        self._session_handle = None
        self._ready = False
