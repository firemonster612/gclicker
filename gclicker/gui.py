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

        # Initial interval is set via on_interval_changed after spinboxes are created
        self.clicker = WaylandPortalClicker(interval=0.1)

        # Window setup
        self.set_default_size(450, 200)
        self.set_title("GClicker")

        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_margin_top(40)
        main_box.set_margin_bottom(40)
        main_box.set_margin_start(40)
        main_box.set_margin_end(40)
        main_box.set_valign(Gtk.Align.CENTER)
        main_box.set_halign(Gtk.Align.CENTER)

        # Time interval boxes
        time_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        time_box.set_halign(Gtk.Align.CENTER)

        # Minutes
        min_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        min_label = Gtk.Label(label="Minutes")
        min_label.add_css_class("caption")
        min_box.append(min_label)

        min_adj = Gtk.Adjustment(value=0, lower=0, upper=59, step_increment=1, page_increment=5)
        self.minutes_spin = Gtk.SpinButton()
        self.minutes_spin.set_adjustment(min_adj)
        self.minutes_spin.set_digits(0)
        self.minutes_spin.set_width_chars(5)
        self.minutes_spin.connect("value-changed", self.on_interval_changed)
        min_box.append(self.minutes_spin)
        time_box.append(min_box)

        # Seconds
        sec_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        sec_label = Gtk.Label(label="Seconds")
        sec_label.add_css_class("caption")
        sec_box.append(sec_label)

        sec_adj = Gtk.Adjustment(value=0, lower=0, upper=59, step_increment=1, page_increment=5)
        self.seconds_spin = Gtk.SpinButton()
        self.seconds_spin.set_adjustment(sec_adj)
        self.seconds_spin.set_digits(0)
        self.seconds_spin.set_width_chars(5)
        self.seconds_spin.connect("value-changed", self.on_interval_changed)
        sec_box.append(self.seconds_spin)
        time_box.append(sec_box)

        # Milliseconds
        ms_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        ms_label = Gtk.Label(label="Milliseconds")
        ms_label.add_css_class("caption")
        ms_box.append(ms_label)

        ms_adj = Gtk.Adjustment(value=100, lower=0, upper=999, step_increment=10, page_increment=100)
        self.milliseconds_spin = Gtk.SpinButton()
        self.milliseconds_spin.set_adjustment(ms_adj)
        self.milliseconds_spin.set_digits(0)
        self.milliseconds_spin.set_width_chars(5)
        self.milliseconds_spin.connect("value-changed", self.on_interval_changed)
        ms_box.append(self.milliseconds_spin)
        time_box.append(ms_box)

        main_box.append(time_box)

        # Control buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_homogeneous(True)

        self.start_button = Gtk.Button(label="Start")
        self.start_button.add_css_class("suggested-action")
        self.start_button.add_css_class("pill")
        self.start_button.set_size_request(120, 50)
        self.start_button.connect("clicked", self.on_start_clicked)
        button_box.append(self.start_button)

        self.stop_button = Gtk.Button(label="Stop")
        self.stop_button.add_css_class("destructive-action")
        self.stop_button.add_css_class("pill")
        self.stop_button.set_size_request(120, 50)
        self.stop_button.set_sensitive(False)
        self.stop_button.connect("clicked", self.on_stop_clicked)
        button_box.append(self.stop_button)

        main_box.append(button_box)

        self.set_child(main_box)

    def on_interval_changed(self, spin_button):
        """Handle interval change."""
        minutes = self.minutes_spin.get_value()
        seconds = self.seconds_spin.get_value()
        milliseconds = self.milliseconds_spin.get_value()

        # Calculate total interval in seconds
        total_interval = (minutes * 60) + seconds + (milliseconds / 1000.0)

        # Ensure minimum interval
        if total_interval < 0.001:
            total_interval = 0.001

        self.clicker.set_interval(total_interval)

    def on_start_clicked(self, button):
        """Handle start button click."""
        # Disable button while setting up
        self.start_button.set_sensitive(False)

        # Start in a thread to avoid blocking UI
        def start_thread():
            success = self.clicker.start()

            # Update UI in main thread
            def update_ui():
                if success:
                    self.stop_button.set_sensitive(True)
                    self.minutes_spin.set_sensitive(False)
                    self.seconds_spin.set_sensitive(False)
                    self.milliseconds_spin.set_sensitive(False)
                else:
                    self.start_button.set_sensitive(True)
                return False

            GLib.idle_add(update_ui)

        threading.Thread(target=start_thread, daemon=True).start()

    def on_stop_clicked(self, button):
        """Handle stop button click."""
        self.clicker.stop()
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        self.minutes_spin.set_sensitive(True)
        self.seconds_spin.set_sensitive(True)
        self.milliseconds_spin.set_sensitive(True)


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
