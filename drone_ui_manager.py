import cv2
import sys
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, 
    QPushButton, QLabel,
    QHBoxLayout, QTextEdit, 
    QGroupBox, QGridLayout, 
    QSizePolicy, QStackedLayout, 
    QMessageBox,
)
from PySide6.QtCore import (
    Qt, 
    QTimer,
)
from PySide6.QtGui import ( 
    QImage, 
    QPixmap, 
    QTextCursor,
)
from datetime import datetime
from threading import Thread

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manager'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drone_capture'))

from Controller import Controller

class DroneControlAppUIManager(QWidget):
    def __init__(self, tello_manager):
        super().__init__()
        self.tello_manager = tello_manager  
        self.joystick_manager = Controller()
        self.tello_manager.log_callback = self.log_action
        self.init_ui()
        
        # Check battery level
        self.last_battery_warning = 100 

        if self.tello_manager.init_sdk_mode():
            self.state_thread = Thread(target=self.tello_manager.receive_state, daemon=True)
            self.state_thread.start()

        self.tello_manager.start_video_stream()
        self.tello_manager.apply_filter = self.apply_filter

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_feed)
        self.timer.start(50)

        self.telemetry_timer = QTimer(self)
        self.telemetry_timer.timeout.connect(self.update_telemetry_metrics)
        self.telemetry_timer.start(1000)

        self.joystick_timer = QTimer(self)
        self.joystick_timer.timeout.connect(self.update_joystick_display)
        self.joystick_timer.start(100)

        self.recording_active = False
        self.current_filter = "normal"

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
        land_button.setStyleSheet("font-size: 20px; padding: 10px;")
        land_button.clicked.connect(self.land)

        left_layout.addWidget(takeoff_button)
        left_layout.addWidget(land_button)

        filter_group = self.create_filter_controls()
        left_layout.addWidget(filter_group)

        metrics_group = self.create_metrics_display()
        left_layout.addWidget(metrics_group)

        log_group = QGroupBox("Log")
        log_group.setStyleSheet("font-size: 20px")
        log_layout = QVBoxLayout()

        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        log_layout.addWidget(self.log_text_edit)

        log_group.setLayout(log_layout)
        left_layout.addWidget(log_group)

        joystick_group = QGroupBox("Joystick Inputs")
        joystick_group.setStyleSheet("font-size: 20px")
        joystick_layout = QVBoxLayout()

        self.joystick_display_widget = QTextEdit()
        self.joystick_display_widget.setReadOnly(True)
        joystick_layout.addWidget(self.joystick_display_widget)

        joystick_group.setLayout(joystick_layout)
        left_layout.addWidget(joystick_group)

        main_layout.addLayout(left_layout, 8)
        right_layout = QVBoxLayout()
        video_container = QStackedLayout()

        self.video_label = QLabel("Video Stream")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet(
            "background-color: black; color: white; font-size: 18px;"
        )
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        video_container.addWidget(self.video_label)

        right_layout.addLayout(video_container)

        telemetry_layout = QHBoxLayout()
        self.battery_label = QLabel("Battery: --%")
        self.pitch_label = QLabel("Pitch: --°")
        self.roll_label = QLabel("Roll: --°")
        self.yaw_label = QLabel("Yaw: --°")
        self.flight_time_label = QLabel("Flight Time: --")

        for label in [
            self.battery_label,
            self.pitch_label,
            self.roll_label,
            self.yaw_label,
            self.flight_time_label,
        ]:
            label.setStyleSheet(
                "font-size: 20px; padding: 5px; color: white; background-color: rgba(0, 0, 0, 0.5);"
            )
            telemetry_layout.addWidget(label)

        right_layout.addLayout(telemetry_layout)
        main_layout.addLayout(right_layout, 14)

        self.setLayout(main_layout)

    def create_filter_controls(self):
        filter_group = QGroupBox("Filter Camera")
        filter_group.setStyleSheet("font-size: 20px")
        filter_layout = QGridLayout()

        filters = {
            "Normal": "normal",
            "B&W": "bw",
            "Grayscale": "grayscale",
            "Invert": "invert",
        }

        for i, (name, value) in enumerate(filters.items()):
            button = QPushButton(name)
            button.setStyleSheet("font-size: 20px; padding: 10px;")
            button.clicked.connect(lambda _, v=value: self.set_filter(v))
            filter_layout.addWidget(button, i // 2, i % 2)

        filter_group.setLayout(filter_layout)
        return filter_group

    def create_metrics_display(self):
        metrics_group = QGroupBox("Metrics")
        metrics_group.setStyleSheet("font-size: 20px")
        metrics_layout = QVBoxLayout()

        self.temp_label = QLabel("Temperature: --°C")
        self.speed_label = QLabel("Speed: -- m/s")
        self.altitude_label = QLabel("Altitude: -- m")
        self.height_label = QLabel("Barometer: -- cm")

        for label in [
            self.temp_label,
            self.speed_label,
            self.altitude_label,
            self.height_label,
        ]:
            label.setStyleSheet("font-size: 25px;")
            metrics_layout.addWidget(label)

        metrics_group.setLayout(metrics_layout)
        return metrics_group

    def takeoff(self):
        self.tello_manager.send_msg("takeoff")
        self.log_action("Takeoff initiated")

    def land(self):
        self.tello_manager.send_msg("land")
        self.log_action("Landing initiated")

    def take_photo(self):
        self.tello_manager.take_photo()

    def start_video(self):
        self.tello_manager.start_recording()

    def stop_video(self):
        self.tello_manager.stop_recording()
        
    def set_filter(self, filter_type):
        self.current_filter = filter_type

    def update_video_feed(self):
        frame = self.tello_manager.get_current_frame()
        if frame is not None:
            frame = self.apply_filter(frame)

            frame = cv2.resize(frame, (self.video_label.width(), self.video_label.height()))
            q_img = QImage(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).data,
                        frame.shape[1], frame.shape[0], QImage.Format_RGB888)

            self.video_label.setPixmap(QPixmap.fromImage(q_img))

    def apply_filter(self, frame):
        if self.current_filter == "normal":
            return frame
        elif self.current_filter == "bw":
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            frame = cv2.adaptiveThreshold(gray_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

            return cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        elif self.current_filter == "grayscale":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        elif self.current_filter == "invert":
            frame = cv2.bitwise_not(frame)
            return frame

    def format_time(self, seconds):
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def update_telemetry_metrics(self):
        state = self.tello_manager.get_state()
        
        flight_time_seconds = state.get('flight_time', 0)
        formatted_flight_time = self.format_time(flight_time_seconds)
        
        self.temp_label.setText(f"Temperature: {state.get('temperature', '--')}°C")
        self.speed_label.setText(f"Speed: {state.get('speed', '--')} m/s")
        self.altitude_label.setText(f"Altitude: {state.get('altitude', '--')} m")
        self.height_label.setText(f"Barometer: {state.get('barometer', '--')} cm")
        self.battery_label.setText(f"Battery: {state.get('battery', '--')}%")
        self.pitch_label.setText(f"Pitch: {state.get('pitch', '--')}°")
        self.roll_label.setText(f"Roll: {state.get('roll', '--')}°")
        self.yaw_label.setText(f"Yaw: {state.get('yaw', '--')}°")
        self.flight_time_label.setText(f"Flight Time: {formatted_flight_time}")
        
        # Battery Warning Logic
        try:
            battery_level = int(state.get('battery', 100)) 
        except ValueError:
            battery_level = 100

        if battery_level <= 15 and battery_level <= self.last_battery_warning - 5:
            self.show_battery_warning(battery_level)
            self.last_battery_warning = battery_level

    def update_joystick_display(self):
        buttons = self.joystick_manager.get_buttons()
        axes = self.joystick_manager.get_axes()

        joystick_text = ""

        for i, button in enumerate(buttons):
            if button:  
                joystick_text += f"Button {i+1}: Pressed\n"

        axis_threshold = 0.1  
        for i, axis_value in enumerate(axes):
            if abs(axis_value) > axis_threshold:  
                joystick_text += f"Axis {i+1}: {axis_value:.2f}\n"

        self.joystick_display_widget.setText(joystick_text)

        self.joystick_display_widget.moveCursor(QTextCursor.End)

    def log_action(self, message):
        cursor = self.log_text_edit.textCursor()
        cursor.movePosition(QTextCursor.Start)
        
        if cursor.selectedText(): 
            cursor.insertText("\n" + message)
        else:
            cursor.insertText(message) 
        
        self.log_text_edit.setTextCursor(cursor)
        self.log_text_edit.ensureCursorVisible()

    def show_battery_warning(self, battery_level):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Low Battery Warning")
        msg.setText(f"Battery level is critically low: {battery_level}%.\nPlease land immediately.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
        