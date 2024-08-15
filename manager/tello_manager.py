import socket
from threading import Thread
import cv2 as cv
import time


class TelloManager:
    def __init__(self):
        self.addr = ('192.168.10.1', 8889)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 9000))
        self.state = {}

    def send_msg(self, command):
        # Send action commands to the drone and receive responses
        self.sock.sendto(command.encode(), self.addr)
        data, _ = self.sock.recvfrom(1024)
        return data.decode()

    def receive_state(self):
        # Thread to receive state information from the drone
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
        
        retry_count = 0
        max_retries = 5
        timeout = 2  # seconds

        while not cap.isOpened() and retry_count < max_retries:
            print(f"Video stream not opened. Retrying... {retry_count + 1}/{max_retries}")
            time.sleep(timeout)  # Synchronous sleep from the `time` module
            cap.open('udp://@0.0.0.0:11111')
            retry_count += 1

        if not cap.isOpened():
            print("Failed to open video stream after multiple retries.")
            return  # Exit the video thread if the stream cannot be opened

        while True:
            ret, img = cap.read()
            if ret:
                img = cv.resize(img, (640, 480))
                cv.imshow('Flight', img)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv.destroyAllWindows()
    def init_sdk_mode(self):
        # Initiate SDK mode
        data = self.send_msg("command")
        if data == 'ok':
            print("Entering SDK Mode")
            return True
        else:
            print("Error initiating SDK Mode")
            return False

    def start_video_stream(self):
        # Start the video stream
        data = self.send_msg('streamon')
        if data == 'ok':
            thread2 = Thread(target=self.video_stream)
            thread2.start()
            return True
        else:
            print("Error starting video stream")
            return False

    def stop_drone_operations(self):
        # Stop all operations and land the drone
        data = self.send_msg('land')
        print('Response:', data)
        self.sock.close()
