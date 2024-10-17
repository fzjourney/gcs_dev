import sys
import os
from threading import Thread
from time import sleep

import pygame
from PySide6.QtWidgets import QApplication

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manager'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drone_capture'))

from tello_manager import TelloManager
from controller_manager import JoystickManager
from drone_ui_manager import DroneControlAppUIManager

class DroneControlApp:
    def __init__(self, tello_manager):
        self.tello_manager = tello_manager 
        self.joystick_manager = JoystickManager()
        self.recording_active = False

    def run(self):
        if self.tello_manager.init_sdk_mode():
            state_thread = Thread(target=self.tello_manager.receive_state)
            state_thread.start()

            if self.tello_manager.start_video_stream():
                print("Video stream started")

                try:
                    while True:
                        pygame.event.pump()

                        self.tello_manager.send_msg('command')

                        buttons = self.joystick_manager.get_buttons()
                        axes = self.joystick_manager.get_axes()

                        # Button 1 Capture photo
                        if buttons[0]:
                            self.tello_manager.take_photo()
                            sleep(2)

                        # Button 2 Start/stop recording
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

                        # Button 3 Pause recording
                        if buttons[2] and self.recording_active:
                            self.tello_manager.pause_recording()
                            sleep(1)

                        # Button 4 - Resume recording
                        if buttons[3] and self.recording_active:
                            self.tello_manager.resume_recording()
                            sleep(1)

                        sleep(0.1)

                        if len(buttons) > 7:
                            # Button 7 for takeoff
                            if buttons[6]:
                                self.tello_manager.send_msg('takeoff')
                                print('Takeoff')
                                sleep(1)

                            # Button 8 for land
                            elif buttons[7]:
                                self.tello_manager.send_msg('land')
                                print('Land')
                                sleep(1)

                        sleep(0.1)

                except KeyboardInterrupt:
                    print("Controller stopped")

                finally:
                    self.tello_manager.stop_drone_operations()
                    pygame.quit()
                    state_thread.join()


if __name__ == "__main__":
    tello_manager = TelloManager()  

    app = QApplication(sys.argv)
    app_ui = DroneControlAppUIManager(tello_manager) 
    app_ui.show()

    controller = DroneControlApp(tello_manager)

    controller_thread = Thread(target=controller.run, daemon=True)
    controller_thread.start()

    sys.exit(app.exec())
