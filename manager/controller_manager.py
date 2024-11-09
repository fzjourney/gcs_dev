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
        """
        Initializes the JoystickManager by setting up the Pygame library and the joystick.

        This constructor checks for the availability of joysticks and initializes the first
        available joystick. If no joystick is found, it exits the application with an error message.
        """
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("No joystick found")
            raise SystemExit("No joystick found")

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        print(f"Joystick name: {self.joystick.get_name()}")

    def get_axes(self):
        """
        Retrieves the current state of the joystick axes.

        Returns a list of values from -1.0 to 1.0, representing the state of each axis. A value of 0.0 indicates the axis is centered.

        :return: A list of axis values
        :rtype: List[float]
        """

        return [self.joystick.get_axis(i) for i in range(self.joystick.get_numaxes())]

    def get_buttons(self):
        """
        Retrieves the current state of the joystick buttons.

        Returns a list of boolean values, each representing the state of a button. A value of True indicates the button is pressed.

        :return: A list of button states
        :rtype: List[bool]
        """

        pygame.event.pump()
        button_states = [self.joystick.get_button(i) for i in range(self.joystick.get_numbuttons())]
        return button_states

    def get_axis_count(self):
        """
        Retrieves the number of axes on the joystick.

        :return: The number of axes on the joystick
        :rtype: int
        """
        return self.joystick.get_numaxes()

    def get_button_count(self):
        """
        Retrieves the number of buttons on the joystick.

        :return: The number of buttons on the joystick
        :rtype: int
        """
        return self.joystick.get_numbuttons()