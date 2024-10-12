from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QMessageBox, QGroupBox, QGridLayout, QSizePolicy
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
import cv2

# Simulated backend data updates with variables
pitch = 10
roll = 92
yaw = 24
battery = 90
temperature = 30
speed = 25
altitude = 2500
height = 15
flight_time = "00:02:21"

# Function to simulate button press
def on_button_click(action):
    msg = QMessageBox()
    msg.setText(f"{action} button pressed")
    msg.exec()

# Main application window
class DroneControlUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.cap = cv2.VideoCapture(0)  # Open the laptop camera
        self.current_filter = None
        
        # Timer for updating the video feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_feed)
        self.timer.start(30)  # Update every 30 ms

    def init_ui(self):
        self.setWindowTitle("Drone Control Interface")
        self.setGeometry(100, 100, 800, 500)
        
        # Set window to windowed fullscreen
        self.setWindowState(Qt.WindowMaximized)  # Fullscreen
        self.setWindowFlag(Qt.WindowStaysOnBottomHint, False)

        main_layout = QHBoxLayout(self)

        # Left side layout (Controls, Data)
        left_layout = QVBoxLayout()
        
        # Takeoff and Land buttons
        takeoff_button = QPushButton("Takeoff")
        takeoff_button.setStyleSheet("font-size: 20px; padding: 10px;")
        takeoff_button.clicked.connect(lambda: on_button_click("Takeoff"))

        land_button = QPushButton("Land")
        land_button.clicked.connect(lambda: on_button_click("Land"))
        land_button.setStyleSheet("font-size: 20px; padding: 10px;")

        left_layout.addWidget(takeoff_button)
        left_layout.addWidget(land_button)

        # Filter buttons
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
        normal_button.clicked.connect(lambda: self.set_filter("normal"))  # Reset to normal
        normal_button.setStyleSheet("font-size: 20px; padding: 10px;")

        filter_layout.addWidget(normal_button, 1, 0) 
        filter_layout.addWidget(bw_button, 1, 1)
        filter_layout.addWidget(grayscale_button, 2, 0)
        filter_layout.addWidget(invert_button, 2, 1)

        filter_group.setLayout(filter_layout)
        left_layout.addWidget(filter_group)

        # Metrics display (Temperature, Speed, etc.)
        metrics_group = QGroupBox("Metrics")
        metrics_group.setStyleSheet("font-size: 20px")
        metrics_layout = QVBoxLayout()

        temp_label = QLabel(f"Temperature: {temperature}°C")
        speed_label = QLabel(f"Speed: {speed} km/s")
        altitude_label = QLabel(f"Altitude: {altitude} m")
        height_label = QLabel(f"Height: {height} m")
        
        temp_label.setStyleSheet("font-size: 25px;")
        speed_label.setStyleSheet("font-size: 25px;")
        altitude_label.setStyleSheet("font-size: 25px;")
        height_label.setStyleSheet("font-size: 25px;")

        metrics_layout.addWidget(temp_label)
        metrics_layout.addWidget(speed_label)
        metrics_layout.addWidget(altitude_label)
        metrics_layout.addWidget(height_label)

        metrics_group.setLayout(metrics_layout)
        left_layout.addWidget(metrics_group)

        # Add left layout to main layout with stretch factor
        main_layout.addLayout(left_layout, 8) 

        # Right side layout (Video Stream, Data)
        right_layout = QVBoxLayout()

        # Placeholder for video stream
        self.video_label = QLabel("Video Stream")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: transparent; color: white; font-size: 18px;")  # Black background for video
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Make video label expandable
        right_layout.addWidget(self.video_label)

        # Display flight data like Pitch, Roll, Yaw
        flight_data_layout = QHBoxLayout()

        pitch_label = QLabel(f"Pitch: {pitch}")
        pitch_label.setAlignment(Qt.AlignCenter)

        roll_label = QLabel(f"Roll: {roll}")
        roll_label.setAlignment(Qt.AlignCenter)

        yaw_label = QLabel(f"Yaw: {yaw}")
        yaw_label.setAlignment(Qt.AlignCenter)

        battery_label = QLabel(f"Battery: {battery}%")
        battery_label.setAlignment(Qt.AlignCenter)
        
        pitch_label.setStyleSheet("font-size: 25px;")
        roll_label.setStyleSheet("font-size: 25px;")
        yaw_label.setStyleSheet("font-size: 25px;")
        battery_label.setStyleSheet("font-size: 25px;")

        flight_data_layout.addWidget(pitch_label)
        flight_data_layout.addWidget(roll_label)
        flight_data_layout.addWidget(yaw_label)
        flight_data_layout.addWidget(battery_label)

        right_layout.addLayout(flight_data_layout)

        # Display flight time
        flight_time_label = QLabel(f"Flight Time: {flight_time}")
        flight_time_label.setAlignment(Qt.AlignCenter)
        flight_time_label.setStyleSheet("font-size: 25px;")
        right_layout.addWidget(flight_time_label)

        # Add right layout to main layout with stretch factor
        main_layout.addLayout(right_layout, 14)  

    def set_filter(self, filter_type):
        """Set the current filter to be applied."""
        self.current_filter = filter_type

    def update_video_feed(self):
        """Capture video from the camera and apply filters."""
        ret, frame = self.cap.read()
        if not ret:
            return

        if self.current_filter == "bw":
            # Convert the frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  
            # Apply a binary threshold to create a black and white effect
            _, frame = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)  
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)  # Convert back to BGR for displaying
        elif self.current_filter == "grayscale":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Grayscale filter
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)  # Convert grayscale images to BGR for displaying
        elif self.current_filter == "invert":
            frame = cv2.bitwise_not(frame)  # Invert filter
        elif self.current_filter == "normal":
            # No filter applied, use the original frame
            pass

        # Resize the frame to fit the QLabel
        frame_height, frame_width, _ = frame.shape
        label_height = self.video_label.height()
        label_width = self.video_label.width()

        # Maintain aspect ratio
        if frame_width / frame_height > label_width / label_height:
            new_width = label_width
            new_height = int(label_width * frame_height / frame_width)
        else:
            new_height = label_height
            new_width = int(label_height * frame_width / frame_height)

        # Resize the frame
        frame = cv2.resize(frame, (new_width, new_height))

        # Convert the frame to QImage and display it
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img))


    def closeEvent(self, event):
        """Release the video capture when the window is closed."""
        self.cap.release()
        event.accept()

# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = DroneControlUI()
    window.show()
    app.exec()
