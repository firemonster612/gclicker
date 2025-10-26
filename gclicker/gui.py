"""GTK4 GUI for GClicker."""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import threading

from gclicker.wayland_clicker import WaylandPortalClicker


class GClickerWindow(Gtk.ApplicationWindow):
    """Main application window."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.clicker = WaylandPortalClicker(interval=0.1)

        # Window setup
        self.set_default_size(400, 300)
        self.set_title("GClicker")

        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_valign(Gtk.Align.CENTER)

        # Title
        title = Gtk.Label(label="GClicker")
        title.add_css_class("title-1")
        main_box.append(title)

        # Status label
        self.status_label = Gtk.Label(label="Idle")
        self.status_label.add_css_class("title-4")
        main_box.append(self.status_label)

        # Interval control group
        interval_group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        interval_label = Gtk.Label(label="Click Interval (seconds)")
        interval_label.add_css_class("heading")
        interval_group.append(interval_label)

        # Interval adjustment (0.001 to 10 seconds)
        interval_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        interval_box.set_halign(Gtk.Align.CENTER)

        adjustment = Gtk.Adjustment(
            value=0.1,
            lower=0.001,
            upper=10.0,
            step_increment=0.01,
            page_increment=0.1
        )
        self.interval_spin = Gtk.SpinButton()
        self.interval_spin.set_adjustment(adjustment)
        self.interval_spin.set_digits(3)
        self.interval_spin.set_value(0.1)
        self.interval_spin.connect("value-changed", self.on_interval_changed)

        interval_box.append(self.interval_spin)
        interval_group.append(interval_box)

        # Add some preset buttons
        preset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        preset_box.set_halign(Gtk.Align.CENTER)

        presets = [
            ("Fast (0.05s)", 0.05),
            ("Normal (0.1s)", 0.1),
            ("Slow (0.5s)", 0.5),
        ]

        for label, value in presets:
            btn = Gtk.Button(label=label)
            btn.connect("clicked", lambda b, v=value: self.interval_spin.set_value(v))
            preset_box.append(btn)

        interval_group.append(preset_box)
        main_box.append(interval_group)

        # Control buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_homogeneous(True)

        self.start_button = Gtk.Button(label="Start")
        self.start_button.add_css_class("suggested-action")
        self.start_button.connect("clicked", self.on_start_clicked)
        button_box.append(self.start_button)

        self.stop_button = Gtk.Button(label="Stop")
        self.stop_button.add_css_class("destructive-action")
        self.stop_button.set_sensitive(False)
        self.stop_button.connect("clicked", self.on_stop_clicked)
        button_box.append(self.stop_button)

        main_box.append(button_box)

        # Info label
        info_label = Gtk.Label(
            label="Uses Wayland RemoteDesktop portal.\nPermission dialog appears on first run only."
        )
        info_label.add_css_class("dim-label")
        info_label.set_wrap(True)
        info_label.set_justify(Gtk.Justification.CENTER)
        main_box.append(info_label)

        self.set_child(main_box)

    def on_interval_changed(self, spin_button):
        """Handle interval change."""
        interval = spin_button.get_value()
        self.clicker.set_interval(interval)

    def on_start_clicked(self, button):
        """Handle start button click."""
        # Disable button while setting up
        self.start_button.set_sensitive(False)
        self.status_label.set_label("Starting...")

        # Start in a thread to avoid blocking UI
        def start_thread():
            success = self.clicker.start()

            # Update UI in main thread
            def update_ui():
                if success:
                    self.stop_button.set_sensitive(True)
                    self.interval_spin.set_sensitive(False)
                    self.status_label.set_label("Clicking...")
                    self.status_label.add_css_class("success")
                else:
                    self.start_button.set_sensitive(True)
                    self.status_label.set_label("Failed to start (permission denied?)")
                return False

            GLib.idle_add(update_ui)

        threading.Thread(target=start_thread, daemon=True).start()

    def on_stop_clicked(self, button):
        """Handle stop button click."""
        self.clicker.stop()
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        self.interval_spin.set_sensitive(True)
        self.status_label.set_label("Idle")
        self.status_label.remove_css_class("success")


class GClickerApplication(Adw.Application):
    """Main application class."""

    def __init__(self):
        super().__init__(application_id='com.github.gclicker')
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        """Handle application activation."""
        self.win = GClickerWindow(application=app)
        self.win.present()


def main():
    """Main entry point for GUI."""
    app = GClickerApplication()
    return app.run(None)


if __name__ == '__main__':
    main()
