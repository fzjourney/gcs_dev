import pygame
import time


"""
    TESTING PURPOSES OF THE JOYSTICK DISPLAY
    
    Manages the graphical display of joystick inputs using Pygame. 
    It handles the initialization of the display, rendering text, 
    drawing axes for joystick values, and updating the screen accordingly.
"""

class DisplayManager:
    def __init__(self):
        """
        Initializes the DisplayManager by setting up the Pygame library and the display.

        It sets up a window of size 800x600 with the title "Joystick Input Display" and
        a font for rendering text to the screen.
        """
        pygame.init()
        self.screen_width, self.screen_height = 800, 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Joystick Input Display")
        self.font = pygame.font.Font(None, 24)

    def draw_text(self, text, position, color=(255, 255, 255)):
        """
        Renders and displays a given text at the specified position on the screen.

        :param text: The text to be rendered and displayed
        :param position: The (x, y) coordinates of the text's top-left corner
        :param color: The color of the text (RGB), defaults to white
        """
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, position)

    def draw_axes(self, axes_values):
        """
        Draws a graphical representation of joystick axes on the screen.

        This method renders a square representing the boundary for joystick input visualization.
        It draws the axes lines and positions a circle based on the x and y values from the 
        `axes_values`. If a third axis value is present, it draws an additional line to represent roll.

        :param axes_values: A list of joystick axis values, where the first two values are the 
                            x and y axes, and an optional third value represents roll.
        """
        square_size = 200
        graph_top_left_x = self.screen_width - square_size - 40
        graph_top_left_y = 40
        center_x = graph_top_left_x + square_size // 2
        center_y = graph_top_left_y + square_size // 2

        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            (graph_top_left_x, graph_top_left_y, square_size, square_size),
            1,
        )
        pygame.draw.line(
            self.screen,
            (255, 0, 0),
            (center_x, graph_top_left_y),
            (center_x, graph_top_left_y + square_size),
            1,
        )
        pygame.draw.line(
            self.screen,
            (255, 0, 0),
            (graph_top_left_x, center_y),
            (graph_top_left_x + square_size, center_y),
            1,
        )

        axis_0_pos = center_x + int(axes_values[0] * (square_size // 2))
        axis_1_pos = center_y - int(axes_values[1] * (square_size // 2))
        pygame.draw.circle(self.screen, (0, 255, 0), (axis_0_pos, axis_1_pos), 10)

        if len(axes_values) > 2:
            roll_pos = center_x + int(axes_values[2] * (square_size // 2))
            pygame.draw.line(
                self.screen,
                (0, 0, 255),
                (center_x, center_y),
                (roll_pos, axis_1_pos),
                2,
            )

        self.draw_text("(x)", (graph_top_left_x + square_size + 10, center_y - 10))
        self.draw_text("(y)", (center_x - 10, graph_top_left_y - 30))

    def update_display(self):
        """
        Updates the display by swapping the front and back buffers and then pauses execution for 0.1 seconds,
        effectively creating a 10 FPS cap.
        """
        pygame.display.flip()
        time.sleep(0.1)

    def clear_screen(self):
        """
        Clears the screen by filling it with black.
        """
        
        self.screen.fill((0, 0, 0))
