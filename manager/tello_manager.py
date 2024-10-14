import os
import socket
from threading import Thread, Lock
import cv2 as cv
from time import sleep

import random
import string
from datetime import datetime

os.environ['OPENCV_FFMPEG_LOGLEVEL'] = 'quiet'
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'loglevel;error'

class TelloManager:
    def __init__(self):
        self.addr = ('192.168.10.1', 8889)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 9000))
        self.state = {}
        self.video_writer = None
        self.recording = False
        self.paused = False
        self.lock = Lock()
        self.current_frame = None
        self.video_stream_active = False
        self.record_thread = None

    def send_msg(self, command):
        self.sock.sendto(command.encode(), self.addr)
        data, _ = self.sock.recvfrom(1024)
        return data.decode()

    def receive_state(self):
        serv_addr = ('', 8890)
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serv_sock.bind(serv_addr)
        while True:
            try:
                state_data, _ = serv_sock.recvfrom(1024)
                state_str = state_data.decode('utf-8')
                print(f"Received state data: {state_str}")
                self.parse_state_data(state_str)
            except Exception as e:
                print(f"Error receiving state: {str(e)}")
                break


    def parse_state_data(self, state_str):
        try:
            data_dict = dict(item.split(':') for item in state_str.split(';') if item)
            print(f"Parsed state data: {data_dict}") 

            with self.lock:
                self.state['battery'] = data_dict.get('bat', 'Unknown')
                
                templ = float(data_dict.get('templ', 0))
                temph = float(data_dict.get('temph', 0))
                self.state['temperature'] = f"{(templ + temph) / 2:.1f}°C"
                
                speed_x = float(data_dict.get('vgx', 0))
                speed_y = float(data_dict.get('vgy', 0))
                speed_z = float(data_dict.get('vgz', 0))
                self.state['speed'] = f"{(abs(speed_x) + abs(speed_y) + abs(speed_z)) / 3:.1f} m/s"
                
                self.state['altitude'] = data_dict.get('h', 'Unknown')
                self.state['pitch'] = data_dict.get('pitch', 'Unknown')
                self.state['roll'] = data_dict.get('roll', 'Unknown')
                self.state['yaw'] = data_dict.get('yaw', 'Unknown')
                self.state['tof'] = data_dict.get('tof', 'Unknown')
                self.state['baro'] = data_dict.get('baro', 'Unknown')
                self.state['flight_time'] = data_dict.get('time', 'Unknown')
        except Exception as e:
            print(f"Error parsing state data: {str(e)}")

    def start_video_stream(self):     
        self.send_msg("streamon")

    def stop_video_stream(self):  
        self.send_msg("streamoff")

    def stop_drone_operations(self):
        data = self.send_msg('land')
        print('Response:', data)
        self.video_stream_active = False
        if self.sock:
            self.sock.close()
        if hasattr(self, 'state_socket') and self.state_socket:
            self.state_socket.close() 


    def video_stream(self):
        cap = cv.VideoCapture('udp://@0.0.0.0:11111')
        if not cap.isOpened():
            print("Error: Could not open video stream.")
            return
        self.video_stream_active = True

        while self.video_stream_active:
            ret, img = cap.read()
            if ret:
                img = cv.resize(img, (640, 480))
                self.current_frame = img 
            else:
                self.current_frame = None 

        cap.release()

    def take_photo(self):
        img = self.get_current_frame()
        if img is not None:
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'drone_capture', 'img')
            
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            
            # Date format: YYYYMMDD_HHMMSS
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')  
            random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=2))  
            filename = f"{date_str}_{random_str}.jpg"
            
            photo_path = os.path.join(base_dir, filename)
            
            cv.imwrite(photo_path, img)
            
            photo_path_normalized = os.path.normpath(photo_path)
            print(f"Photo taken and saved to {photo_path_normalized}")
        else:
            print("Failed to capture photo")    
            
    def start_recording(self):
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'drone_capture', 'video')
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=2))
        video_filename = f"{date_str}_{random_str}.mp4"
        video_path = os.path.join(base_dir, video_filename)

        self.video_writer = cv.VideoWriter(video_path, cv.VideoWriter_fourcc(*'mp4v'), 20.0, (640, 480))
        self.recording = True
        self.paused = False

        if self.record_thread is None or not self.record_thread.is_alive():
            self.record_thread = Thread(target=self.record_video)
            self.record_thread.start()

        print(f"Recording started, saving to {video_path}")
        
    def stop_recording(self):
        self.recording = False
        if self.video_writer:
            self.video_writer.release() 
        if self.record_thread:
            self.record_thread.join() 
        self.record_thread = None
        print("Recording stopped")

    def pause_recording(self):
        with self.lock:
            self.paused = True
        print("Recording paused")

    def resume_recording(self):
        with self.lock:
            self.paused = False
        print("Recording resumed")

    def record_video(self):
        while self.recording:
            with self.lock:
                if not self.paused:
                    img = self.get_current_frame()  
                    if img is not None:
                        self.video_writer.write(img)  
            sleep(0.1)

    def get_current_frame(self):
        """Return the latest captured frame for display."""
        with self.lock:
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
        data = self.send_msg('land')
        print('Response:', data)
        self.video_stream_active = False
        if self.sock:
            self.sock.close()
