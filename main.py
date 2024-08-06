import pygame
import threading
from manager.joystick_manager import JoystickManager
from manager.display_manager import DisplayManager
from manager.media_manager import MediaManager

# Backup
class DroneCaptureApp:
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    BUTTON_CAPTURE_IMAGE = 2
    BUTTON_RECORD_VIDEO = 3
    BUTTON_STOP_VIDEO = 5

    BUTTON_NAMES = {
        0: "middle button (1)",
        1: "button 2",
        2: "button 3",
        3: "button 4",
        4: "button 5",
        5: "button 6",
        6: "button 7",
        7: "button 8",
        8: "button 9",
        9: "button 10",
        10: "button 11",
        11: "button 12"
    }

    AXIS_NAMES = {
        0: "X Axis",
        1: "Y Axis",
        2: "Diagonal Axis",
        3: "Zoom in/out"
    }

    def __init__(self):
        pygame.init()
        pygame.camera.init()
        self.joystick_manager = JoystickManager()
        self.display_manager = DisplayManager()
        self.media_manager = MediaManager()
        self.camera = pygame.camera.Camera(pygame.camera.list_cameras()[0])
        self.camera.start()
        self.record_thread = None

    def record_video_task(self):
        self.media_manager.record_video(self.camera)

    def run(self):
        try:
            while True:
                self.display_manager.clear_screen()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return

                axes_values = self.joystick_manager.get_axes()
                buttons_state = self.joystick_manager.get_buttons()

                for i in range(self.joystick_manager.get_axis_count()):
                    axis_value = axes_values[i]
                    self.display_manager.draw_text(f"{self.AXIS_NAMES.get(i, f'Axis {i}')} value: {axis_value:.2f}", (20, 20 + i * 30))

                for i in range(self.joystick_manager.get_button_count()):
                    button_state = buttons_state[i]
                    self.display_manager.draw_text(f"{self.BUTTON_NAMES.get(i, f'Button {i}')} : {button_state}", (20, 140 + i * 30))

                self.display_manager.draw_axes(axes_values)
                self.display_manager.update_display()

                if buttons_state[self.BUTTON_CAPTURE_IMAGE]:
                    img_filename = self.media_manager.capture_image(self.camera)
                    if img_filename:
                        print(f"Captured image: {img_filename}")

                if buttons_state[self.BUTTON_RECORD_VIDEO] and self.record_thread is None:
                    self.record_thread = threading.Thread(target=self.record_video_task)
                    self.record_thread.start()

                if buttons_state[self.BUTTON_STOP_VIDEO] and self.record_thread is not None:
                    self.media_manager.stop_video_recording()
                    self.record_thread.join()
                    self.record_thread = None
                    print("Video recording stopped")
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            self.camera.stop()
            pygame.quit()

if __name__ == "__main__":
    app = DroneCaptureApp()
    app.run()
