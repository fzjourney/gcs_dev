import pygame

from typing import List
from PySide6.QtGui import (
    QTextCursor,
)
from time import sleep

class Controller:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("No joystick found")
            raise SystemExit("No joystick found")

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        
        self.num_axes = self.joystick.get_numaxes()
        self.num_buttons = self.joystick.get_numbuttons()

        print(f"Joystick name: {self.joystick.get_name()}")

    def get_axes(self) -> List[float]:
        return [self.joystick.get_axis(i) for i in range(self.num_axes)]

    def get_buttons(self) -> List[bool]:

        pygame.event.pump()
        return [self.joystick.get_button(i) for i in range(self.num_buttons)]

    def get_axis_count(self) -> int:
        return self.num_axes

    def get_button_count(self) -> int:
        return self.num_buttons
    
    def update_joystick_display(self, joystick_display_widget):
        buttons = self.get_buttons()
        axes = self.get_axes()

        joystick_text = ""

        for i, button in enumerate(buttons):
            if button:  
                joystick_text += f"Button {i+1}: Pressed\n"

        axis_threshold = 0.1  
        for i, axis_value in enumerate(axes):
            if abs(axis_value) > axis_threshold:  
                joystick_text += f"Axis {i+1}: {axis_value:.2f}\n"

        joystick_display_widget.setText(joystick_text)
        joystick_display_widget.moveCursor(QTextCursor.End)
        
    def run_joystick_control(self, MetricsSystem, recording_active):
            AXIS_THRESHOLD = 0.3 
            recording_active = False 
            while True:
                pygame.event.pump() 
                buttons = self.get_buttons()
                axes = self.get_axes()

                # Button 1: Capture photo
                if buttons[0]:
                    MetricsSystem.take_photo()
                    sleep(2)

                # Button 2: Start/stop recording
                if buttons[1]:
                    if not recording_active:
                        MetricsSystem.start_recording()
                        recording_active = True
                        print('Recording started')
                    else:
                        MetricsSystem.stop_recording()
                        recording_active = False
                        print('Recording stopped')
                    sleep(1)

                # Button 3: Pause recording
                if buttons[2] and recording_active:
                    MetricsSystem.pause_recording()
                    sleep(1)

                # Button 4: Resume recording
                if buttons[3] and recording_active:
                    MetricsSystem.resume_recording()
                    sleep(1)

                # Button 5: Move up
                if buttons[4]:
                    MetricsSystem.send_msg("up 20")
                
                # Button 6: Move down
                if buttons[5]:
                    MetricsSystem.send_msg("down 20")

                # Button 7 for Takeoff
                if len(buttons) > 7:
                    if buttons[6]:
                        MetricsSystem.send_msg('takeoff')
                        print('Takeoff')
                        sleep(1)
                    # Button 8 for Land
                    elif buttons[7]:
                        MetricsSystem.send_msg('land')
                        print('Land')
                        sleep(1)

                # Forward/Backward (no threshold)
                if abs(axes[1]) <= 1:  
                    speed = int(10 + (abs(axes[1]) * 90)) 
                    if axes[1] < 0:  # Moving forward
                        MetricsSystem.send_msg(f"forward {speed}")
                        print(f"Moving forward at speed {speed}")
                    elif axes[1] > 0:  # Moving backward
                        MetricsSystem.send_msg(f"back {speed}")
                        print(f"Moving backward at speed {speed}")

                # Left/Right (no threshold)
                if abs(axes[0]) <= 1:  
                    speed = int(10 + (abs(axes[0]) * 90)) 
                    if axes[0] < 0:  # Moving left
                        MetricsSystem.send_msg(f"left {speed}")
                        print(f"Moving left at speed {speed}")
                    elif axes[0] > 0:  # Moving right
                        MetricsSystem.send_msg(f"right {speed}")
                        print(f"Moving right at speed {speed}")


                # Axis 3 (Rotation: yaw)
                if abs(axes[2]) > AXIS_THRESHOLD:
                    if axes[2] > AXIS_THRESHOLD:
                        MetricsSystem.send_msg("cw 20")  
                        print("Rotating clockwise")
                    elif axes[2] < -AXIS_THRESHOLD:
                        MetricsSystem.send_msg("ccw 20")  
                        print("Rotating counterclockwise")

                if buttons[8]:  
                    MetricsSystem.send_msg("flip l")
                if buttons[9]:  
                    MetricsSystem.send_msg("flip r")
                if buttons[10]:  
                    MetricsSystem.send_msg("flip f")
                if buttons[11]:  
                    MetricsSystem.send_msg("flip b")
