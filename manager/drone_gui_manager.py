# drone_gui_manager.py

import tkinter as tk
from threading import Thread

class DroneGuiManager:
    def __init__(self, tello_manager):
        self.tello_manager = tello_manager
        self.window = tk.Tk()
        self.window.title("Drone Controller")
        self.battery_label = tk.Label(self.window, text="Battery: Unknown")
        self.battery_label.pack()

        # Initialize mode (photo/video)
        self.is_photo_mode = True
        self.mode_label = tk.Label(self.window, text="Mode: Photo")
        self.mode_label.pack()

    def update_battery(self):
        """Update battery status in the GUI."""
        while True:
            battery = self.tello_manager.get_battery()
            if battery:
                self.battery_label.config(text=f"Battery: {battery}%")
            self.window.update_idletasks()

    def toggle_mode(self):
        """Toggle between photo and video mode."""
        self.is_photo_mode = not self.is_photo_mode
        mode_text = "Photo" if self.is_photo_mode else "Video"
        self.mode_label.config(text=f"Mode: {mode_text}")

    def takeoff(self):
        """Handle takeoff."""
        self.tello_manager.send_msg("takeoff")

    def land(self):
        """Handle landing."""
        self.tello_manager.send_msg("land")

    def run(self):
        """Run the GUI."""
        battery_thread = Thread(target=self.update_battery)
        battery_thread.start()
        self.window.mainloop()
