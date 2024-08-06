import socket
from threading import Thread
import cv2 as cv

# Set up URL and socket
addr = ('192.168.10.1', 8889)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 9000))

# Set up variables to store command and drone state
state = {}

def send_msg(command):
    # Function to send action commands to the drone and receive responses
    sock.sendto(command.encode(), addr)
    data, _ = sock.recvfrom(1024)
    return data.decode()

def receive_state():
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
                state[item[0]] = float(item[1])
    serv_sock.close()

def video_stream():
    # Function to receive video stream from the drone
    cap = cv.VideoCapture('udp://@0.0.0.0:11111')
    if not cap.isOpened():
        cap.open('udp://@0.0.0.0:11111')
    while True:
        ret, img = cap.read()
        if ret:
            img = cv.resize(img, (640, 480))
            cv.imshow('Flight', img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv.destroyAllWindows()

def init_sdk_mode():
    data = send_msg("command")  # Send command to initiate SDK mode
    if data == 'ok':  # Only if SDK mode is successfully initiated
        print("Entering SDK Mode")
        return True
    else:
        print("Error initiating SDK Mode")
        return False

def start_video_stream():
    data = send_msg('streamon')  # Send command to initiate video streaming mode
    if data == 'ok':  # Only if streaming mode is successfully initiated
        thread2 = Thread(target=video_stream)  # Start thread to receive video stream
        thread2.start()
        return True
    else:
        print("Error starting video stream")
        return False

def stop_drone_operations():
    data = send_msg('land')
    print('Response:', data)
    sock.close()

# Source: controller_manager.py
