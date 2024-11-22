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
    def __init__(self, MetricsSystem):
        self.MetricsSystem = MetricsSystem 
        self.Controller = Controller()
        self.recording_active = False  
        self.previous_axes = [0.0] * self.Controller.get_axis_count() 

    def run(self):
        if self.MetricsSystem.init_sdk_mode():
            state_thread = Thread(target=self.MetricsSystem.receive_state)
            state_thread.start()

            if self.MetricsSystem.start_video_stream():
                print("Video stream started")

                try:
                    while True:
                        pygame.event.pump() 
                        self.process_joystick_inputs() 
                        sleep(0.05)  
                        
                except KeyboardInterrupt:
                    print("Controller stopped")

                finally:
                    self.MetricsSystem.stop_drone_operations() 
                    pygame.quit() 
                    state_thread.join()  

    def process_joystick_inputs(self):
        AXIS_THRESHOLD = 0.3  

        buttons = self.Controller.get_buttons()
        axes = self.Controller.get_axes()

        # Button 1: Capture photo
        if buttons[0]:
            self.MetricsSystem.take_photo()
            sleep(2)

        # Button 2: Start/stop recording
        if buttons[1]:
            if not self.recording_active:
                self.MetricsSystem.start_recording()
                self.recording_active = True
                print('Recording started')
            else:
                self.MetricsSystem.stop_recording()
                self.recording_active = False
                print('Recording stopped')
            sleep(1)

        # Button 3: Pause recording
        if buttons[2] and self.recording_active:
            self.MetricsSystem.pause_recording()
            sleep(1)

        # Button 4: Resume recording
        if buttons[3] and self.recording_active:
            self.MetricsSystem.resume_recording()
            sleep(1)

        # Button 5: Move up
        if buttons[4]:
            self.MetricsSystem.send_msg("up 20")
        
        # Button 6: Move down
        if buttons[5]:
            self.MetricsSystem.send_msg("down 20")

        # Button 7 for Takeoff
        if len(buttons) > 7:
            if buttons[6]:
                self.MetricsSystem.send_msg('takeoff')
                print('Takeoff')
                sleep(1)
        # Button 8 for Land
            elif buttons[7]:
                self.MetricsSystem.send_msg('land')
                print('Land')
                sleep(1)

        # Axis 1 (Left/Right)
        if abs(axes[0]) > AXIS_THRESHOLD:
            if axes[0] < -AXIS_THRESHOLD:
                self.MetricsSystem.send_msg("left 20")
                print("Moving left")
            elif axes[0] > AXIS_THRESHOLD:
                self.MetricsSystem.send_msg("right 20")
                print("Moving right")

        # Axis 2 (Forward/Backward)
        if abs(axes[1]) > AXIS_THRESHOLD:
            if axes[1] < -AXIS_THRESHOLD:
                self.MetricsSystem.send_msg("forward 20")
                print("Moving forward")
            elif axes[1] > AXIS_THRESHOLD:
                self.MetricsSystem.send_msg("back 20")
                print("Moving backward")

        # Axis 3 (Rotation: yaw)
        if abs(axes[2]) > AXIS_THRESHOLD:
            if axes[2] > AXIS_THRESHOLD:
                self.MetricsSystem.send_msg("cw 20")  
                print("Rotating clockwise")
            elif axes[2] < -AXIS_THRESHOLD:
                self.MetricsSystem.send_msg("ccw 20")  
                print("Rotating counterclockwise")

        if buttons[8]:  
            self.MetricsSystem.send_msg("flip l")
        if buttons[9]:  
            self.MetricsSystem.send_msg("flip r")
        if buttons[10]:  
            self.MetricsSystem.send_msg("flip f")
        if buttons[11]:  
            self.MetricsSystem.send_msg("flip b")


if __name__ == "__main__":
    MetricsSystem = MetricsSystem()

    app = QApplication(sys.argv)
    app_ui = DroneControlAppUIManager(MetricsSystem)
    app_ui.show()

    Controller = DroneControlApp(MetricsSystem)
    Controller_thread = Thread(target=Controller.run, daemon=True)
    Controller_thread.start()

    sys.exit(app.exec())
    