import socket
from threading import Thread
import av
import cv2 as cv
import time

class TelloManager:
    def __init__(self):
        self.addr = ('192.168.10.1', 8889)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 9000))
        self.state = {}

    def send_msg(self, command):
        try:
            self.sock.sendto(command.encode(), self.addr)
            data, _ = self.sock.recvfrom(1024)
            return data.decode()
        except socket.error as e:
            print(f"Error sending command {command}: {e}")
            return ""

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

    def video_stream(self, display_manager):
        try:
            container = av.open('udp://@0.0.0.0:11111')
            stream = container.streams.video[0]
            stream.thread_type = 'AUTO'

            for frame in container.decode(video=0):
                img = frame.to_ndarray(format='bgr24')
                img = cv.resize(img, (640, 480))
                
                # Convert the image to RGB and pass it to the display manager
                img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                display_manager.update_frame(img_rgb)

                if cv.waitKey(1) & 0xFF == ord('q'):
                    break

        except av.AVError as e:
            print(f"Error occurred while capturing video stream: {e}")

        cv.destroyAllWindows()

    def init_sdk_mode(self):
        data = self.send_msg("command")
        if data == 'ok':
            print("Entering SDK Mode")
            return True
        else:
            print("Error initiating SDK Mode")
            return False

    def start_video_stream(self, display_manager):
        data = self.send_msg('streamon')
        if data == 'ok':
            thread2 = Thread(target=self.video_stream, args=(display_manager,))
            thread2.start()
            return True
        else:
            print("Error starting video stream")
            return False

    def stop_drone_operations(self):
        self.send_msg('land')
        self.sock.close()
