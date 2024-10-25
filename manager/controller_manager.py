import pygame

""" 
    DO NOT TOUCH!
    UNLESS MAJOR UPDATE IS NEEDED
    
    Designed to manage joystick input using the Pygame library. 
    It initializes the joystick, checks for its availability, and 
    provides methods to access joystick axes and button states. 
    It effectively serves as an interface to interact with the joystick, 
    enabling the retrieval of input data for applications such as gaming or 
    drone control.
"""
class JoystickManager:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("No joystick found")
            raise SystemExit("No joystick found")

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        print(f"Joystick name: {self.joystick.get_name()}")

    def get_axes(self):
        return [self.joystick.get_axis(i) for i in range(self.joystick.get_numaxes())]

    def get_buttons(self):
        pygame.event.pump()
        button_states = [self.joystick.get_button(i) for i in range(self.joystick.get_numbuttons())]
        return button_states

    def get_axis_count(self):
        return self.joystick.get_numaxes()

    def get_button_count(self):
        return self.joystick.get_numbuttons()