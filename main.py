import sys
import os
from threading import Thread
from time import sleep
import pygame

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manager'))

from tello_manager import TelloManager
from controller_manager import JoystickManager
from display_manager import DisplayManager

class DroneControlApp:
    BUTTON_TAKEOFF = 6
    BUTTON_LANDING = 7
    AXIS_NAMES = {
        0: "X Axis",          # -1 for left, 1 for right
        1: "Y Axis",          # -1 for forward, 1 for backward
        2: "Diagonal Axis",   # Rotation
        3: "Zoom Axis"        # Altitude control
    }

    def __init__(self):
        self.tello_manager = TelloManager()
        self.joystick_manager = JoystickManager()
        self.display_manager = DisplayManager()

    def send_axis_commands(self, axes_values):
        axis_threshold = 0.2
        move_distance = 50
        x_axis = axes_values[0]
        y_axis = axes_values[1]
        diagonal_axis = axes_values[2]
        zoom_axis = axes_values[3]

        if x_axis > axis_threshold:
            self.tello_manager.send_msg(f'right {move_distance}')
            print(f'Moving right by {move_distance} cm')
        elif x_axis < -axis_threshold:
            self.tello_manager.send_msg(f'left {move_distance}')
            print(f'Moving left by {move_distance} cm')

        if y_axis > axis_threshold:
            self.tello_manager.send_msg(f'back {move_distance}')
            print(f'Moving back by {move_distance} cm')
        elif y_axis < -axis_threshold:
            self.tello_manager.send_msg(f'forward {move_distance}')
            print(f'Moving forward by {move_distance} cm')

        if diagonal_axis > axis_threshold:
            self.tello_manager.send_msg(f'cw {move_distance}')  # Clockwise
            print(f'Rotating clockwise by {move_distance} degrees')
        elif diagonal_axis < -axis_threshold:
            self.tello_manager.send_msg(f'ccw {move_distance}')  # Counterclockwise
            print(f'Rotating counterclockwise by {move_distance} degrees')

        if zoom_axis > axis_threshold:
            self.tello_manager.send_msg(f'up {move_distance}')
            print(f'Ascending by {move_distance} cm')
        elif zoom_axis < -axis_threshold:
            self.tello_manager.send_msg(f'down {move_distance}')
            print(f'Descending by {move_distance} cm')

        # Throttle commands to avoid overwhelming the drone
        sleep(0.2)  # Adjust the sleep time as necessary

    def control_drone(self):
        # Main logic for controlling the drone
        if self.tello_manager.init_sdk_mode():
            state_thread = Thread(target=self.tello_manager.receive_state)
            state_thread.start()

            if self.tello_manager.start_video_stream():
                print("Video stream started. Ready to accept commands.")

                try:
                    while True:
                        pygame.event.pump()

                        # Get joystick buttons and axes
                        buttons = self.joystick_manager.get_buttons()
                        axes = self.joystick_manager.get_axes()

                        # Display axes and button states
                        self.display_manager.clear_screen()
                        self.display_manager.draw_axes(axes)

                        # Display axis names and values
                        for i in range(self.joystick_manager.get_axis_count()):
                            axis_value = axes[i]
                            self.display_manager.draw_text(
                                f"{self.AXIS_NAMES.get(i, f'Axis {i}')} value: {axis_value:.2f}",
                                (20, 20 + i * 30)
                            )

                        # Handle takeoff and landing using joystick buttons
                        if buttons[self.BUTTON_TAKEOFF]:  # Button 6 for takeoff
                            self.tello_manager.send_msg('takeoff')
                            print('Taking off...')
                            sleep(2)
                        elif buttons[self.BUTTON_LANDING]:  # Button 7 for landing
                            self.tello_manager.send_msg('land')
                            print('Landing...')
                            sleep(2)

                        # Send axis commands to the drone
                        self.send_axis_commands(axes)

                        self.display_manager.update_display()
                        sleep(0.1)

                except KeyboardInterrupt:
                    print("Exiting...")

                finally:
                    self.tello_manager.stop_drone_operations()
                    pygame.quit()
                    state_thread.join()

    def run(self):
        # Execute drone control logic
        self.control_drone()

if __name__ == "__main__":
    app = DroneControlApp()
    app.run()
