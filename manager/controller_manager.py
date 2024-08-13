import pygame
import time
from tello_manager import send_msg, state

class JoystickController:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("No joystick detected")
            exit()

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        print("Joystick connected:", self.joystick.get_name())

    def get_joystick_input(self):
        pygame.event.pump()

        # Mapping joystick inputs based on your provided layout
        axis_x = self.joystick.get_axis(0)  # Roll (left/right)
        axis_y = self.joystick.get_axis(1)  # Pitch (forward/backward)
        zoom = self.joystick.get_axis(3)    # Throttle (up/down)
        
        middle_button = self.joystick.get_button(1)  # Button for takeoff/land

        return {
            'roll': axis_x,
            'pitch': axis_y,
            'throttle': zoom,
            'takeoff_land': middle_button,
        }

    def send_drone_commands(self, inputs):
        # Convert joystick inputs to drone commands
        roll = int(inputs['roll'] * 100)
        pitch = int(inputs['pitch'] * 100)
        throttle = int(inputs['throttle'] * 100)
        yaw = 0  # Assuming you are not using yaw for now

        # Send commands to the drone based on joystick input
        send_msg(f'rc {roll} {pitch} {throttle} {yaw}')

        # Handle takeoff and landing with the middle button
        if inputs['takeoff_land']:
            send_msg('takeoff')
            print('Takeoff command sent')
            time.sleep(1)  # Simple debounce logic
        elif inputs['takeoff_land'] == 0:
            send_msg('land')
            print('Land command sent')
            time.sleep(1)  # Simple debounce logic

    def run(self):
        print("Starting Joystick Controller")
        while True:
            inputs = self.get_joystick_input()
            self.send_drone_commands(inputs)
            time.sleep(0.1)

if __name__ == "__main__":
    controller = JoystickController()
    controller.run()
