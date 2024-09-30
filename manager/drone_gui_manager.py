import tkinter as tk
from tkinter import ttk
from threading import Thread
from tello_manager import TelloManager

class DroneGuiManager:
    def __init__(self, drone_control_app):
        self.app = drone_control_app
        self.tello_manager = self.app.tello_manager
        self.root = tk.Tk()
        self.root.title("Tello Drone Telemetry")

        # Create buttons for drone control
        self.takeoff_button = ttk.Button(self.root, text="Takeoff", command=self.takeoff)
        self.takeoff_button.grid(row=0, column=0, padx=10, pady=10)

        self.land_button = ttk.Button(self.root, text="Land", command=self.land)
        self.land_button.grid(row=0, column=1, padx=10, pady=10)

        # Telemetry display
        self.create_telemetry_display()

        # Start updating telemetry in a separate thread
        self.telemetry_thread = Thread(target=self.update_telemetry, daemon=True)
        self.telemetry_thread.start()

    def create_status_label(self, frame, text, row):
        """Helper function to create a label for displaying telemetry values."""
        label = tk.Label(frame, text=text)
        label.grid(row=row, column=0, padx=5, pady=2, sticky='e')
        value_label = tk.Label(frame, text="Unknown", width=10)
        value_label.grid(row=row, column=1, padx=5, pady=2, sticky='w')
        return value_label

    def create_telemetry_display(self):
        """Creates the telemetry display in the GUI."""
        telemetry_frame = tk.Frame(self.root)
        telemetry_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Telemetry labels
        self.battery_label = self.create_status_label(telemetry_frame, "Battery (%):", 0)
        self.temperature_label = self.create_status_label(telemetry_frame, "Temperature (°C):", 1)
        self.pitch_label = self.create_status_label(telemetry_frame, "Pitch (°):", 2)
        self.roll_label = self.create_status_label(telemetry_frame, "Roll (°):", 3)
        self.yaw_label = self.create_status_label(telemetry_frame, "Yaw (°):", 4)
        self.baro_label = self.create_status_label(telemetry_frame, "Barometer (cm):", 5)
        self.tof_label = self.create_status_label(telemetry_frame, "TOF (cm):", 6)
        self.height_label = self.create_status_label(telemetry_frame, "Height (cm):", 7)

    def update_telemetry(self):
        """Periodically updates telemetry data from the drone and updates the GUI."""
        telemetry_data = self.app.tello_manager.state
        print(f"Telemetry data: {telemetry_data}")  # Debug print

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
        self.tello_manager.send_msg("takeoff")
        print("Drone taking off")

    def land(self):
        self.tello_manager.send_msg("land")
        print("Drone landing")

    def run(self):
        self.root.mainloop()
