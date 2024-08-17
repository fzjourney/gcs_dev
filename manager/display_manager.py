import pygame
import numpy as np
import time

class DisplayManager:
    def __init__(self):
        pygame.init()
        self.screen_width, self.screen_height = 800, 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Joystick Input Display")
        self.font = pygame.font.Font(None, 24)
        self.frame_surface = None  # Surface for the video frame

    def update_frame(self, frame):
        # Convert the OpenCV frame to Pygame Surface
        frame = np.rot90(frame)  # Rotate the frame to match Pygame orientation
        frame = np.flipud(frame)  # Flip the frame vertically
        frame_surface = pygame.surfarray.make_surface(frame)
        self.frame_surface = pygame.transform.scale(frame_surface, (640, 480))

    def draw_axes(self, axes_values):
        square_size = 200
        graph_top_left_x = self.screen_width - square_size - 40
        graph_top_left_y = 40
        center_x = graph_top_left_x + square_size // 2
        center_y = graph_top_left_y + square_size // 2

        pygame.draw.rect(self.screen, (255, 255, 255), (graph_top_left_x, graph_top_left_y, square_size, square_size), 1)
        pygame.draw.line(self.screen, (255, 0, 0), (center_x, graph_top_left_y), (center_x, graph_top_left_y + square_size), 1)
        pygame.draw.line(self.screen, (255, 0, 0), (graph_top_left_x, center_y), (graph_top_left_x + square_size, center_y), 1)

        axis_0_pos = center_x + int(axes_values[0] * (square_size // 2))
        axis_1_pos = center_y - int(axes_values[1] * (square_size // 2))
        pygame.draw.circle(self.screen, (0, 255, 0), (axis_0_pos, axis_1_pos), 10)

        if len(axes_values) > 2:
            roll_pos = center_x + int(axes_values[2] * (square_size // 2))
            pygame.draw.line(self.screen, (0, 0, 255), (center_x, center_y), (roll_pos, axis_1_pos), 2)

        self.draw_text("(x)", (graph_top_left_x + square_size + 10, center_y - 10))
        self.draw_text("(y)", (center_x - 10, graph_top_left_y - 30))

    def update_display(self):
        if self.frame_surface:
            self.screen.blit(self.frame_surface, (0, 0))  # Blit the frame surface onto the Pygame screen
        pygame.display.flip()
        time.sleep(0.1)

    def clear_screen(self):
        self.screen.fill((0, 0, 0))
