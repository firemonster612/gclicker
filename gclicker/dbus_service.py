"""D-Bus service for gclicker GUI/CLI communication."""

import threading
from gi.repository import Gio, GLib
from gclicker.wayland_clicker import WaylandPortalClicker


# D-Bus XML interface definition
DBUS_INTERFACE = '''
<node>
  <interface name='org.gclicker.Control'>
    <method name='Toggle'>
      <arg type='b' name='success' direction='out'/>
    </method>
    <method name='GetState'>
      <arg type='b' name='running' direction='out'/>
      <arg type='d' name='interval' direction='out'/>
    </method>
    <method name='SetInterval'>
      <arg type='d' name='interval' direction='in'/>
      <arg type='b' name='success' direction='out'/>
    </method>
    <signal name='StateChanged'>
      <arg type='b' name='running'/>
      <arg type='d' name='interval'/>
    </signal>
  </interface>
</node>
'''


class GClickerDBusService:
    """D-Bus service for controlling gclicker."""

    BUS_NAME = 'org.gclicker.Service'
    OBJECT_PATH = '/org/gclicker/Control'

    def __init__(self, clicker, on_state_changed=None):
        """
        Initialize the D-Bus service.

        Args:
            clicker: WaylandPortalClicker instance to control
            on_state_changed: Callback function when state changes (running, interval)
        """
        self.clicker = clicker
        self.on_state_changed = on_state_changed
        self.connection = None
        self.registration_id = None
        self.name_owner_id = None

    def _handle_method_call(self, connection, sender, object_path, interface_name,
                           method_name, parameters, invocation):
        """Handle D-Bus method calls."""
        try:
            if method_name == 'Toggle':
                success = self._toggle()
                invocation.return_value(GLib.Variant('(b)', (success,)))

            elif method_name == 'GetState':
                running = self.clicker.is_running()
                interval = self.clicker.interval
                invocation.return_value(GLib.Variant('(bd)', (running, interval)))

            elif method_name == 'SetInterval':
                interval = parameters[0]
                self.clicker.set_interval(interval)
                self._emit_state_changed()
                invocation.return_value(GLib.Variant('(b)', (True,)))

            else:
                invocation.return_error_literal(
                    Gio.dbus_error_quark(),
                    Gio.DBusError.UNKNOWN_METHOD,
                    f"Unknown method: {method_name}"
                )
        except Exception as e:
            invocation.return_error_literal(
                Gio.dbus_error_quark(),
                Gio.DBusError.FAILED,
                f"Method call failed: {e}"
            )

    def _toggle(self):
        """Toggle the clicker state."""
        if self.clicker.is_running():
            self.clicker.stop()
        else:
            # Start in a thread to avoid blocking
            def start_thread():
                success = self.clicker.start()
                # Emit state change after starting
                GLib.idle_add(self._emit_state_changed)
                # Notify the callback
                if self.on_state_changed:
                    GLib.idle_add(lambda: self.on_state_changed(
                        self.clicker.is_running(),
                        self.clicker.interval
                    ))
                return False

            threading.Thread(target=start_thread, daemon=True).start()
            # Return True immediately, actual state change will be signaled
            return True

        # For stop, emit immediately
        self._emit_state_changed()

        # Notify the callback
        if self.on_state_changed:
            self.on_state_changed(self.clicker.is_running(), self.clicker.interval)

        return True

    def _emit_state_changed(self):
        """Emit StateChanged signal."""
        if not self.connection:
            return

        try:
            running = self.clicker.is_running()
            interval = self.clicker.interval

            self.connection.emit_signal(
                None,  # destination (broadcast)
                self.OBJECT_PATH,
                'org.gclicker.Control',
                'StateChanged',
                GLib.Variant('(bd)', (running, interval))
            )
        except Exception as e:
            print(f"Error emitting state change signal: {e}")

    def start(self):
        """Start the D-Bus service."""
        try:
            # Get the session bus
            self.connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)

            # Parse the interface
            node_info = Gio.DBusNodeInfo.new_for_xml(DBUS_INTERFACE)
            interface_info = node_info.lookup_interface('org.gclicker.Control')

            # Register the object
            self.registration_id = self.connection.register_object(
                self.OBJECT_PATH,
                interface_info,
                self._handle_method_call,
                None,  # get_property
                None   # set_property
            )

            # Own the bus name
            def on_bus_acquired(connection, name):
                print(f"D-Bus service acquired name: {name}")

            def on_name_acquired(connection, name):
                print(f"D-Bus service registered: {name}")

            def on_name_lost(connection, name):
                print(f"D-Bus service lost name: {name}")

            self.name_owner_id = Gio.bus_own_name(
                Gio.BusType.SESSION,
                self.BUS_NAME,
                Gio.BusNameOwnerFlags.NONE,
                on_bus_acquired,
                on_name_acquired,
                on_name_lost
            )

            return True

        except Exception as e:
            print(f"Failed to start D-Bus service: {e}")
            return False

    def stop(self):
        """Stop the D-Bus service."""
        if self.registration_id:
            self.connection.unregister_object(self.registration_id)
            self.registration_id = None

        if self.name_owner_id:
            Gio.bus_unown_name(self.name_owner_id)
            self.name_owner_id = None

        self.connection = None


def check_gui_running():
    """Check if the GUI is running by checking for the D-Bus service."""
    try:
        connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)

        # Try to call a method to see if the service exists
        result = connection.call_sync(
            'org.freedesktop.DBus',
            '/org/freedesktop/DBus',
            'org.freedesktop.DBus',
            'NameHasOwner',
            GLib.Variant('(s)', (GClickerDBusService.BUS_NAME,)),
            GLib.VariantType('(b)'),
            Gio.DBusCallFlags.NONE,
            -1,
            None
        )

        return result[0]
    except Exception:
        return False


def call_toggle():
    """Call the Toggle method on the D-Bus service."""
    try:
        connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)

        result = connection.call_sync(
            GClickerDBusService.BUS_NAME,
            GClickerDBusService.OBJECT_PATH,
            'org.gclicker.Control',
            'Toggle',
            None,
            GLib.VariantType('(b)'),
            Gio.DBusCallFlags.NONE,
            -1,
            None
        )

        return result[0]
    except Exception as e:
        print(f"Failed to call Toggle: {e}")
        return False


def get_state():
    """Get the current state from the D-Bus service."""
    try:
        connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)

        result = connection.call_sync(
            GClickerDBusService.BUS_NAME,
            GClickerDBusService.OBJECT_PATH,
            'org.gclicker.Control',
            'GetState',
            None,
            GLib.VariantType('(bd)'),
            Gio.DBusCallFlags.NONE,
            -1,
            None
        )

        return result[0], result[1]  # running, interval
    except Exception as e:
        print(f"Failed to get state: {e}")
        return False, 0.0
