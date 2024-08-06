import pygame.camera
import cv2
import os
import time
from .error_logger_manager import ErrorLoggerManager

VIDEO_DIR = "drone_capture/video"
IMAGE_DIR = "drone_capture/img"
LOG_DIR = "drone_capture/log"

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

class MediaManager:
    record_video_flag = False

    @staticmethod
    def capture_image(camera):
        try:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            img_filename = os.path.join(IMAGE_DIR, f"image_{timestamp}.jpg")
            img = camera.get_image()
            pygame.image.save(img, img_filename)
            print(f"Image captured and saved: {img_filename}")
            return img_filename
        except Exception as e:
            ErrorLoggerManager.log_error(f"Error capturing image: {str(e)}")
            return None

    @classmethod
    def record_video(cls, camera):
        try:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            video_filename = os.path.join(VIDEO_DIR, f"video_{timestamp}.avi")
            
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            fps = 30.0
            frame_size = (camera.get_size()[0], camera.get_size()[1])
            out = cv2.VideoWriter(video_filename, fourcc, fps, frame_size)
            
            print(f"Recording video to: {video_filename}")
            cls.record_video_flag = True

            while cls.record_video_flag:
                img = camera.get_image()
                frame = pygame.surfarray.pixels3d(img)
                frame = frame.swapaxes(0, 1)
                out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

            out.release()
            print(f"Video recording saved: {video_filename}")
        except Exception as e:
            ErrorLoggerManager.log_error(f"Error recording video: {str(e)}")

    @classmethod
    def stop_video_recording(cls):
        cls.record_video_flag = False
