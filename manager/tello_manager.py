import os
import socket
import random
import string
import cv2 as cv

from threading import Thread, Lock
from time import sleep
from datetime import datetime

os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "quiet"
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "loglevel;error"

class TelloManager:
    def __init__(self, log_callback=None, apply_filter=None):
        self.apply_filter = apply_filter
        self.addr = ("192.168.10.1", 8889)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", 9000))
        
        self.state = {}
        self.lock = Lock()
        
        self.current_frame = None
        self.video_stream_active = False
        self.recording = False
        self.video_writer = None
        self.frame_queue = []
        self.max_frame_queue_size = 10
        self.record_thread = None
        
        self.log_callback = log_callback

    def init_sdk_mode(self):
        data = self.send_msg("command")
        if data == "ok":
            print("Entering SDK Mode")
            return True
        else:
            print("Error initiating SDK Mode")
            return False
    
    def send_msg(self, command):
        try:
            self.sock.sendto(command.encode(), self.addr)
            data, _ = self.sock.recvfrom(1024)
            return data.decode()
        except socket.error as e:
            print(f"Socket error: {e}")
            return "error"

    def receive_state(self):
        """
        Continuously listens for state updates from the drone.
        """
        try:
            serv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            serv_sock.bind(("", 8890))
            while True:
                try:
                    state_data, _ = serv_sock.recvfrom(1024)
                    self.parse_state_data(state_data.decode("utf-8"))
                except Exception as e:
                    print(f"Error receiving state: {e}")
                    break
        finally:
            serv_sock.close()

    def parse_state_data(self, state_str):
        """
        Parses the state string received from the drone.
        """
        try:
            data_dict = {}
            for item in state_str.split(";"):
                if ":" in item:
                    key, value = item.split(":", 1)
                    data_dict[key.strip()] = value.strip()

            with self.lock:
                self.state["battery"] = data_dict.get("bat", "Unknown")
                self.state["temperature"] = self.calculate_temperature(
                    data_dict.get("templ", 0), data_dict.get("temph", 0)
                )
                self.state["speed"] = self.calculate_speed(
                    data_dict.get("vgx", 0), data_dict.get("vgy", 0), data_dict.get("vgz", 0)
                )
                self.state.update({
                    "altitude": data_dict.get("h", "Unknown"),
                    "barometer": data_dict.get("baro", "Unknown"),
                    "pitch": data_dict.get("pitch", "Unknown"),
                    "roll": data_dict.get("roll", "Unknown"),
                    "yaw": data_dict.get("yaw", "Unknown"),
                    "flight_time": data_dict.get("time", "Unknown"),
                })

        except Exception as e:
            print(f"Error parsing state data: {e}")
    
    @staticmethod
    def calculate_temperature(templ, temph):
        try:
            return f"{(float(templ) + float(temph)) / 2:.1f}"
        except ValueError:
            return "Unknown"

    @staticmethod
    def calculate_speed(vgx, vgy, vgz):
        try:
            return f"{(abs(float(vgx)) + abs(float(vgy)) + abs(float(vgz))) / 3:.1f}"
        except ValueError:
            return "Unknown"
        
    def get_state(self):
        with self.lock:
            return self.state.copy()

    def start_video_stream(self):
        data = self.send_msg("streamon")
        if data == "ok":
            thread = Thread(target=self.video_stream)
            thread.start()
            return True
        else:
            print("Error starting video stream")
            return False

    def video_stream(self):
        cap = cv.VideoCapture("udp://@0.0.0.0:11111")
        if not cap.isOpened():
            print("Error: Could not open video stream.")
            return
        self.video_stream_active = True

        while self.video_stream_active:
            ret, img = cap.read()
            if ret:
                img = cv.resize(img, (640, 480))
                with self.lock:
                    self.current_frame = img
                if self.recording and not self.paused:
                    if len(self.frame_queue) < self.max_frame_queue_size:
                        self.frame_queue.append(img)
                    else:
                        sleep(0.05)
            else:
                self.current_frame = None

        cap.release()

    def stop_video_stream(self):
        self.send_msg("streamoff")

    def take_photo(self):
        img = self.get_current_frame()
        if img is not None:
            if self.apply_filter:
                img = self.apply_filter(img)  # Apply the filter if provided

            base_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "drone_capture", "img"
            )
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)

            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_str = "".join(random.choices(string.ascii_letters + string.digits, k=2))
            filename = f"{date_str}_{random_str}.jpg"
            photo_path = os.path.join(base_dir, filename)
            cv.imwrite(photo_path, img)

            log_msg = f"Photo taken and saved to {photo_path}"
            print(log_msg)
            if self.log_callback:
                self.log_callback(log_msg)  # Invoke the log callback
        else:
            error_msg = "Failed to capture photo"
            print(error_msg)
            if self.log_callback:
                self.log_callback(error_msg)  # Invoke the log callback on error

    def start_recording(self):
        base_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "drone_capture", "video"
        )
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_str = "".join(random.choices(string.ascii_letters + string.digits, k=2))
        video_filename = f"{date_str}_{random_str}.mp4"
        video_path = os.path.join(base_dir, video_filename)

        self.video_writer = cv.VideoWriter(
            video_path, cv.VideoWriter_fourcc(*"mp4v"), 20.0, (640, 480)
        )
        self.recording = True
        self.paused = False

        if self.record_thread is None or not self.record_thread.is_alive():
            self.record_thread = Thread(target=self.record_video, daemon=True)
            self.record_thread.start()

        log_msg = f"Recording started, saving to {video_path}"
        print(log_msg)
        if self.log_callback:
            self.log_callback(log_msg)  # Invoke the log callback when recording starts

    def record_video(self):
        while self.recording:
            with self.lock:
                if not self.paused and len(self.frame_queue) > 0:
                    frame = self.frame_queue.pop(0)
                    if frame is not None:
                        if self.apply_filter:
                            frame = self.apply_filter(frame)  # Apply filter to each frame
                        self.video_writer.write(frame)
            sleep(0.05)
    def stop_recording(self):
        self.recording = False
        if self.video_writer:
            self.video_writer.release()
        if self.record_thread:
            self.record_thread.join()
        self.record_thread = None
        # log_msg = "Recording stopped"
        # print(log_msg)
        # if self.log_callback:
        #     self.log_callback(log_msg)

    def pause_recording(self):
        with self.lock:
            self.paused = True
        print("Recording paused")

    def resume_recording(self):
        with self.lock:
            self.paused = False
        print("Recording resumed")

    def stop_drone_operations(self):
        data = self.send_msg("land")
        print("Response:", data)
        self.video_stream_active = False
        if self.sock:
            self.sock.close()
        if hasattr(self, "state_socket") and self.state_socket:
            self.state_socket.close()

    def get_current_frame(self):
        with self.lock:
            return self.current_frame
