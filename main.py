import pygame
from manager.media_manager import MediaManager

# Backup
class DroneCaptureApp:
    def __init__(self):
        pygame.init()
        pygame.camera.init()
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
                    
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            self.camera.stop()
            pygame.quit()

if __name__ == "__main__":
    app = DroneCaptureApp()
    app.run()
