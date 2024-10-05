import os
import socket
from threading import Thread
import cv2 as cv
from time import sleep

import random
import string
from datetime import datetime

os.environ['OPENCV_FFMPEG_LOGLEVEL'] = 'quiet'

class TelloManager:
    def __init__(self):
        self.addr = ('192.168.10.1', 8889)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 9000))
        self.state = {}
        self.video_writer = None
        self.recording = False
        self.current_frame = None
        self.video_stream_active = False

    def send_msg(self, command):
        self.sock.sendto(command.encode(), self.addr)
        data, _ = self.sock.recvfrom(1024)
        return data.decode()

    def receive_state(self):
        serv_addr = ('', 8890)
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serv_sock.bind(serv_addr)
        while True:
            raw_data, _ = serv_sock.recvfrom(1024)
            raw_data = raw_data.decode()
            data = raw_data.split(';')
            for i in data:
                if ':' in i:
                    item = i.split(':')
                    self.state[item[0]] = float(item[1])
        serv_sock.close()

    def video_stream(self):
        cap = cv.VideoCapture('udp://@0.0.0.0:11111')
        if not cap.isOpened():
            cap.open('udp://@0.0.0.0:11111')

        cap.set(cv.CAP_PROP_BUFFERSIZE, 3)
        self.video_stream_active = True

        while self.video_stream_active:
            ret, img = cap.read()
            if ret:
                img = cv.resize(img, (640, 480))
                self.current_frame = img  
                cv.imshow('Flight', img)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv.destroyAllWindows()

    def take_photo(self):
        img = self.get_current_frame()
        if img is not None:
            # Base directory for saving photos
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'drone_capture', 'img')
            
            # Ensure the directory exists
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            
            # Generate a unique filename with the current date and a random string
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')  # Date format: YYYYMMDD_HHMMSS
            random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=6))  # Random 6-char string
            filename = f"{date_str}_{random_str}.jpg"
            
            # Full photo path
            photo_path = os.path.join(base_dir, filename)
            
            # Save the image
            cv.imwrite(photo_path, img)
            
            # Normalize the path for printing
            photo_path_normalized = os.path.normpath(photo_path)
            print(f"Photo taken and saved to {photo_path_normalized}")
        else:
            print("Failed to capture photo")    
            
    def start_recording(self):
        video_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drone_capture', 'video', 'output.avi')
        self.video_writer = cv.VideoWriter(video_path, cv.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))
        self.recording = True

        self.record_thread = Thread(target=self.record_video)
        self.record_thread.start()

    def record_video(self):
        while self.recording:
            img = self.get_current_frame()  
            if img is not None:
                self.video_writer.write(img)
            sleep(0.1)

    def stop_recording(self):
        self.recording = False
        if self.video_writer:
            self.video_writer.release()
        if self.record_thread:
            self.record_thread.join()

    def get_current_frame(self):
        """Returns the most recent frame from the active video stream."""
        return self.current_frame

    def init_sdk_mode(self):
        data = self.send_msg("command")
        if data == 'ok':
            print("Entering SDK Mode")
            return True
        else:
            print("Error initiating SDK Mode")
            return False

    def start_video_stream(self):
        data = self.send_msg('streamon')
        if data == 'ok':
            thread = Thread(target=self.video_stream)
            thread.start()
            return True
        else:
            print("Error starting video stream")
            return False

    def stop_drone_operations(self):
        """Stop video stream and drone operations."""
        data = self.send_msg('land')
        print('Response:', data)
        self.video_stream_active = False
        if self.sock:
            self.sock.close()
