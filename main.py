import sys
import os
from threading import Thread
import tkinter as tk
from tkinter import ttk

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manager'))

from tello_manager import TelloManager
from display_manager import DisplayManager

class DroneGuiManager:
    def __init__(self, drone_control_app):
        self.app = drone_control_app
        self.root = tk.Tk()
        self.root.title("Drone Control Panel")

        self.takeoff_button = ttk.Button(self.root, text="Takeoff", command=self.takeoff)
        self.takeoff_button.grid(row=0, column=0, padx=10, pady=10)

        self.land_button = ttk.Button(self.root, text="Land", command=self.land)
        self.land_button.grid(row=1, column=1, padx=10, pady=10)

        self.mode_label = tk.Label(self.root, text="Mode: Video")
        self.mode_label.grid(row=1, column=0, columnspan=2, pady=10)

        self.create_slider("Focal Length:", 50, 0, 100, 2)
        self.create_slider("Tint:", 1.0, 0.0, 2.0, 3)
        self.create_slider("Temperature (K):", 1901, 1000, 10000, 4)

        self.create_status_display()

    def create_slider(self, text, initial_value, min_value, max_value, row):
        label = tk.Label(self.root, text=text)
        label.grid(row=row, column=0, padx=10, pady=5)

        slider = tk.Scale(self.root, from_=min_value, to=max_value, orient="horizontal", resolution=0.01)
        slider.set(initial_value)
        slider.grid(row=row, column=1, padx=10, pady=5)

    def create_status_display(self):
        """Creates the telemetry display in the GUI."""
        status_frame = tk.Frame(self.root)
        status_frame.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

        self.battery_label = self.create_status_label(status_frame, "Battery:", "Unknown", 0)
        self.temperature_label = self.create_status_label(status_frame, "Temperature:", "Unknown", 1)
        self.speed_label = self.create_status_label(status_frame, "Speed:", "Unknown", 2)
        self.altitude_label = self.create_status_label(status_frame, "Altitude:", "Unknown", 3)

        # Start telemetry update loop
        self.update_telemetry()

    def create_status_label(self, frame, text, value, row):
        label = tk.Label(frame, text=text)
        label.grid(row=row, column=0, padx=5, pady=2)

        value_label = tk.Label(frame, text=value)
        value_label.grid(row=row, column=1, padx=5, pady=2)
        return value_label

    def update_telemetry(self):
        """Periodically updates telemetry data from the drone and updates the GUI."""
        telemetry_data = self.app.tello_manager.state
        print(f"Telemetry datassss: {telemetry_data}")  # Debug print

        if telemetry_data:
            battery = telemetry_data.get('battery', 'Unknown')
            temperature = telemetry_data.get('temperature', 'Unknown')
            speed = telemetry_data.get('speed', 'Unknown')
            altitude = telemetry_data.get('altitude', 'Unknown')

            # Update the labels with new telemetry data
            self.battery_label.config(text=str(battery))
            self.temperature_label.config(text=str(temperature))
            self.speed_label.config(text=str(speed))
            self.altitude_label.config(text=str(altitude))

        # Schedule the next update
        self.root.after(1000, self.update_telemetry)



    def takeoff(self):
        self.app.tello_manager.send_msg("takeoff")
        print("Drone taking off")

    def land(self):
        self.app.tello_manager.send_msg("land")
        print("Drone landing")

    def run(self):
        self.root.mainloop()

class DroneControlApp:
    def __init__(self):
        self.tello_manager = TelloManager()
        self.display_manager = DisplayManager()
        # Removed joystick manager initialization
        self.is_recording = False
        self.is_photo_mode = True
        self.gui = DroneGuiManager(self)

    def control_drone(self):
        """Main control loop for drone actions."""    
        self.tello_manager.init_sdk_mode()

        state_thread = Thread(target=self.tello_manager.receive_state, daemon=True)
        state_thread.start()

        self.tello_manager.start_video_stream()
        print("Video stream started. Ready to accept commands.")
        video_thread = Thread(target=self.tello_manager.video_stream, daemon=True)
        video_thread.start()

        try:
            while True:
                # Main loop can stay empty as telemetry and control are managed by threads
                pass

        except KeyboardInterrupt:
            print("Exiting...")

        finally:
            self.tello_manager.stop_drone_operations()
            video_thread.join()

    def run(self):
        """Run the main drone control application and GUI."""        
        control_thread = Thread(target=self.control_drone, daemon=True)
        control_thread.start()

        self.gui.run()

if __name__ == "__main__":
    app = DroneControlApp()
    app.run()
