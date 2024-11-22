import sys
import os
import pygame

from threading import Thread
from time import sleep
from PySide6.QtWidgets import QApplication

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manager'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drone_capture'))

from manager.MetricsSystem import MetricsSystem
from manager.Controller import Controller
from drone_ui_manager import DroneControlAppUIManager

class DroneControlApp:
    def __init__(self, tello_manager):
        self.tello_manager = tello_manager 
        self.joystick_manager = Controller()
        self.recording_active = False  
        self.previous_axes = [0.0] * self.joystick_manager.get_axis_count() 

    def run(self):
        if self.tello_manager.init_sdk_mode():
            state_thread = Thread(target=self.tello_manager.receive_state)
            state_thread.start()

            if self.tello_manager.start_video_stream():
                print("Video stream started")

                try:
                    while True:
                        pygame.event.pump() 
                        self.process_joystick_inputs() 
                        sleep(0.05)  
                        
                except KeyboardInterrupt:
                    print("Controller stopped")

                finally:
                    self.tello_manager.stop_drone_operations() 
                    pygame.quit() 
                    state_thread.join()  

    def process_joystick_inputs(self):
        AXIS_THRESHOLD = 0.3  

        buttons = self.joystick_manager.get_buttons()
        axes = self.joystick_manager.get_axes()

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

        # Button 7 for Takeoff
        if len(buttons) > 7:
            if buttons[6]:
                self.tello_manager.send_msg('takeoff')
                print('Takeoff')
                sleep(1)
        # Button 8 for Land
            elif buttons[7]:
                self.tello_manager.send_msg('land')
                print('Land')
                sleep(1)

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
                self.tello_manager.send_msg("cw 20")  
                print("Rotating clockwise")
            elif axes[2] < -AXIS_THRESHOLD:
                self.tello_manager.send_msg("ccw 20")  
                print("Rotating counterclockwise")

        if buttons[8]:  
            self.tello_manager.send_msg("flip l")
        if buttons[9]:  
            self.tello_manager.send_msg("flip r")
        if buttons[10]:  
            self.tello_manager.send_msg("flip f")
        if buttons[11]:  
            self.tello_manager.send_msg("flip b")


if __name__ == "__main__":
    tello_manager = MetricsSystem()

    app = QApplication(sys.argv)
    app_ui = DroneControlAppUIManager(tello_manager)
    app_ui.show()

    controller = DroneControlApp(tello_manager)
    controller_thread = Thread(target=controller.run, daemon=True)
    controller_thread.start()

    sys.exit(app.exec())
    