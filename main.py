import sys
import os
from threading import Thread
from time import sleep
import pygame

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manager'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drone_capture'))

from tello_manager import TelloManager
from controller_manager import JoystickManager
from display_manager import DisplayManager

class DroneControlApp:
    def __init__(self):
        self.tello_manager = TelloManager()
        self.joystick_manager = JoystickManager()
        self.display_manager = DisplayManager()

    def run(self):
        if self.tello_manager.init_sdk_mode(): 
            state_thread = Thread(target=self.tello_manager.receive_state)
            state_thread.start()

            if self.tello_manager.start_video_stream(): 
                print("1")

                try:
                    while True:
                        pygame.event.pump()

                        self.tello_manager.send_msg('command')

                        buttons = self.joystick_manager.get_buttons()
                        axes = self.joystick_manager.get_axes()
                        self.display_manager.clear_screen()
                        self.display_manager.draw_axes(axes)

                        for i, button in enumerate(buttons):
                            button_label = f"Button {i+1}: {'1' if button else '0'}"
                            self.display_manager.draw_text(button_label, (10, 30 + i * 20))  
                        
                        for i, axis_value in enumerate(axes):    
                            axis_label = f"Axis {i+1}: {axis_value:.2f}"
                            self.display_manager.draw_text(axis_label, (10, 300 + i * 20))
                        
                        self.display_manager.update_display()

                        if buttons[0]:  # Button 1 Capture photo 
                            self.tello_manager.take_photo()
                            sleep(2)
                        
                        if len(buttons) > 7:
                            if buttons[6]:  # Button 6 for takeoff
                                self.tello_manager.send_msg('takeoff')
                                print('Takeoff')
                                sleep(2)
                                
                            elif buttons[7]:  # Button 7 for land
                                self.tello_manager.send_msg('land')
                                print('Land')
                                sleep(2)

                        sleep(0.1)

                except KeyboardInterrupt:
                    print("0")

                finally:
                    self.tello_manager.stop_drone_operations()
                    pygame.quit()
                    state_thread.join()

if __name__ == "__main__":
    app = DroneControlApp()
    app.run()
