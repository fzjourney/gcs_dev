import pygame

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
        return [self.joystick.get_button(i) for i in range(self.joystick.get_numbuttons())]

    def get_axis_count(self):
        return self.joystick.get_numaxes()

    def get_button_count(self):
        return self.joystick.get_numbuttons()
