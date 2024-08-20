import socket
from threading import Thread
import av
import cv2 as cv

class TelloManager:
    def __init__(self):
        self.addr = ('192.168.10.1', 8889)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 9000))
        self.state = {}

    def send_msg(self, command):
        try:
            self.sock.sendto(command.encode(), self.addr)
        except socket.error as e:
            print(f"Error sending command {command}: {e}")

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
        try:
            container = av.open('udp://@0.0.0.0:11111')
            stream = container.streams.video[0]
            stream.thread_type = 'AUTO'

            for frame in container.decode(video=0):
                img = frame.to_ndarray(format='bgr24')
                img = cv.resize(img, (640, 480))
                cv.imshow('Flight', img)

                if cv.waitKey(1) & 0xFF == ord('q'):
                    break

        except av.AVError as e:
            print(f"Error occurred while capturing video stream: {e}")

        cv.destroyAllWindows()

    def init_sdk_mode(self):
        self.send_msg("command")

    def start_video_stream(self):
        self.send_msg('streamon')

    def stop_drone_operations(self):
        self.send_msg('land')
        self.sock.close()
