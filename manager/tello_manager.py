import socket
import threading
import cv2

class TelloManager:
    def __init__(self):
        self.host = ''
        self.port = 9000  
        self.address = ('192.168.10.1', 8889)
        self.state_address = ('', 8890)
        self.state_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.state_socket.bind(self.state_address)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.tello_response = None
        self.lock = threading.Lock()

    def send_msg(self, msg):
        """Send command to Tello."""
        self.socket.sendto(msg.encode('utf-8'), self.address)
        self.tello_response = self.receive_msg()
    
    def receive_msg(self):
        """Receive response from Tello."""
        try:
            response, _ = self.socket.recvfrom(1024)
            return response.decode('utf-8')
        except Exception as e:
            print(f"Error receiving message: {str(e)}")
            return None

    def init_sdk_mode(self):
        """Put Tello in SDK mode."""
        self.send_msg("command")

    def get_battery(self):
        """Get the battery percentage."""
        self.send_msg("battery?")
        return self.tello_response

    def receive_state(self):
        """Continuously receive state information."""
        while True:
            try:
                state, _ = self.state_socket.recvfrom(1024)
                print(f"State: {state.decode('utf-8')}")
            except Exception as e:
                print(f"Error receiving state: {str(e)}")
                break

    def start_video_stream(self):
        """Start video streaming."""
        self.send_msg("streamon")

    def stop_video_stream(self):
        """Stop video streaming."""
        self.send_msg("streamoff")

    def stop_drone_operations(self):
        """Stop all drone operations and clean up."""
        self.send_msg("land")
        self.stop_video_stream()
        self.state_socket.close()
        self.socket.close()
        
    def video_stream(self):
        """Capture video stream and apply OpenCV settings."""
        cap = cv2.VideoCapture('udp://0.0.0.0:11111')  # Tello sends video stream over UDP
        if not cap.isOpened():
            print("Error opening video stream")
            return

        # Configure Camera Settings
        cap.set(cv2.CAP_PROP_AUTO_WB, 1)  # Enable auto white balance
        cap.set(cv2.CAP_PROP_EXPOSURE, -1)  # Auto exposure

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process the frame (apply filters, show it, etc.)
            cv2.imshow("Tello Camera", frame)

            # Press 'q' to quit the video stream
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        
        

