import sys
import os
from threading import Thread
from time import sleep, time

import pygame
from PySide6.QtWidgets import QApplication

# Add necessary paths for module imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manager'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drone_capture'))

# Import required managers
from manager.tello_manager import TelloManager
from manager.controller_manager import JoystickManager
from manager.drone_ui_manager import DroneControlAppUIManager

"""
    Central controller for managing the Tello drone's operations and UI interaction.
"""
class DroneControlApp:
    def __init__(self, tello_manager):
        self.tello_manager = tello_manager 
        self.joystick_manager = JoystickManager()
        self.recording_active = False  # Track recording state
        self.previous_axes = [0.0] * self.joystick_manager.get_axis_count()  # Track previous axis states

    def run(self):
        # Initialize SDK and start state receiving thread if successful
        if self.tello_manager.init_sdk_mode():
            state_thread = Thread(target=self.tello_manager.receive_state)
            state_thread.start()

            # Start video stream and run the main loop if successful
            if self.tello_manager.start_video_stream():
                print("Video stream started")

                try:
                    # Main control loop
                    while True:
                        pygame.event.pump()  # Process pygame events
                        self.process_joystick_inputs()  # Handle joystick inputs
                        sleep(0.05)  # Reduced sleep for faster input processing
                        
                except KeyboardInterrupt:
                    print("Controller stopped")

                finally:
                    self.tello_manager.stop_drone_operations()  # Stop all drone operations
                    pygame.quit()  # Quit pygame
                    state_thread.join()  # Wait for state thread to finish

    def process_joystick_inputs(self):
        AXIS_THRESHOLD = 0.3  # Define threshold for axis input sensitivity

        # Get current button and axis states
        buttons = self.joystick_manager.get_buttons()
        axes = self.joystick_manager.get_axes()

        # Check if emergency key (P) is pressed on the keyboard
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            self.tello_manager.send_msg('emergency')
            print("Emergency command sent")
            sleep(1)

        # Button 1: Capture photo
        if buttons[0]:
            self.tello_manager.take_photo()
            sleep(2)

        # Button 2: Start/stop recording
        if buttons[1]:
            if not self.recording_active:
                self.tello_manager.start_recording()
                self.recording_active = True
                print('Recording started')
            else:
                self.tello_manager.stop_recording()
                self.recording_active = False
                print('Recording stopped')
            sleep(1)

        # Button 3: Pause recording
        if buttons[2] and self.recording_active:
            self.tello_manager.pause_recording()
            sleep(1)

        # Button 4: Resume recording
        if buttons[3] and self.recording_active:
            self.tello_manager.resume_recording()
            sleep(1)

        # Button 5: Move up
        if buttons[4]:
            self.tello_manager.send_msg("up 20")
        
        # Button 6: Move down
        if buttons[5]:
            self.tello_manager.send_msg("down 20")

        # Button 7 and 8 for Takeoff and Land
        if len(buttons) > 7:
            if buttons[6]:  # Takeoff
                self.tello_manager.send_msg('takeoff')
                print('Takeoff')
                sleep(1)
            elif buttons[7]:  # Land
                self.tello_manager.send_msg('land')
                print('Land')
                sleep(1)

        # Continuous axis control
        # Axis 1 (Left/Right)
        if abs(axes[0]) > AXIS_THRESHOLD:
            if axes[0] < -AXIS_THRESHOLD:
                self.tello_manager.send_msg("left 20")
                print("Moving left")
            elif axes[0] > AXIS_THRESHOLD:
                self.tello_manager.send_msg("right 20")
                print("Moving right")

        # Axis 2 (Forward/Backward)
        if abs(axes[1]) > AXIS_THRESHOLD:
            if axes[1] < -AXIS_THRESHOLD:
                self.tello_manager.send_msg("forward 20")
                print("Moving forward")
            elif axes[1] > AXIS_THRESHOLD:
                self.tello_manager.send_msg("back 20")
                print("Moving backward")

        # Axis 3 (Rotation: yaw)
        if abs(axes[2]) > AXIS_THRESHOLD:
            if axes[2] > AXIS_THRESHOLD:
                self.tello_manager.send_msg("cw 20")  # Clockwise rotation
                print("Rotating clockwise")
            elif axes[2] < -AXIS_THRESHOLD:
                self.tello_manager.send_msg("ccw 20")  # Counterclockwise rotation
                print("Rotating counterclockwise")

        # Flip commands
        if buttons[8]:  
            self.tello_manager.send_msg("flip l")
        if buttons[9]:  
            self.tello_manager.send_msg("flip r")
        if buttons[10]:  
            self.tello_manager.send_msg("flip f")
        if buttons[11]:  
            self.tello_manager.send_msg("flip b")


if __name__ == "__main__":
    # Initialize the Tello manager
    tello_manager = TelloManager()

    # Initialize the QApplication and UI manager
    app = QApplication(sys.argv)
    app_ui = DroneControlAppUIManager(tello_manager)
    app_ui.show()

    # Initialize the main controller
    controller = DroneControlApp(tello_manager)
    controller_thread = Thread(target=controller.run, daemon=True)
    controller_thread.start()

    # Execute the Qt application
    sys.exit(app.exec())
