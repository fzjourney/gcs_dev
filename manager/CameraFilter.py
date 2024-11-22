import cv2

class CameraFilter:
    def apply_filter(self, frame):
        if self.current_filter == "normal":
            return frame
        elif self.current_filter == "bw":
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.adaptiveThreshold(gray_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            return cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        elif self.current_filter == "grayscale":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        elif self.current_filter == "invert":
            frame = cv2.bitwise_not(frame)
            return frame