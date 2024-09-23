import socket
import av
import cv2 as cv
from threading import Thread

class TelloManager:
    def __init__(self):
        self.addr = ('192.168.10.1', 8889) 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 9000)) 
        self.state = {"speed": 0, "battery": 0, "time": 0, "wifi": 0} 

    def send_msg(self, command):
        """Send a command to the Tello drone."""
        try:
            self.sock.sendto(command.encode(), self.addr)
        except socket.error as e:
            print(f"Error sending command {command}: {e}")

    def receive_state(self):
        """Receive telemetry data from the Tello drone."""
        serv_addr = ('', 8890)  
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serv_sock.bind(serv_addr)
        while True:
            raw_data, _ = serv_sock.recvfrom(1024)
            raw_data = raw_data.decode()
            data = raw_data.split(';')
            for i in data:
                if ':' in i:
                    key, value = i.split(':')
                    if key == "vgx":  
                        self.state["speed"] = float(value)
                    elif key == "bat": 
                        self.state["battery"] = float(value)
        serv_sock.close()

    def video_stream(self):
        """Receive and display the video stream from the Tello drone."""
        try:
            container = av.open('udp://@0.0.0.0:11111')
            stream = container.streams.video[0]
            stream.thread_type = 'AUTO'

            for frame in container.decode(video=0):
                img = frame.to_ndarray(format='bgr24') 
                img = cv.resize(img, (640, 480))  

                self.overlay_info(img)

                cv.imshow('Tello Video Stream', img)

                if cv.waitKey(1) & 0xFF == ord('q'):  
                    break

        except av.AVError as e:
            print(f"Error capturing video stream: {e}")

        cv.destroyAllWindows()

    def overlay_info(self, img):
        """Overlay speed, battery, time, and wifi on the video frame."""
        font = cv.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        color = (255, 255, 255) 
        thickness = 2

        speed_text = f"Speed: {self.state['speed']} m/s"
        battery_text = f"Battery: {self.state['battery']}%"

        cv.putText(img, speed_text, (10, 30), font, font_scale, color, thickness)
        cv.putText(img, battery_text, (10, 60), font, font_scale, color, thickness)

    def init_sdk_mode(self):
        """Initialize SDK mode on the Tello drone."""
        self.send_msg("command")

    def start_video_stream(self):
        """Send the command to start the video stream."""
        self.send_msg('streamon')

    def stop_drone_operations(self):
        """Send the command to stop any drone operations (optional)."""
        self.sock.close()  
