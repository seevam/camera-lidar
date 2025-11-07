import cv2
import numpy as np

class LaneDetector:
    def __init__(self, config):
        self.threshold = config['threshold']
        self.roi_top = config['roi_top_percent']
        self.min_area = config['min_contour_area']
        self.previous_position = None
    
    def detect(self, frame):
        """
        Detect lane line in frame
        Returns: (line_position, confidence, processed_frame)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to detect black line
        _, binary = cv2.threshold(gray, self.threshold, 255, cv2.THRESH_BINARY_INV)
        
        # Extract region of interest (bottom portion)
        height, width = binary.shape
        roi_start = int(height * self.roi_top)
        roi = binary[roi_start:, :]
        
        # Find contours
        contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process for visualization
        processed = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        
        if contours:
            # Find largest contour (assumed to be line)
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)
            
            if area > self.min_area:
                # Calculate center of mass
                M = cv2.moments(largest)
                if M['m00'] > 0:
                    cx = int(M['m10'] / M['m00'])
                    
                    # Calculate confidence based on area
                    confidence = min(1.0, area / 10000)
                    
                    # Draw contour on processed image
                    cv2.drawContours(processed[roi_start:, :], [largest], -1, (0, 255, 0), 2)
                    
                    self.previous_position = cx
                    return cx, confidence, processed
        
        # No line detected - use previous position if available
        if self.previous_position:
            return self.previous_position, 0.0, processed
        
        # Default to center
        return width // 2, 0.0, processed
