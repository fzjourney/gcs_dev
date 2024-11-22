import pygame
from typing import List

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