import sys
import os
from threading import Thread
from time import sleep
import pygame

# Add the 'manager' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manager'))

from tello_manager import TelloManager
from controller_manager import JoystickManager

class DroneControlApp:
    def __init__(self):
        # Initialize TelloManager and JoystickManager
        self.tello_manager = TelloManager()
        self.joystick_manager = JoystickManager()

    def run(self):
        if self.tello_manager.init_sdk_mode():  # Only proceed if SDK mode is successfully initiated
            # Start thread to receive telemetry data
            state_thread = Thread(target=self.tello_manager.receive_state)
            state_thread.start()

            if self.tello_manager.start_video_stream():  # Only proceed if video streaming mode is successfully initiated
                print("Video stream started. Ready to accept commands.")

                try:
                    while True:
                        pygame.event.pump()  # Process events to update joystick states

                        self.tello_manager.send_msg('command')  # Keep-alive command to avoid drone timeouts

                        # Fetch joystick buttons
                        buttons = self.joystick_manager.get_buttons()
                        print(f"Joystick buttons state: {buttons}")  # Debugging line to check button states

                        # Button 7 to take off, Button 8 to land
                        if len(buttons) > 8:
                            if buttons[7]:  # Button 7 for takeoff
                                self.tello_manager.send_msg('takeoff')
                                print('Taking off...')
                                # Wait for a while to ensure the command is processed
                                sleep(2)
                            elif buttons[8]:  # Button 8 for land
                                self.tello_manager.send_msg('land')
                                print('Landing...')
                                # Wait for a while to ensure the command is processed
                                sleep(2)
                        else:
                            print("Joystick button index out of range.")

                        sleep(0.1)  # Add delay to avoid overloading the main loop

                except KeyboardInterrupt:
                    print("Exiting...")

                finally:
                    # If the main loop is exited, stop all drone operations
                    self.tello_manager.stop_drone_operations()
                    pygame.quit()
                    state_thread.join()

if __name__ == "__main__":
    app = DroneControlApp()
    app.run()
