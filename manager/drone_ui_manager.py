import sys
import os
import cv2
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QMessageBox, QGroupBox, QGridLayout, QSizePolicy
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from threading import Thread
from time import sleep

from tello_manager import TelloManager
from controller_manager import JoystickManager

class DroneControlAppUIManager(QWidget):
    def __init__(self):
        super().__init__()
        self.tello_manager = TelloManager()
        self.joystick_manager = JoystickManager()
        self.init_ui()
        
        if self.tello_manager.init_sdk_mode():
            self.state_thread = Thread(target=self.tello_manager.receive_state)
            self.state_thread.start()
        
        self.tello_manager.start_video_stream()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_feed)
        self.timer.start(30) 
        
        self.recording_active = False

    def init_ui(self):
        self.setWindowTitle("Drone Control Interface")
        self.setGeometry(100, 100, 800, 500)
        
        self.setWindowState(Qt.WindowMaximized) 
        self.setWindowFlag(Qt.WindowStaysOnBottomHint, False)

        main_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        
        takeoff_button = QPushButton("Takeoff")
        takeoff_button.setStyleSheet("font-size: 20px; padding: 10px;")
        takeoff_button.clicked.connect(self.takeoff)

        land_button = QPushButton("Land")
        land_button.clicked.connect(self.land)
        land_button.setStyleSheet("font-size: 20px; padding: 10px;")

        left_layout.addWidget(takeoff_button)
        left_layout.addWidget(land_button)

        filter_group = QGroupBox("Filter Camera")
        filter_group.setStyleSheet("font-size: 20px")
        filter_layout = QGridLayout()

        bw_button = QPushButton("B&W")
        bw_button.clicked.connect(lambda: self.set_filter("bw"))
        bw_button.setStyleSheet("font-size: 20px; padding: 10px;")

        grayscale_button = QPushButton("Greyscale")
        grayscale_button.clicked.connect(lambda: self.set_filter("grayscale"))
        grayscale_button.setStyleSheet("font-size: 20px; padding: 10px;")

        invert_button = QPushButton("Invert")
        invert_button.clicked.connect(lambda: self.set_filter("invert"))
        invert_button.setStyleSheet("font-size: 20px; padding: 10px;")

        normal_button = QPushButton("Normal")
        normal_button.clicked.connect(lambda: self.set_filter("normal"))  
        normal_button.setStyleSheet("font-size: 20px; padding: 10px;")

        filter_layout.addWidget(normal_button, 1, 0) 
        filter_layout.addWidget(bw_button, 1, 1)
        filter_layout.addWidget(grayscale_button, 2, 0)
        filter_layout.addWidget(invert_button, 2, 1)

        filter_group.setLayout(filter_layout)
        left_layout.addWidget(filter_group)

        metrics_group = QGroupBox("Metrics")
        metrics_group.setStyleSheet("font-size: 20px")
        metrics_layout = QVBoxLayout()

        self.temp_label = QLabel("Temperature: --°C")
        self.speed_label = QLabel("Speed: -- km/s")
        self.altitude_label = QLabel("Altitude: -- m")
        self.height_label = QLabel("Height: -- m")

        self.temp_label.setStyleSheet("font-size: 25px;")
        self.speed_label.setStyleSheet("font-size: 25px;")
        self.altitude_label.setStyleSheet("font-size: 25px;")
        self.height_label.setStyleSheet("font-size: 25px;")

        metrics_layout.addWidget(self.temp_label)
        metrics_layout.addWidget(self.speed_label)
        metrics_layout.addWidget(self.altitude_label)
        metrics_layout.addWidget(self.height_label)

        metrics_group.setLayout(metrics_layout)
        left_layout.addWidget(metrics_group)

        main_layout.addLayout(left_layout, 8) 

        right_layout = QVBoxLayout()

        self.video_label = QLabel("Video Stream")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: transparent; color: white; font-size: 18px;")
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  
        right_layout.addWidget(self.video_label)

        main_layout.addLayout(right_layout, 14)  

    def takeoff(self):
        self.tello_manager.send_msg('takeoff')
        self.show_message("Takeoff initiated")

    def land(self):
        self.tello_manager.send_msg('land')
        self.show_message("Landing initiated")

    def show_message(self, action):
        msg = QMessageBox()
        msg.setText(f"{action}")
        msg.exec()

    def set_filter(self, filter_type):
        """Set the current filter to be applied."""
        self.current_filter = filter_type

    def update_video_feed(self):
        """Capture video from the drone's camera and display it with applied filters."""
        frame = self.tello_manager.get_current_frame() 
        if frame is not None:
            # Black and White Filter
            if self.current_filter == "bw":
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  
                _, frame = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)  
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR) 
            # Greyscale Filter
            elif self.current_filter == "grayscale":
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR) 
            # Invert Filter
            elif self.current_filter == "invert":
                frame = cv2.bitwise_not(frame)  
            # No Filter
            elif self.current_filter == "normal":
                pass
            
            frame_height, frame_width, _ = frame.shape
            label_height = self.video_label.height()
            label_width = self.video_label.width()

            if frame_width / frame_height > label_width / label_height:
                new_width = label_width
                new_height = int(label_width * frame_height / frame_width)
            else:
                new_height = label_height
                new_width = int(label_height * frame_width / frame_height)

            frame = cv2.resize(frame, (new_width, new_height))

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_img))

    def closeEvent(self, event):
        self.cap.release()
        self.tello_manager.stop_drone_operations()
        event.accept()

if __name__ == "__main__":
    app = QApplication([])
    window = DroneControlAppUIManager()
    window.show()
    app.exec()
