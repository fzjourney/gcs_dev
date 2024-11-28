import cv2
import sys
import os

from threading import Thread
from time import sleep
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, 
    QPushButton, QLabel, QHBoxLayout, 
    QTextEdit, QGroupBox, QGridLayout, 
    QSizePolicy, QStackedLayout, QMessageBox,
)
from PySide6.QtCore import (
    Qt, QTimer,
)
from PySide6.QtGui import ( 
    QImage, QPixmap, 
)

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manager'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drone_capture'))

from manager.MetricsSystem import MetricsSystem
from manager.Controller import Controller
from manager.CameraFilter import CameraFilter
from manager.Log import Log

class SoftwareGCS(QWidget):
    def __init__(self, MetricsSystem):
        super().__init__()
        self.MetricsSystem = MetricsSystem  
        self.Controller = Controller()
        
        self.log_text_edit = QTextEdit()  
        self.log_text_edit.setReadOnly(True) 
        
        self.Log = Log(self.log_text_edit)  
        self.MetricsSystem.log_action = self.Log.log_callback  
        
        self.CameraFilter = CameraFilter()
        self.init_ui()
        
        self.last_battery_warning = 100 
        self.recording_active = [False]
        
        self.status_message = QLabel("")
        self.status_message.setStyleSheet("color: red; font-size: 15px; background-color: rgba(0, 0, 0, 0.5);")
        self.status_message.setVisible(False)
        
        self.video_label.setLayout(QVBoxLayout())
        self.video_label.layout().addWidget(self.status_message, alignment=Qt.AlignTop | Qt.AlignLeft)

        if self.MetricsSystem.init_sdk_mode():
            self.state_thread = Thread(target=self.MetricsSystem.receive_state, daemon=True)
            self.state_thread.start()

        self.MetricsSystem.start_video_stream()
        self.MetricsSystem.apply_filter = self.CameraFilter.apply_filter

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_feed)
        self.timer.start(50)

        self.telemetry_timer = QTimer(self)
        self.telemetry_timer.timeout.connect(self.update_telemetry_metrics)
        self.telemetry_timer.start(1000)

        self.joystick_timer = QTimer(self)
        self.joystick_timer.timeout.connect(lambda: self.Controller.update_joystick_display(self.joystick_display_widget))
        self.joystick_timer.start(100)

        self.joystick_thread = Thread(target=self.Controller.run_joystick_control, args=(self.MetricsSystem, self.recording_active), daemon=True)
        self.joystick_thread.start()  
        
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
        
        log_layout.addWidget(self.log_text_edit) 
        log_group.setLayout(log_layout)
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
            button.clicked.connect(lambda _, v=value: self.CameraFilter.set_filter(v))
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
        self.MetricsSystem.send_msg("takeoff")
        self.log_callback("Takeoff initiated")

    def land(self):
        self.MetricsSystem.send_msg("land")
        self.log_callback("Landing initiated")

    def take_photo(self):
        self.MetricsSystem.take_photo()

    def start_video(self):
        self.MetricsSystem.start_recording()

    def stop_video(self):
        self.MetricsSystem.stop_recording()

    def update_video_feed(self):
        frame = self.MetricsSystem.get_current_frame()
        if frame is not None:
            frame = self.CameraFilter.apply_filter(frame)

            frame = cv2.resize(frame, (self.video_label.width(), self.video_label.height()))
            q_img = QImage(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).data,
                        frame.shape[1], frame.shape[0], QImage.Format_RGB888)

            self.video_label.setPixmap(QPixmap.fromImage(q_img))

            if self.MetricsSystem.paused:
                self.status_message.setText("Recording Paused")
                self.status_message.setVisible(True)
            else:
                self.status_message.setVisible(False)

    def pause_video(self):
        self.MetricsSystem.pause_recording()
        self.status_message.setText("Recording Paused")
        self.status_message.setVisible(True)

    def hide_status_message(self):
        self.status_message.setVisible(False)
        
    def format_time(self, seconds):
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def update_telemetry_metrics(self):
        state = self.MetricsSystem.update_telemetry_metrics()
        
        flight_time_seconds = state.get('flight_time', 0)
        formatted_flight_time = self.format_time(flight_time_seconds)
        
        self.temp_label.setText(f"Temperature: {state.get('temperature', '--')}°C")
        self.speed_label.setText(f"Speed: {state.get('speed', '--')} m/s")
        self .altitude_label.setText(f"Altitude: {state.get('altitude', '--')} m")
        self.height_label.setText(f"Barometer: {state.get('barometer', '--')} cm")
        self.battery_label.setText(f"Battery: {state.get('battery', '--')}%")
        self.pitch_label.setText(f"Pitch: {state.get('pitch', '--')}°")
        self.roll_label.setText(f"Roll: {state.get('roll', '--')}°")
        self.yaw_label.setText(f"Yaw: {state.get('yaw', '--')}°")
        self.flight_time_label.setText(f"Flight Time: {formatted_flight_time}")
        
        try:
            battery_level = int(state.get('battery', 100)) 
        except ValueError:
            battery_level = 100

        if battery_level <= 15 and battery_level <= self.last_battery_warning - 5:
            self.show_battery_warning(battery_level)
            self.last_battery_warning = battery_level

    def show_battery_warning(self, battery_level):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Low Battery Warning")
        msg.setText(f"Battery level is critically low: {battery_level}%.\nPlease land immediately.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

if __name__ == "__main__":
    MetricsSystem = MetricsSystem()

    app = QApplication(sys.argv)
    app_ui = SoftwareGCS(MetricsSystem)
    app_ui.show()

    sys.exit(app.exec())