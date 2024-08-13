import sys
import os
from threading import Thread

# Add the 'manager' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manager'))

from tello_manager import init_sdk_mode, start_video_stream, stop_drone_operations, send_msg, state, receive_state
from controller_manager import JoystickController  # Import the joystick controller

if __name__ == "__main__":
    print("Initiating Connection to Drone")
    
    if init_sdk_mode():  # Only proceed if SDK mode is successfully initiated
        thread = Thread(target=receive_state)  # Start thread to receive telemetry data
        thread.start()
        
        # Initialize and start the JoystickController in a separate thread
        joystick_controller = JoystickController()
        joystick_thread = Thread(target=joystick_controller.run)
        joystick_thread.start()
        
        if start_video_stream():  # Only proceed if video streaming mode is successfully initiated
            while True:  # Main loop to control the drone
                command = str(input('Enter command: ')).strip()
                if command in ['takeoff', 'land', 'streamoff']:
                    data = send_msg(command)
                    print('Response:', data)
                    if command == 'takeoff':
                        print('Taking off...')
                    elif command == 'land':
                        print('Landing...')
                    elif command == 'streamoff':
                        print('Video stream turned off.')
                elif command == 'exit':
                    break
                else:
                    print("Unknown command")
            
            # If main loop is exited, stop all drone operations
            stop_drone_operations()

            # Optionally join joystick thread before exiting
            joystick_thread.join()

        # Optionally join receive_state thread before exiting
        thread.join()
