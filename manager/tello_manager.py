import socket
import threading
import cv2
import queue

class TelloManager:
    def __init__(self):
        self.host = ''
        self.port = 9000  
        self.address = ('192.168.10.1', 8889)
        self.state_address = ('', 8890)
        
        # Initialize sockets
        self.state_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.state_socket.bind(self.state_address)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        
        self.tello_response = None
        self.lock = threading.Lock()
        
        # Initialize state dictionary
        self.state = {
            'battery': 'Unknown',
            'temperature': 'Unknown',
            'speed': 'Unknown',
            'altitude': 'Unknown',
            'pitch': 'Unknown',
            'roll': 'Unknown',
            'yaw': 'Unknown',
            'tof': 'Unknown',
            'baro': 'Unknown',
            'flight_time': 'Unknown'
        }

        # Start the state update thread
        self.state_thread = threading.Thread(target=self.receive_state)
        self.state_thread.daemon = True
        self.state_thread.start()

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
        return self.state.get('battery', 'Unknown')

    def get_temperature(self):
        """Get the temperature (average of low and high)."""        
        return self.state.get('temperature', 'Unknown')

    def get_speed(self):
        """Get the speed."""        
        return self.state.get('speed', 'Unknown')

    def get_altitude(self):
        """Get the altitude."""        
        return self.state.get('altitude', 'Unknown')

    def receive_state(self):
        """Continuously receive state information and update telemetry."""        
        while True:
            try:
                state_data, _ = self.state_socket.recvfrom(1024)
                state_str = state_data.decode('utf-8')
                print(f"Received state data: {state_str}")  # Debug print
                self.parse_state_data(state_str)
            except Exception as e:
                print(f"Error receiving state: {str(e)}")
                break


    def parse_state_data(self, state_str):
        """Parse state data and update the state dictionary."""
        try:
            data_dict = dict(item.split(':') for item in state_str.split(';') if item)
            print(f"Parsed state data: {data_dict}")  # Debug print

            with self.lock:
                self.state['battery'] = data_dict.get('bat', 'Unknown')
                
                templ = float(data_dict.get('templ', 0))
                temph = float(data_dict.get('temph', 0))
                self.state['temperature'] = f"{(templ + temph) / 2:.1f}°C"
                
                speed_x = float(data_dict.get('vgx', 0))
                speed_y = float(data_dict.get('vgy', 0))
                speed_z = float(data_dict.get('vgz', 0))
                self.state['speed'] = f"{(abs(speed_x) + abs(speed_y) + abs(speed_z)) / 3:.1f} m/s"
                
                self.state['altitude'] = data_dict.get('h', 'Unknown')
                self.state['pitch'] = data_dict.get('pitch', 'Unknown')
                self.state['roll'] = data_dict.get('roll', 'Unknown')
                self.state['yaw'] = data_dict.get('yaw', 'Unknown')
                self.state['tof'] = data_dict.get('tof', 'Unknown')
                self.state['baro'] = data_dict.get('baro', 'Unknown')
                self.state['flight_time'] = data_dict.get('time', 'Unknown')
        except Exception as e:
            print(f"Error parsing state data: {str(e)}")

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
        """Capture video stream using a buffer."""        
        cap = cv2.VideoCapture('udp://0.0.0.0:11111')  
        if not cap.isOpened():
            print("Error opening video stream")
            return

        cap.set(cv2.CAP_PROP_AUTO_WB, 1) 
        cap.set(cv2.CAP_PROP_EXPOSURE, -1) 

        buffer_size = 10 
        frame_buffer = queue.Queue(maxsize=buffer_size)

        def capture_frames():
            """Thread function to capture frames and store them in a buffer."""            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_buffer.full():
                    frame_buffer.get()

                frame_buffer.put(frame)

        capture_thread = threading.Thread(target=capture_frames)
        capture_thread.daemon = True
        capture_thread.start()

        while True:
            if not frame_buffer.empty():
                frame = frame_buffer.get()

                cv2.imshow("Tello Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
