import sys
import os
from threading import Thread
import pygame
import tkinter as tk
from tkinter import ttk

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manager'))

from tello_manager import TelloManager
from controller_manager import JoystickManager
from display_manager import DisplayManager

# Tkinter GUI Manager Class
class DroneGuiManager:
    def __init__(self, drone_control_app):
        self.app = drone_control_app
        self.is_photo_mode = True

        self.root = tk.Tk()
        self.root.title("Drone Control Panel")

        # Takeoff and Land buttons
        self.takeoff_button = ttk.Button(self.root, text="Takeoff", command=self.takeoff)
        self.takeoff_button.grid(row=0, column=0, padx=10, pady=10)

        self.land_button = ttk.Button(self.root, text="Land", command=self.land)
        self.land_button.grid(row=0, column=1, padx=10, pady=10)

        # Mode Label
        self.mode_label = tk.Label(self.root, text="Mode: Video")
        self.mode_label.grid(row=1, column=0, columnspan=2, pady=10)

        # Example Sliders (could add more based on your needs)
        self.create_slider("Focal Length:", 50, 0, 100, 2)
        self.create_slider("Tint:", 1.0, 0.0, 2.0, 3)
        self.create_slider("Temperature (K):", 1901, 1000, 10000, 4)

        # Drone Status Display (mocked data for now)
        self.create_status_display()

    def create_slider(self, text, initial_value, min_value, max_value, row):
        label = tk.Label(self.root, text=text)
        label.grid(row=row, column=0, padx=10, pady=5)

        slider = tk.Scale(self.root, from_=min_value, to=max_value, orient="horizontal", resolution=0.01)
        slider.set(initial_value)
        slider.grid(row=row, column=1, padx=10, pady=5)

    def create_status_display(self):
        status_frame = tk.Frame(self.root)
        status_frame.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

        # Mocked data - could be updated with actual drone telemetry
        self.create_status_label(status_frame, "Battery:", "90%", 0)
        self.create_status_label(status_frame, "Temperature:", "30°", 1)
        self.create_status_label(status_frame, "Signal Strength:", "Good", 2)

    def create_status_label(self, frame, text, value, row):
        label = tk.Label(frame, text=text)
        label.grid(row=row, column=0, padx=5, pady=2)

        value_label = tk.Label(frame, text=value)
        value_label.grid(row=row, column=1, padx=5, pady=2)

    def takeoff(self):
        self.app.tello_manager.send_msg("takeoff")
        print("Drone taking off")

    def land(self):
        self.app.tello_manager.send_msg("land")
        print("Drone landing")

    def run(self):
        self.root.mainloop()


class DroneControlApp:
    AXIS_TAKEOFF_LAND = 3
    BUTTON_PHOTO = 0
    BUTTON_VIDEO = 1
    BUTTON_Z_AXIS_UP = 2
    BUTTON_Z_AXIS_DOWN = 3
    BUTTON_TOGGLE_PHOTO_VIDEO = 4

    def __init__(self):
        self.tello_manager = TelloManager()
        self.display_manager = DisplayManager()
        self.controller_manager = JoystickManager()
        self.is_recording = False
        self.is_photo_mode = True

        # Initialize GUI
        self.gui = DroneGuiManager(self)

    def handle_buttons(self, buttons):
        """Handle button-based actions."""
        if buttons[6]:  # Button 7 (index 6)
            self.gui.takeoff()
        
        if buttons[7]:  # Button 8 (index 7)
            self.gui.land()

        if buttons[self.BUTTON_PHOTO]:
            if self.gui.is_photo_mode:
                self.tello_manager.send_msg("photo")
                print("Photo captured.")
            else:
                print("Not in photo mode, cannot capture photo.")

        if buttons[self.BUTTON_VIDEO]:
            if not self.gui.is_photo_mode:
                if self.is_recording:
                    self.tello_manager.send_msg("stop video")
                    print("Video recording stopped.")
                    self.is_recording = False
                else:
                    self.tello_manager.send_msg("start video")
                    print("Video recording started.")
                    self.is_recording = True

    def control_drone(self):
        """Main control loop for drone actions."""
        self.tello_manager.init_sdk_mode()

        state_thread = Thread(target=self.tello_manager.receive_state)
        state_thread.start()

        self.tello_manager.start_video_stream()
        print("Video stream started. Ready to accept commands.")
        video_thread = Thread(target=self.tello_manager.video_stream)
        video_thread.start()

        try:
            while True:
                pygame.event.pump()
                buttons = self.controller_manager.get_buttons()
                axes = self.controller_manager.get_axes()

                if axes[self.AXIS_TAKEOFF_LAND] == -1:
                    self.gui.takeoff()
                elif axes[self.AXIS_TAKEOFF_LAND] == 1:
                    self.gui.land()

                self.handle_buttons(buttons)

                pygame.time.wait(50)

        except KeyboardInterrupt:
            print("Exiting...")

        finally:
            self.tello_manager.stop_drone_operations()
            pygame.quit()
            state_thread.join()
            video_thread.join()

    def run(self):
        """Run the main drone control application and GUI."""
        control_thread = Thread(target=self.control_drone)
        control_thread.start()

        # Run the GUI in the main thread
        self.gui.run()


if __name__ == "__main__":
    app = DroneControlApp()
    app.run()
