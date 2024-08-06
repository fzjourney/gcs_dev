import pygame

# Initialize Pygame and Joystick
def init_joystick():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No joystick found")
        raise SystemExit("No joystick found")

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick name: {joystick.get_name()}")

    return joystick

# Get the list of axis values from the joystick
def get_axes(joystick):
    return [joystick.get_axis(i) for i in range(joystick.get_numaxes())]

# Get the list of button states from the joystick
def get_buttons(joystick):
    return [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

# Get the number of axes on the joystick
def get_axis_count(joystick):
    return joystick.get_numaxes()

# Get the number of buttons on the joystick
def get_button_count(joystick):
    return joystick.get_numbuttons()