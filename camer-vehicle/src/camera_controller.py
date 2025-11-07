import cv2
import numpy as np

class CameraController:
    def __init__(self, config):
        self.camera_id = config['device_id']
        self.width = config['width']
        self.height = config['height']
        self.fps = config['fps']
        
        # Initialize camera
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        if not self.cap.isOpened():
            raise Exception("Failed to open camera")
        
        print(f"[INFO] Camera initialized: {self.width}x{self.height} @ {self.fps}fps")
    
    def get_frame(self):
        """Capture single frame"""
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def show_debug(self, frame, line_position, confidence):
        """Display debug visualization"""
        # Draw line position
        if confidence > 0:
            cv2.line(frame, (line_position, 0), (line_position, frame.shape[0]), (0, 255, 0), 2)
        
        # Draw center line
        center = frame.shape[1] // 2
        cv2.line(frame, (center, 0), (center, frame.shape[0]), (255, 0, 0), 1)
        
        # Add text info
        cv2.putText(frame, f"Confidence: {confidence:.2f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Camera View', frame)
    
    def check_quit(self):
        """Check for quit key"""
        return cv2.waitKey(1) & 0xFF == ord('q')
    
    def cleanup(self):
        """Release resources"""
        self.cap.release()
        cv2.destroyAllWindows()
