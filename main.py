import sys
import os
from threading import Thread
import pygame

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manager'))

from tello_manager import TelloManager
from controller_manager import JoystickManager
from display_manager import DisplayManager

class DroneControlApp:
    AXIS_TAKEOFF_LAND = 3  # Axis 3 controls takeoff/land
    BUTTON_PHOTO = 0        # Button 1: Capture photo
    BUTTON_VIDEO = 1        # Button 2: Start/stop video recording
    BUTTON_Z_AXIS_UP = 2    # Button 3: Z axis +
    BUTTON_Z_AXIS_DOWN = 3  # Button 4: Z axis -
    BUTTON_TOGGLE_PHOTO_VIDEO = 4  # Button 5: Photo/video toggle
    BUTTON_AUTO_FOCUS = 5   # Button 6: Auto focus

    def __init__(self):
        self.tello_manager = TelloManager()
        self.joystick_manager = JoystickManager()
        self.display_manager = DisplayManager()
        self.is_recording = False  # Track if video is recording
        self.is_photo_mode = True  # Track if in photo mode

    def send_axis_commands(self, axes_values):
        axis_threshold = 0.2
        max_speed = 100
        x_axis = int(axes_values[0] * max_speed)
        y_axis = int(axes_values[1] * max_speed)
        diagonal_axis = int(axes_values[2] * max_speed)

        # Horizontal and vertical movement
        if abs(x_axis) > axis_threshold * max_speed:
            direction = 'right' if x_axis > 0 else 'left'
            self.tello_manager.send_msg(f'{direction} {abs(x_axis)}')

        if abs(y_axis) > axis_threshold * max_speed:
            direction = 'back' if y_axis > 0 else 'forward'
            self.tello_manager.send_msg(f'{direction} {abs(y_axis)}')

        if abs(diagonal_axis) > axis_threshold * max_speed:
            direction = 'cw' if diagonal_axis > 0 else 'ccw'
            self.tello_manager.send_msg(f'{direction} {abs(diagonal_axis)}')

    def control_drone(self):
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

                buttons = self.joystick_manager.get_buttons()
                axes = self.joystick_manager.get_axes()

                self.display_manager.clear_screen()
                self.display_manager.draw_axes(axes)

                # Axis-based takeoff/land
                if axes[self.AXIS_TAKEOFF_LAND] == -1:
                    self.tello_manager.send_msg('takeoff')
                    print('Taking off...')
                elif axes[self.AXIS_TAKEOFF_LAND] == 1:
                    self.tello_manager.send_msg('land')
                    print('Landing...')

                # Button-based controls
                if buttons[self.BUTTON_PHOTO]:
                    if self.is_photo_mode:
                        self.tello_manager.send_msg('photo')
                        print("Photo captured.")
                    else:
                        print("Not in photo mode, cannot capture photo.")

                if buttons[self.BUTTON_VIDEO]:
                    if not self.is_photo_mode:
                        if self.is_recording:
                            self.tello_manager.send_msg('stop video')
                            print("Video recording stopped.")
                            self.is_recording = False
                        else:
                            self.tello_manager.send_msg('start video')
                            print("Video recording started.")
                            self.is_recording = True
                    else:
                        print("Not in video mode, cannot start/stop video.")

                if buttons[self.BUTTON_Z_AXIS_UP]:
                    self.tello_manager.send_msg('up 20')  # Example altitude control
                    print("Moving up.")

                if buttons[self.BUTTON_Z_AXIS_DOWN]:
                    self.tello_manager.send_msg('down 20')  # Example altitude control
                    print("Moving down.")

                if buttons[self.BUTTON_TOGGLE_PHOTO_VIDEO]:
                    self.is_photo_mode = not self.is_photo_mode
                    mode = "Photo" if self.is_photo_mode else "Video"
                    print(f"Mode switched to {mode}.")

                if buttons[self.BUTTON_AUTO_FOCUS]:
                    self.tello_manager.send_msg('auto focus')
                    print("Auto focus triggered.")

                self.send_axis_commands(axes)

                self.display_manager.update_display()
                pygame.time.wait(50)

        except KeyboardInterrupt:
            print("Exiting...")

        finally:
            self.tello_manager.stop_drone_operations()
            pygame.quit()
            state_thread.join()
            video_thread.join()

    def run(self):
        self.control_drone()

if __name__ == "__main__":
    app = DroneControlApp()
    app.run()
