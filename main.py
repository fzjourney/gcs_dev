import sys
import os
from threading import Thread
from time import sleep
import pygame

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manager'))

from tello_manager import TelloManager
from controller_manager import JoystickManager

class DroneControlApp:
    def __init__(self):
        self.tello_manager = TelloManager()
        self.joystick_manager = JoystickManager()

    def run(self):
        if self.tello_manager.init_sdk_mode():  
            state_thread = Thread(target=self.tello_manager.receive_state)
            state_thread.start()

            if self.tello_manager.start_video_stream():  
                print("Video stream started. Ready to accept commands.")

                try:
                    while True:
                        pygame.event.pump()  

                        self.tello_manager.send_msg('command')  

                        # Fetch joystick buttons
                        buttons = self.joystick_manager.get_buttons()
                        print(f"Joystick buttons state: {buttons}")  

                        # Button 7 to take off, Button 8 to land
                        if len(buttons) > 7:
                            if buttons[6]: 
                                self.tello_manager.send_msg('takeoff')
                                print('Taking off...')
                                sleep(2)
                            elif buttons[7]:
                                self.tello_manager.send_msg('land')
                                print('Landing...')
                                sleep(2)
                        else:
                            print("Joystick button index out of range.")

                        sleep(0.1) 

                except KeyboardInterrupt:
                    print("Exiting...")

                finally:
                    self.tello_manager.stop_drone_operations()
                    pygame.quit()
                    state_thread.join()

if __name__ == "__main__":
    app = DroneControlApp()
    app.run()
