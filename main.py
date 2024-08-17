import sys
import os
from threading import Thread
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

    COMMAND_COOLDOWN = 0.2  # Command cooldown in seconds

    def __init__(self):
        self.tello_manager = TelloManager()
        self.joystick_manager = JoystickManager()
        self.display_manager = DisplayManager()
        self.last_command_time = 0

    def send_axis_commands(self, axes_values):
        axis_threshold = 0.2
        max_speed = 100 
        x_axis = int(axes_values[0] * max_speed)
        y_axis = int(axes_values[1] * max_speed)
        diagonal_axis = int(axes_values[2] * max_speed)
        zoom_axis = int(axes_values[3] * max_speed)

        commands = []
        if abs(x_axis) > axis_threshold * max_speed:
            direction = 'right' if x_axis > 0 else 'left'
            commands.append(f'{direction} {abs(x_axis)}')

        if abs(y_axis) > axis_threshold * max_speed:
            direction = 'back' if y_axis > 0 else 'forward'
            commands.append(f'{direction} {abs(y_axis)}')

        if abs(diagonal_axis) > axis_threshold * max_speed:
            direction = 'cw' if diagonal_axis > 0 else 'ccw'
            commands.append(f'{direction} {abs(diagonal_axis)}')

        if abs(zoom_axis) > axis_threshold * max_speed:
            direction = 'up' if zoom_axis > 0 else 'down'
            commands.append(f'{direction} {abs(zoom_axis)}')

        current_time = pygame.time.get_ticks()
        if current_time - self.last_command_time > self.COMMAND_COOLDOWN * 1000:
            for command in commands:
                Thread(target=self.tello_manager.send_msg, args=(command,)).start()
                print(f'Sending command: {command}')
            self.last_command_time = current_time

    def control_drone(self):
        if self.tello_manager.init_sdk_mode():
            state_thread = Thread(target=self.tello_manager.receive_state)
            state_thread.start()

            if self.tello_manager.start_video_stream():
                print("Video stream started. Ready to accept commands.")

                try:
                    while True:
                        pygame.event.pump()

                        buttons = self.joystick_manager.get_buttons()
                        axes = self.joystick_manager.get_axes()

                        self.display_manager.clear_screen()
                        self.display_manager.draw_axes(axes)

                        for i in range(self.joystick_manager.get_axis_count()):
                            axis_value = axes[i]
                            self.display_manager.draw_text(
                                f"{self.AXIS_NAMES.get(i, f'Axis {i}')} value: {axis_value:.2f}",
                                (20, 20 + i * 30)
                            )

                        if buttons[self.BUTTON_TAKEOFF]:  # Button 6 for takeoff
                            self.tello_manager.send_msg('takeoff')
                            print('Taking off...')
                            pygame.time.wait(2000)  # Wait 2 seconds before the next command
                        elif buttons[self.BUTTON_LANDING]:  # Button 7 for landing
                            self.tello_manager.send_msg('land')
                            print('Landing...')
                            pygame.time.wait(2000)  # Wait 2 seconds before the next command

                        # Send axis commands to the drone
                        self.send_axis_commands(axes)

                        self.display_manager.update_display()
                        pygame.time.wait(100)  # Wait 0.1 second before the next loop

                except KeyboardInterrupt:
                    print("Exiting...")

                finally:
                    self.tello_manager.stop_drone_operations()
                    pygame.quit()
                    state_thread.join()

    def run(self):
        self.control_drone()

if __name__ == "__main__":
    app = DroneControlApp()
    app.run()
